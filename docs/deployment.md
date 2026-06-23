# Deployment

AgentReplay is designed to run with a single command for local/demo use, and to deploy frontend and backend separately for hosted demos.

## One Command

```bash
cp .env.example .env
docker compose -f infra/docker-compose.yml up
```

Services:

| Service | Port | Purpose |
| --- | --- | --- |
| `web` | 3000 | React dashboard |
| `api` | 8000 | FastAPI ingestion, compiler, runner, evaluator |
| `worker` | n/a | Redis-backed background jobs |
| `postgres` | 5432 | Event store and metadata |
| `redis` | 6379 | Queue |

Open the dashboard at `http://localhost:3000`. The dashboard includes demo mode with seeded workflows, so a first-time visitor can explore the graph, replay, and metrics without recording anything.

## Configuration

Configuration is via environment variables. See [`.env.example`](../.env.example).

Key groups:

- Database: `STORE_BACKEND`, `DATABASE_URL`
- Queue: `REDIS_URL`
- Object storage: `STORAGE_BACKEND`, `STORAGE_DIR`, or S3/R2 keys
- LLM settings: `DEEPSEEK_API_KEY`, used only when the LLM driver or model-backed summaries are enabled
- Frontend API target: `VITE_API_URL`

## Hosted Demo

Because the dashboard is offline-first, it can be published as a static demo even when the API is unreachable. It bundles a demo fixture and falls back automatically.

Recommended targets:

- Frontend: Vercel, Cloudflare Pages, or any static host
- Backend and worker: Render or Fly.io
- Database: managed Postgres
- Queue: managed Redis
- Object storage: local filesystem for demo, S3/R2 for shared hosted environments

Point the frontend at the API with `VITE_API_URL`.

## Vercel

`vercel.json` builds `apps/web` to `apps/web/dist`.

Steps:

1. Import the repository in Vercel.
2. Use the included `vercel.json`.
3. Set `VITE_API_URL` if a hosted API is available.

## Render

`render.yaml` is a Render blueprint with:

- API as a Docker service, health-checked at `/health`
- Dashboard as a static site
- `STORE_BACKEND=memory` by default for a zero-database demo

Point Render at the repository and it can provision both services.

## GitHub Pages

GitHub Pages also works for the offline dashboard, but Pages must first be enabled in the repository settings. Enable:

```text
Settings -> Pages -> Source: GitHub Actions
```

Then add or run a Pages deployment workflow that builds the dashboard with:

```bash
VITE_BASE=/agentreplay/ npm run build -w @agentreplay/web
```

This repository does not enable the Pages workflow by default because GitHub Actions cannot create the Pages site unless Pages is already enabled for the repository.

## Production Notes

- Object storage should move off the local filesystem for shared hosted environments.
- API keys should scope ingestion per project.
- Add rate limits at the ingestion edge before public multi-tenant use.
- Event-sourced replay data doubles as an audit trail and makes projections reproducible.

## CI/CD

GitHub Actions (`.github/workflows/ci.yml`) runs:

- backend lint
- backend tests
- workspace typechecks
- package tests
- Playwright dashboard E2E
- Docker builds

## End-To-End Check

```bash
npm run test:e2e
```

The E2E suite builds the dashboard and runs Playwright against the offline demo. See `tests/e2e/dashboard.spec.ts`.
