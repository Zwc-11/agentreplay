# Local setup (without Docker)

For development you can run each service directly. Prefer Docker (see [deployment.md](deployment.md)) unless you're actively hacking on a service.

## Prerequisites

- Node.js 20+
- Python 3.11+
- PostgreSQL 15+ running locally
- Redis 7+ running locally

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
# run migrations, then:
uvicorn app.main:app --reload --port 8000
```

Start the background worker (compiler + evaluator) in a second terminal:

```bash
cd apps/api && source .venv/bin/activate
python -m app.workers.main
```

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
npm run build -w packages/shared-types
```

## 5. Playwright

```bash
cd apps/api && playwright install chromium
```

## 6. Demo data

Seed the demo workflows so the dashboard has something to show:

```bash
cd apps/api && python -m app.scripts.seed_demo
```

## Tests

```bash
# backend
cd apps/api && pytest

# frontend
cd apps/web && npm test

# end-to-end (AgentReplay testing itself with Playwright)
npm run test:e2e
```

See [evaluation.md](evaluation.md) for what the metrics mean and [workflow-graph.md](workflow-graph.md) for how recordings become graphs.
