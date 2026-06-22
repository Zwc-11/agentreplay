# Local setup (without Docker)

For development you can run each service directly. Prefer Docker (see [deployment.md](deployment.md)) unless you're actively hacking on a service.

## Prerequisites

- Node.js 20+
- Python 3.11+
- PostgreSQL 15+ and Redis 7+ are only needed when you switch away from the default in-memory demo store

## 1. Environment

```bash
cp .env.example .env
# edit DATABASE_URL / REDIS_URL if your local services differ
```

## 2. Backend (FastAPI)

```bash
cd apps/api
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8000
```

The API seeds the bundled demo recordings on startup. No database, Redis, migrations, or worker are required for the MVP flow.

## 3. Frontend (React dashboard)

```bash
cd apps/web
npm install
npm run dev   # http://localhost:3000
```

## 4. Packages

The TypeScript packages (`recorder-sdk`, `playwright-generator`, `graph-core`, `eval-core`, `shared-types`) are npm workspaces. From the repo root:

```bash
npm install            # installs all workspace deps
npm run build -w @agentreplay/recorder-sdk
```

## 5. Playwright

```bash
cd apps/api && playwright install chromium
```

## 6. Demo data

The demo workflows are loaded automatically from `examples/**/recordings/*.json`.

To test real-data import, open the dashboard and choose **Import Recording**, then pick:

```text
examples/demo-calendar/recordings/event.json
```

See [real-recordings.md](real-recordings.md) for the recorder SDK, import API, and E2E verification path.

## Tests

```bash
npm run typecheck
npm test
npx playwright install chromium
npm run test:e2e
```

See [evaluation.md](evaluation.md) for what the metrics mean and [workflow-graph.md](workflow-graph.md) for how recordings become graphs.
