# Deployment

AgentReplay is designed to run with a single command for local/demo use, and to deploy frontend + backend separately for a hosted demo.

## One command (local / demo)

```bash
cp .env.example .env
docker compose -f infra/docker-compose.yml up
```

Services:

| Service | Port | Purpose |
| --- | --- | --- |
| `web` | 3000 | React dashboard |
| `api` | 8000 | FastAPI: ingestion, compiler, agent runner, evaluator |
| `worker` | — | Redis-backed compiler + evaluator jobs |
| `postgres` | 5432 | event store + metadata |
| `redis` | 6379 | queue |

Open the dashboard at `http://localhost:3000`. The dashboard includes **demo mode** with seeded workflows, so a first-time visitor can explore the graph, replay, and metrics without recording anything.

## Configuration

All configuration is via environment variables. See [`.env.example`](../.env.example). Key groups: database (`DATABASE_URL`), queue (`REDIS_URL`), object storage (`STORAGE_BACKEND`, `STORAGE_DIR`, or S3/R2 keys), and LLM settings (`DEEPSEEK_API_KEY`, used only when the LLM driver or model-backed summaries are enabled).

## Hosted demo

A recruiter-friendly hosted demo should let visitors click around even if the backend serves seeded data:

- **Frontend:** Vercel or Cloudflare Pages (`apps/web`).
- **Backend + worker:** Render or Fly.io (`apps/api`), with managed Postgres and Redis.
- **Object storage:** start on the instance filesystem; move to S3/R2 for persistence.

Point the frontend at the API with `VITE_API_URL`.

## Production notes

- **Migrations** run on API start (or as a one-off job) from `apps/api/migrations`.
- **Object storage** should move off the local filesystem to S3/R2 for any shared/hosted environment.
- **API keys** scope ingestion per project; add rate limits at the ingestion edge (Week 6).
- **Observability** — because the system is event-sourced, replays and projections are reproducible from the log, which doubles as an audit trail.

## CI/CD

GitHub Actions (`.github/workflows/ci.yml`) runs lint, typecheck, backend tests, frontend tests, Playwright e2e, and a Docker build on every push/PR. A deploy workflow can promote `main` to the hosting providers above.

## Hosted demo & deploy targets

Because the dashboard is **offline-first** (it bundles a demo fixture and falls back to it when the API is unreachable), you can publish a fully interactive demo with **no backend at all**.

### GitHub Pages (zero backend, recommended for the demo)

`.github/workflows/deploy-pages.yml` builds the dashboard and publishes it. Enable Pages once (Settings → Pages → Source: GitHub Actions). Every push to `main` then updates:

```
https://zwc-11.github.io/agentreplay/
```

The build sets `VITE_BASE=/agentreplay/` so asset paths resolve under the project path.

### Vercel (web)

`vercel.json` builds `apps/web` to `apps/web/dist`. Import the repo in Vercel — no config needed.

### Render (API + web)

`render.yaml` is a Render blueprint: the API as a Docker service (health-checked at `/health`) and the dashboard as a static site wired to it via `VITE_API_URL`. Point Render at the repo and it provisions both.

### Object storage

Screenshots and DOM snapshots are stored via the object-storage adapter (`STORAGE_DIR`, filesystem by default) and served at `GET /v1/blobs/{key}`. Live recordings (`python -m app.scripts.record` / `live`) capture real screenshots; the replay panel loads them and falls back to a placeholder when a blob is absent. Swap in S3/R2 behind the same `ObjectStore` interface for shared/hosted environments.

### Persistence

The default in-memory store needs no database. For durable data set `STORE_BACKEND=postgres` and `DATABASE_URL`; the `PostgresStore` creates its own JSONB tables on first use.

### End-to-end check

`npm run test:e2e` builds the dashboard and runs Playwright against it offline (no API needed). See `tests/e2e/dashboard.spec.ts`.
