# Real recordings

AgentReplay can now test more than the bundled MVP demo data. You can import a browser-event recording from JSON, or use the recorder SDK in a real web app and send events to the API.

## Run locally

Terminal 1:

```bash
cd apps/api
pip install -e ".[dev]"
python -m uvicorn app.main:app --reload --port 8000
```

Terminal 2:

```bash
npm install
npm run dev -w @agentreplay/web
```

Open `http://localhost:3000`.

## Import JSON from the dashboard

1. Click **Import Recording**.
2. Pick a recording JSON file.
3. The backend validates the event stream, stores it, compiles a workflow graph, and the dashboard switches to the imported workflow.

Example files:

```text
examples/demo-shop/recordings/checkout.json
examples/demo-shop/recordings/checkout_flaky.json
examples/demo-crm/recordings/lead.json
examples/demo-calendar/recordings/event.json
```

The import payload shape is:

```json
{
  "sessionId": "calendar-demo",
  "workflowId": "calendar-demo",
  "name": "Calendar - create an event",
  "goal": "create a calendar event",
  "events": []
}
```

`events` must contain at least one `BrowserEvent`.

## Import JSON through the API

```bash
curl -X POST http://localhost:8000/v1/recordings:import \
  -H "content-type: application/json" \
  --data-binary @examples/demo-calendar/recordings/event.json
```

Then run an agent against it:

```bash
curl -X POST "http://localhost:8000/v1/workflows/calendar-demo/runs?driver=scripted"
```

## Record from a real app

Install and start the recorder in the browser app you want to test:

```ts
import { Recorder } from "@agentreplay/recorder-sdk";

const recorder = new Recorder({
  sessionId: `checkout-${Date.now()}`,
  ingestUrl: "http://localhost:8000/v1/events:batch",
  batchSize: 10,
});

recorder.start();

// When the workflow is finished:
recorder.stop();
const recording = recorder.exportRecording("Checkout flow", "complete checkout");
```

You can upload `recording` from the dashboard or post it to `POST /v1/recordings:import`.

## Verify the path

```bash
npm run typecheck
npm test
npx playwright install chromium
npm run test:e2e
```

The E2E smoke test imports the calendar recording through the dashboard file input and verifies the replay, graph, metrics, and timeline.

## Live Playwright capture & run (no hand-written JSON)

The bundled `demo-shop` app can be recorded and driven by a **real browser** end to end. Install browsers once:

```bash
cd apps/api
pip install -e ".[dev]"
python -m playwright install chromium
```

One command — serves the app, records it live, runs the agent against a broken checkout, and reports where it failed:

```bash
python -m app.scripts.live
```

Or step by step:

```bash
# 1) serve the demo-shop app (append ?broken=1 to break checkout)
python -m app.scripts.serve_demo                 # http://localhost:8080

# 2) record it live into a recording JSON
python -m app.scripts.record --url http://localhost:8080 --out live-checkout.json

# 3) import it, then run the live Playwright agent against it
curl -X POST http://localhost:8000/v1/recordings:import \
  -H "content-type: application/json" --data-binary @live-checkout.json
curl -X POST "http://localhost:8000/v1/workflows/live-checkout/runs?driver=playwright"
```

`driver=playwright` executes each recorded command in Chromium, captures the real network responses, and stops at the first step that fails live (e.g. a `500` on checkout). AgentReplay then classifies the failure (network-caused, wrong-element, …) exactly like the seeded drivers.

The capture/execution logic is unit-tested against a fake page (`apps/api/tests/test_playwright.py`), so CI stays green **without** a browser — only the live CLIs (`serve_demo`, `record`, `live`) and `driver=playwright` need Chromium installed.
