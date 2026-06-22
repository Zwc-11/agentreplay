<div align="center">

# AgentReplay

### A browser workflow flight recorder for AI agents

**Record a real web workflow once → compile it into a replayable simulator → run an agent against it → see exactly where the agent diverged.**

[Architecture](docs/architecture.md) · [Event Schema](docs/event-schema.md) · [Workflow Graph](docs/workflow-graph.md) · [Evaluation](docs/evaluation.md) · [Deployment](docs/deployment.md) · [DeepSeek](docs/deepseek.md) · [Roadmap](PLAN.md)

</div>

---

## What is AgentReplay?

AgentReplay is an open-source **browser workflow simulator** and failure-analysis platform. You record a human performing a real browser workflow once — clicks, typed input, navigations, network calls, DOM snapshots — and AgentReplay turns that recording into a structured **workflow graph** and a runnable **Playwright replay environment**.

You then run a browser agent against the same task and AgentReplay performs a **human-vs-agent path comparison**: it overlays the two paths on an interactive graph, pinpoints the **first divergence step**, and explains the failure with step-level metrics, a timeline of DOM/network/console state, and an AI-generated root-cause summary.

Think **Sentry + Playwright Trace Viewer + React Flow + an agent evaluation layer**, focused specifically on the browser-automation lane.

> The product in one line: **Record workflow → compile graph → run agent → compare paths → explain failure → export Playwright test.**

## Why browser agents fail

Browser agents fail in ways that are hard to see from a transcript alone:

- They click the **wrong element** (an ad, a lookalike button, a stale selector).
- They act on a **stale DOM state** before a route finishes loading.
- A **network failure** (e.g. a `500` on submit) disables a control, and the agent retries the wrong action instead of recovering.
- They **diverge silently** several steps before the visible failure, so the real root cause is buried.

A flat log of actions doesn't surface any of this. AgentReplay reconstructs the **browser state at every step** and renders the divergence as a graph, so the root cause is obvious in about three seconds.

## Architecture

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

The backend uses **event sourcing** (every browser event is stored append-only and replayable) and **hexagonal architecture** (domain logic in `core/`, infrastructure behind `adapters/`), so the compiler and evaluator can be tested without the web server or database. See [docs/architecture.md](docs/architecture.md) for the full design and rationale.

**Stack:** React + TypeScript + Tailwind + React Flow + Framer Motion (web) · FastAPI + Playwright (api) · PostgreSQL + Redis · Docker Compose. LLMs are used only for human-readable summaries, never for core logic.

## Repository layout

```
agentreplay/
  apps/
    web/                 React dashboard (graph, replay, timeline, metrics)
    api/                 FastAPI: ingestion, compiler, agent runner, evaluator
  packages/
    recorder-sdk/        Browser recorder → BrowserEvent stream
    playwright-generator/ Workflow graph → runnable Playwright test
    graph-core/          events → states → workflow graph (framework-free)
    eval-core/           divergence detection + metrics (framework-free)
    shared-types/        BrowserEvent, BrowserCommand, WorkflowGraph types
  infra/                 docker-compose, postgres, redis
  examples/              demo-shop, demo-crm, demo-calendar
  docs/                  architecture, event-schema, workflow-graph, evaluation
  tests/                 e2e (Playwright) + integration
```

## Quick start

```bash
git clone https://github.com/Zwc-11/agentreplay.git
cd agentreplay
cp .env.example .env
docker compose -f infra/docker-compose.yml up
```

Then open the dashboard:

```
http://localhost:3000
```

The dashboard ships with **demo mode** (seeded workflows) so the system is explorable without recording anything first. See [docs/local-setup.md](docs/local-setup.md) for development without Docker.

To test real recording ingestion without Docker:

```bash
# terminal 1
cd apps/api
pip install -e ".[dev]"
python -m uvicorn app.main:app --reload --port 8000

# terminal 2, from the repo root
npm install
npm run dev -w @agentreplay/web
```

Open `http://localhost:3000`, click **Import Recording**, and choose `examples/demo-calendar/recordings/event.json`. See [docs/real-recordings.md](docs/real-recordings.md) for the SDK snippet, API import endpoint, and verification commands.

## Demo workflow

1. Record a checkout flow on the bundled `demo-shop` app with the recorder SDK.
2. AgentReplay compiles the event stream into a workflow graph: `Login → Search → Add to cart → Checkout → Success`.
3. Run an agent against the same task (start with the built-in `ScriptedAgentDriver` and `RandomAgentDriver` — no API keys required).
4. The dashboard overlays the human and agent paths; the divergence node pulses red where the agent went wrong.
5. Export a runnable Playwright test, or open a pre-filled GitHub issue from the failure summary.

## Event schema

Recordings are stored as a stream of structured `BrowserEvent`s — not just screenshots:

```ts
type BrowserEvent = {
  sessionId: string;
  stepIndex: number;
  timestamp: string;
  eventType: "click" | "input" | "navigation" | "network" | "assertion" | "error";
  url: string;
  target?: {
    selector: string;
    role?: string;
    label?: string;
    text?: string;
    bbox?: { x: number; y: number; width: number; height: number };
  };
  network?: { method: string; path: string; status: number; latencyMs: number };
  screenshotKey?: string;
  domSnapshotKey?: string;
};
```

Full schema and storage model: [docs/event-schema.md](docs/event-schema.md).

## Generated Playwright tests

Every recorded workflow compiles to a runnable [Playwright](https://playwright.dev) test:

```ts
test("checkout workflow", async ({ page }) => {
  await page.goto("https://demo-store.local");
  await page.getByRole("textbox", { name: "Email" }).fill("demo@test.com");
  await page.getByRole("button", { name: "Continue" }).click();
  await expect(page.getByText("Dashboard")).toBeVisible();
});
```

## Evaluation metrics

AgentReplay reports measurable, step-level outcomes for every agent run:

| Metric | What it tells you |
| --- | --- |
| Task success rate | Did the agent reach the goal state? |
| Step accuracy | Fraction of steps matching the human path |
| First divergence step | Where the agent first went off-route |
| Wrong-click count | Off-path actions taken |
| Agent recovery rate | How often it recovered after diverging |
| Network-caused failure rate | Failures rooted in a bad network response |
| Replay reconstruction success | Could the workflow be fully rebuilt? |
| Generated test pass rate | Do the exported Playwright tests pass? |

Definitions and formulas: [docs/evaluation.md](docs/evaluation.md).

## Roadmap

A six-week MVP plan (foundation → replay → graph compiler → agent comparison → AI summaries → enterprise polish) lives in [PLAN.md](PLAN.md).

## License

[MIT](LICENSE)
