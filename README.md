<div align="center">

# AgentReplay

### Browser workflow replay and failure analysis for agent testing

**Record a real web workflow once -> compile it into a replayable simulator -> run an agent against it -> see exactly where it diverged.**

[![CI](https://github.com/Zwc-11/agentreplay/actions/workflows/ci.yml/badge.svg)](https://github.com/Zwc-11/agentreplay/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![PRs welcome](https://img.shields.io/badge/PRs-welcome-blue.svg)](CONTRIBUTING.md)
![Python](https://img.shields.io/badge/python-3.11%2B-3776ab)
![Node](https://img.shields.io/badge/node-20%2B-3c873a)

[Architecture](docs/architecture.md) | [Event Schema](docs/event-schema.md) | [Workflow Graph](docs/workflow-graph.md) | [Evaluation](docs/evaluation.md) | [Deployment](docs/deployment.md) | [DeepSeek](docs/deepseek.md) | [Roadmap](PLAN.md)

</div>

---

![AgentReplay dashboard showing a real calendar workflow replay](artifacts/agentreplay-calendar-real-recording.png)

## Try It In 60 Seconds

The dashboard works without a backend by loading bundled demo data and falling back to demo mode automatically.

```bash
npm install
npm run dev -w @agentreplay/web
```

Open:

```text
http://localhost:3000
```

Prefer the terminal? Run the whole pipeline:

```bash
cd apps/api
pip install -e ".[dev]"
python -m app.scripts.demo
```

Everything wired together:

```bash
docker compose -f infra/docker-compose.yml up
```

Run `make help` to see common development commands.

## What Is AgentReplay?

AgentReplay is an open-source browser workflow simulator and failure-analysis platform. It records a human performing a real browser workflow, including clicks, typed input, navigations, network calls, and DOM snapshots, then turns that recording into a structured workflow graph and runnable Playwright replay.

You can run a browser agent against the same task and compare the human path to the agent path. The dashboard shows the first divergence step, step-level metrics, timeline evidence, network state, root-cause summary, and an exportable Playwright test.

The product loop is:

```text
Record workflow -> compile graph -> run agent -> compare paths -> explain failure -> export Playwright test
```

## Why Browser Agents Fail

Browser agents fail in ways that are hard to diagnose from a transcript alone:

- They click the wrong element, such as an ad, lookalike button, or stale selector.
- They act on stale DOM state before a route finishes loading.
- A network failure disables the intended control, then the agent retries the wrong action.
- They diverge silently several steps before the visible failure.

AgentReplay reconstructs the browser state at every step and renders the divergence as a graph so the root cause is clear quickly.

## Architecture

```text
Demo Website / User Browser
  -> Recorder SDK / Playwright
  -> Ingestion API
  -> Event Store
  -> Workflow Compiler
  -> Agent Runner + Evaluator
  -> React Dashboard
```

The backend uses event sourcing and a hexagonal architecture. Core logic lives in `core/`; infrastructure adapters live behind `adapters/`. This keeps the compiler and evaluator testable without a web server or database.

Stack:

- Web: React, TypeScript, Tailwind, React Flow, Framer Motion
- API: FastAPI, Playwright
- Storage: PostgreSQL, Redis, filesystem/object storage adapters
- Tooling: Docker Compose, Playwright, pytest, Vitest

## Repository Layout

```text
agentreplay/
  apps/
    web/                  React dashboard
    api/                  FastAPI ingestion, compiler, runner, evaluator
  packages/
    recorder-sdk/         Browser recorder -> BrowserEvent stream
    playwright-generator/ Workflow graph -> runnable Playwright test
    graph-core/           Events -> states -> workflow graph
    eval-core/            Divergence detection and metrics
    shared-types/         Shared TypeScript contracts
  infra/                  Docker Compose
  examples/               Demo shop, CRM, and calendar workflows
  docs/                   Architecture and implementation docs
  tests/                  End-to-end tests
```

## Real Recording Import

Start the API and dashboard:

```bash
# terminal 1
cd apps/api
pip install -e ".[dev]"
python -m uvicorn app.main:app --reload --port 8000

# terminal 2, from repo root
npm install
npm run dev -w @agentreplay/web
```

Open `http://localhost:3000`, click **Import Recording**, and choose:

```text
examples/demo-calendar/recordings/event.json
```

The API endpoint is also available directly:

```bash
curl -X POST http://localhost:8000/v1/recordings:import \
  -H "content-type: application/json" \
  --data-binary @examples/demo-calendar/recordings/event.json
```

See [docs/real-recordings.md](docs/real-recordings.md) for SDK usage and import details.

## Demo Workflow

1. Record a checkout flow on the bundled demo shop.
2. AgentReplay compiles the event stream into a workflow graph.
3. Run one of the built-in drivers or the LLM driver against the task.
4. Inspect the human and agent paths in the graph.
5. Export a runnable Playwright test or open a pre-filled GitHub issue from the failure summary.

## Event Schema

Recordings are stored as structured browser events:

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

Full schema: [docs/event-schema.md](docs/event-schema.md).

## Generated Playwright Tests

Every recorded workflow compiles to a runnable Playwright test:

```ts
test("checkout workflow", async ({ page }) => {
  await page.goto("https://demo-store.local");
  await page.getByRole("textbox", { name: "Email" }).fill("demo@test.com");
  await page.getByRole("button", { name: "Continue" }).click();
  await expect(page.getByText("Dashboard")).toBeVisible();
});
```

## Evaluation Metrics

AgentReplay reports measurable, step-level outcomes for every run:

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

Definitions: [docs/evaluation.md](docs/evaluation.md).

## Benchmark

Run:

```bash
python -m app.scripts.benchmark
```

You can also use `GET /v1/benchmark` or the **Benchmark** tab in the dashboard.

Bundled demo benchmark across 4 workflows and 3 drivers:

| Driver | Task success | Mean step accuracy | Wrong clicks | Mean first divergence | Network-caused |
| --- | --- | --- | --- | --- | --- |
| scripted | 100% | 100% | 0 | - | 0 |
| divergent | 0% | 63% | 4 | step 6.75 | 1 |
| random | 0% | 47% | 4 | step 4.75 | 1 |

The scripted driver is the always-correct baseline. The divergent and random drivers are deliberate failure drivers. Use `driver=llm` to benchmark the DeepSeek thinking model.

## Contributing

Contributions are welcome: bug reports, docs, demo workflows, and features. See [CONTRIBUTING.md](CONTRIBUTING.md), [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md), and [SECURITY.md](SECURITY.md). Notable changes are tracked in [CHANGELOG.md](CHANGELOG.md).

## License

[MIT](LICENSE)
