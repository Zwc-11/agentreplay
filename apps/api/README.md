# AgentReplay API

FastAPI backend using **event sourcing** + **hexagonal architecture**. Domain logic lives in `app/core` (workflow, evaluation, graph, replay) and is independent of `app/adapters` (postgres, playwright, redis, llm, storage). See [../../docs/architecture.md](../../docs/architecture.md).

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8000
```
