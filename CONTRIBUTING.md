# Contributing to AgentReplay

Thanks for your interest in improving AgentReplay! This is an open-source **browser workflow simulator** — contributions of all kinds are welcome: bug reports, docs, new demo workflows, agent drivers, and features.

## Ground rules

- Be respectful — see the [Code of Conduct](CODE_OF_CONDUCT.md).
- Keep changes focused; one logical change per pull request.
- Add or update tests for any behavior change.
- Run the checks below before opening a PR.

## Project layout

```
apps/web      React + TypeScript dashboard (Vite)
apps/api      FastAPI backend: compiler, evaluator, agent runner
packages/*    framework-free TS libraries (graph-core, eval-core, …)
examples/*    demo apps + recordings
docs/*        architecture, event schema, evaluation, deployment
```

See [docs/architecture.md](docs/architecture.md) for the design and [docs/local-setup.md](docs/local-setup.md) to run it locally.

## Development setup

Backend (Python 3.11+):

```bash
cd apps/api
python -m venv .venv && . .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8000
```

Frontend + packages (Node 20+):

```bash
npm install
npm run dev -w @agentreplay/web                 # http://localhost:3000
```

## Checks (run before pushing)

```bash
# backend
cd apps/api && ruff check app && pytest

# typescript (from repo root)
npm run typecheck        # all packages + web
npm test                 # package tests + pytest
```

CI runs the same checks on every pull request (see `.github/workflows/ci.yml`).

## Commit & PR conventions

- Write clear, imperative commit messages (e.g. "Add network-causality graph mode").
- Reference issues with `Fixes #123` where applicable.
- Fill in the pull-request template; describe what changed and how you verified it.

## Adding things

- **A demo workflow:** drop a recording JSON under `examples/<app>/recordings/` and register it in `apps/api/app/state.py`.
- **An agent driver:** implement the `AgentDriver` interface and register it in `apps/api/app/adapters/playwright/drivers.py`.
- **A graph mode / metric:** see `packages/graph-core` and `packages/eval-core`.

## License

By contributing, you agree that your contributions are licensed under the [MIT License](LICENSE).
