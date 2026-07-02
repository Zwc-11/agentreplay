# AgentReplay — Build Plan

> **Product center:** Record workflow → compile graph → run agent → compare paths → explain failure → export Playwright test.
>
> **Positioning:** AgentReplay is a **browser workflow simulator**. It owns the browser-simulation lane — DOM snapshots, Playwright replay, human-vs-agent path graphs. It is deliberately *not* framed as an "agent reliability harness," and avoids the coding-agent / pass@k / patch-ranking / CI-trace language that belongs to other projects.

---

## 1. Vision

AgentReplay should feel like **Sentry + Playwright Trace Viewer + React Flow + an agent eval platform**. Existing tools can inspect a single recorded trace; AgentReplay's unique layer is turning browser traces into **structured workflow graphs** and then comparing **human vs. agent** behavior on top of them. That comparison is the enterprise idea.

## 2. The five major features

| # | Feature | What it does | Lives in |
| - | --- | --- | --- |
| A | **Recorder SDK** | Captures DOM events, clicks, input, navigations, screenshots, network req/res, console logs, a11y snapshots, and element metadata (role/label/text/selector/bbox) as structured `BrowserEvent`s. | `packages/recorder-sdk` |
| B | **Workflow compiler** | Raw events → normalized events → browser states → edges/actions → workflow graph. Each node is a browser state; each edge is an action. | `packages/graph-core`, `apps/api/app/core/graph` |
| C | **Playwright generator** | Emits a runnable Playwright test from the recorded workflow. | `packages/playwright-generator` |
| D | **Agent runner** | Pluggable drivers behind one interface (strategy pattern): Scripted, Random, Playwright, LLM. Cheap/fake agents first. | `apps/api/app/adapters/playwright`, `core/evaluation` |
| E | **Eval dashboard** | React Flow graph comparing human path, agent path, expected vs. actual transitions, network failures, divergence point, failure reason. | `apps/web` |

## 3. Architecture decisions

- **Event sourcing** — store every browser event append-only (`SessionEventCreated`, `NetworkRequestCaptured`, `DomSnapshotCaptured`, `AgentActionExecuted`, `DivergenceDetected`, `EvaluationCompleted`). Replayable, auditable, debuggable. This is *browser-state* replay, distinct from coding-agent trace replay.
- **Hexagonal architecture** — domain logic in `core/` (workflow, evaluation, graph, replay) is independent of `adapters/` (postgres, playwright, redis, llm, storage). The compiler and evaluator are testable without the web server or DB.
- **Strategy pattern** — agent drivers share `AgentDriver`; `ScriptedAgentDriver | RandomAgentDriver | PlaywrightAgentDriver | LLMAgentDriver`.
- **Pipeline pattern** — compilation = normalize → group into states → infer actions → build graph → compute metrics → generate replay.
- **Repository pattern** — `WorkflowRepository` keeps DB code out of business logic.
- **Command pattern** — browser actions are typed commands (`click | fill | goto | assertVisible`), which makes Playwright generation clean.

## 4. Tech stack

| Layer | Choice |
| --- | --- |
| Frontend | React, TypeScript, Tailwind, React Flow, Framer Motion |
| Backend | Python FastAPI (Go is an option later for stronger systems signal) |
| Browser automation | Playwright (Chromium/Firefox/WebKit) |
| Database | PostgreSQL (relational metadata + JSONB event payloads) |
| Queue | Redis + worker |
| Object storage | Local filesystem first, S3/R2 later |
| AI | OpenAI/local LLM for **summaries only**, never core logic |
| Deploy | Docker Compose; Vercel/Render/Fly.io; optional Cloudflare Pages |

## 5. Six-week roadmap

### Week 1 — Foundation
Monorepo, frontend shell, backend API, PostgreSQL schema, Playwright recorder for one demo site, event ingestion endpoint.
**Deliverable:** record a login workflow and store events in Postgres.

