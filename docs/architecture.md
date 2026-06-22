# Architecture

This document describes how AgentReplay is structured and *why*. The guiding goal is that the **domain logic** — compiling events into a workflow graph, detecting divergence, computing metrics — is independent of any framework, database, or browser. Infrastructure plugs in behind interfaces.

## System overview

```
┌──────────────────────────────┐
│ Demo Website / User Browser  │
└──────────────┬───────────────┘
               ▼
┌──────────────────────────────┐
│ Recorder SDK / Playwright    │  captures events + DOM/a11y snapshots
└──────────────┬───────────────┘
               ▼
┌──────────────────────────────┐
│ Ingestion API                │  auth, validation, batching
└──────────────┬───────────────┘
               ▼
┌──────────────────────────────┐
│ Event Store                  │  PostgreSQL (JSONB) + object storage
└──────────────┬───────────────┘
               ▼
┌──────────────────────────────┐
│ Workflow Compiler Worker     │  events → states → graph
└──────────────┬───────────────┘
               ▼
┌──────────────────────────────┐
│ Agent Runner + Evaluator     │  Playwright run + metrics
└──────────────┬───────────────┘
               ▼
┌──────────────────────────────┐
│ React Dashboard              │  replay, graph, metrics, AI summary
└──────────────────────────────┘
```

## Design patterns

### Event sourcing
The system of record is an **append-only event log**, not the final workflow. Domain events include:

- `SessionEventCreated`
- `NetworkRequestCaptured`
- `DomSnapshotCaptured`
- `AgentActionExecuted`
- `DivergenceDetected`
- `EvaluationCompleted`

Any workflow graph, replay, or metric is a *projection* derived from the log. This makes the platform replayable, auditable, and easy to debug — and it is specifically **browser-state replay**, distinct from coding-agent trace replay.

### Hexagonal (ports & adapters)
```
apps/api/app/
  core/                 # framework-free domain logic
    workflow/           # normalize → states → actions → graph (pipeline)
    evaluation/         # divergence detection + metric calculation
    graph/              # graph model + projections
    replay/             # rebuild browser state at step N
  adapters/             # infrastructure implementations of core ports
    postgres/           # repositories
    playwright/         # browser driving + test execution
    redis/              # queue / worker
    llm/                # summary generation
    storage/            # screenshots & DOM snapshots (fs → S3/R2)
  routes/               # FastAPI HTTP layer
  schemas/              # pydantic request/response models
  services/             # application orchestration
  workers/              # background compiler + evaluator jobs
  repositories/         # repository interfaces (ports)
```
The dependency rule points inward: `core/` knows nothing about FastAPI, Postgres, or Playwright. This is what lets the compiler and evaluator be unit-tested with plain in-memory fakes.

### Strategy pattern — agent drivers
All agents implement one interface so they are interchangeable:

```ts
interface AgentDriver {
  name: string;
  run(task: WorkflowTask): Promise<AgentRunResult>;
}
```

```
AgentDriver
  ├── ScriptedAgentDriver     # replays recorded steps exactly (baseline)
  ├── RandomAgentDriver       # intentionally makes wrong clicks (failure testing)
  ├── PlaywrightAgentDriver   # scripted Playwright execution
  └── LLMAgentDriver          # a model chooses the next browser action
```
The first version depends only on the cheap/fake drivers, so the whole pipeline works before any real agent is wired in.

### Pipeline pattern — workflow compilation
```
normalize events → group into states → infer actions → build graph → compute metrics → generate replay
```
Each stage is a pure function from one representation to the next, which makes the compiler trivial to test stage-by-stage.

### Repository pattern — storage
```python
class WorkflowRepository:
    def save_event(self, event: BrowserEvent) -> None: ...
    def load_session(self, session_id: str) -> list[BrowserEvent]: ...
    def save_graph(self, graph: WorkflowGraph) -> None: ...
```
Business logic depends on the interface; the Postgres implementation lives in `adapters/postgres`.

### Command pattern — browser actions
```ts
type BrowserCommand =
  | { type: "click"; selector: string }
  | { type: "fill"; selector: string; value: string }
  | { type: "goto"; url: string }
  | { type: "assertVisible"; selector: string };
```
A workflow edge carries a `BrowserCommand`, which maps cleanly onto both Playwright generation and agent execution.

## Data model

PostgreSQL stores relational metadata alongside JSONB payloads. Tables:

`users · projects · api_keys · sessions · events · snapshots · workflow_graphs · agent_runs · agent_actions · evaluation_metrics · failure_summaries`

Key tables:

```sql
CREATE TABLE events (
  id          uuid PRIMARY KEY,
  session_id  uuid NOT NULL,
  step_index  int  NOT NULL,
  event_type  text NOT NULL,
  timestamp   timestamptz NOT NULL,
  url         text,
  target      jsonb,
  network     jsonb,
  payload     jsonb
);

CREATE TABLE workflow_graphs (
  id          uuid PRIMARY KEY,
  session_id  uuid NOT NULL,
  nodes       jsonb NOT NULL,
  edges       jsonb NOT NULL,
  created_at  timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE agent_runs (
  id           uuid PRIMARY KEY,
  workflow_id  uuid NOT NULL,
  driver_name  text NOT NULL,
  status       text NOT NULL,
  success      boolean,
  started_at   timestamptz,
  completed_at timestamptz
);

CREATE TABLE evaluation_metrics (
  id                uuid PRIMARY KEY,
  agent_run_id      uuid NOT NULL,
  task_success      boolean,
  step_accuracy     numeric,
  wrong_click_count int,
  divergence_step   int,
  replay_latency_ms int
);
```

JSONB is used for `target`, `network`, and `payload` so the event schema can evolve without migrations, while still being queryable (and indexable) where needed.

## Object storage

Screenshots and DOM/accessibility snapshots are large and binary, so they are stored in object storage (local filesystem in dev, S3/R2 later) and referenced from events by `screenshotKey` / `domSnapshotKey`. The `storage` adapter hides which backend is in use.

## Request lifecycle (record → explain)

1. **Record** — the recorder SDK batches `BrowserEvent`s and POSTs them to the ingestion API.
2. **Ingest** — the API authenticates the project API key, validates each event, and appends it to the log.
3. **Compile** — a worker projects the event stream into a `WorkflowGraph` (states + action edges).
4. **Run** — the agent runner executes a driver against the task in a Playwright environment, producing an agent action stream.
5. **Evaluate** — the evaluator aligns the agent path against the human path, finds the first divergence, and computes metrics.
6. **Explain** — the LLM adapter generates a human-readable failure summary; the dashboard renders the graph, timeline, and metrics.

See [event-schema.md](event-schema.md), [workflow-graph.md](workflow-graph.md), and [evaluation.md](evaluation.md) for each stage in detail.