### Week 2 — Replay engine
Event timeline, screenshot storage, Playwright test generation, simple replay viewer.
**Deliverable:** a recorded workflow can be replayed and exported as a Playwright test.

### Week 3 — Graph compiler
Event-to-state compiler, workflow graph nodes/edges, React Flow visualization, human-path graph.
**Deliverable:** a recorded workflow becomes an interactive graph.

### Week 4 — Agent comparison
Scripted agent runner, random/failure agent runner, human-vs-agent graph comparison, divergence detection, step-level metrics.
**Deliverable:** run an agent, compare its path, identify the first divergence.

### Week 5 — AI summaries & polish
AI-generated failure summary, generated GitHub issue, landing page, demo mode, Docker Compose, README, architecture diagram.
**Deliverable:** a recruiter can open the deployed demo and understand it in 30 seconds.

### Week 6 — Enterprise polish
Auth / project API keys, rate limits, seed dataset of workflows, benchmark page, docs site, CI tests, deployment pipeline.
**Deliverable:** looks like a real open-source product, not a class project.

## 6. MVP scope (build this first — don't over-build)

1. One demo app (fake checkout or fake CRM).
2. Record one human workflow.
3. Store events in Postgres.
4. Generate the workflow graph.
5. Show the React Flow graph.
6. Run a simple scripted/failing agent.
7. Compare paths and show divergence.
8. Generate a Playwright test.
9. Add an AI failure summary.

That is already enough for a compelling demo.

## 7. Graph modes (the part that makes people stop)

The graph must answer one question — *where did the agent go wrong?* — in ~3 seconds.

1. **Human path** — the correct route (`Login → Search → Add Item → Checkout → Success`).
2. **Human vs. agent** — both paths overlaid; the divergence node pulses red. The main WOW demo.
3. **Browser-state graph** — each node is a state snapshot; clicking shows screenshot, URL, DOM summary, available actions, network calls, console logs.
4. **Network causality** — `Click Submit → POST /checkout → 500 → disabled button → repeated wrong clicks → failure`.

## 8. Metrics to design for

Task success rate · step accuracy · wrong-click count · first divergence step · replay reconstruction success · agent recovery rate · network-caused failure rate · average replay latency · generated Playwright test pass rate.

> Only publish real numbers after measuring them. The schema and pipeline are designed so these are computable from day one. See [docs/evaluation.md](docs/evaluation.md).

## 9. Database tables

`users · projects · api_keys · sessions · events · snapshots · workflow_graphs · agent_runs · agent_actions · evaluation_metrics · failure_summaries`. Full DDL in [docs/architecture.md](docs/architecture.md).

## 10. Testing & CI

- **Backend:** event validation, graph compiler, divergence detector, metric calculation, Playwright generator.
- **Frontend:** graph rendering, timeline filtering, replay state changes, metrics panel.
- **E2E:** AgentReplay tests itself with Playwright — record → compile → run agent → detect divergence → show summary.
- **CI (GitHub Actions):** lint · typecheck · backend tests · frontend tests · Playwright e2e · Docker build.

## 11. Demo video (90 seconds)

Checkout workflow recorded → turned into a graph → run an agent → it diverges at step 5 on the wrong checkout button → graph highlights divergence → timeline shows DOM/screenshot/network → AgentReplay emits a failure summary + Playwright test.

## 12. Resume outcome (the reason this exists)

> Built an **open-source** browser workflow simulator that captures DOM events, screenshots, and network calls, then stores and replays web flows as **Playwright** environments.
>
> Built a **React Flow** dashboard for human-vs-agent path comparison, surfacing divergence points, step metrics, timeline replay, and AI failure summaries.

Upgrade with real numbers once measured (e.g. "captured 40+ workflows across demo apps", "detected first divergence with N% agreement vs. manual labels").

## 13. Vocabulary

**Use:** browser workflow simulator · browser-state graph · human-vs-agent path comparison · Playwright replay environment · workflow reconstruction.
**Avoid:** agent reliability harness · pass@k · coding-agent eval · patch ranking · CI trace replay.
