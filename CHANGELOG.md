# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Browser **workflow compiler**: events → states → action graph (framework-free `graph-core`).
- **Divergence detection** + step-level metrics and failure categorisation (`eval-core`).
- **Agent drivers** behind one interface: `scripted`, `divergent`, `random`, `playwright` (live), and `llm` (DeepSeek v4 Pro thinking model).
- **Playwright test generator** and a heuristic + DeepSeek-refined **AI failure summary**.
- **Live Playwright** capture (`PlaywrightRecorder`) and execution (`PlaywrightAgentDriver`) against a bundled servable demo-shop app.
- **Benchmark** across every workflow × driver: CLI (`python -m app.scripts.benchmark`), API (`GET /v1/benchmark`), and a dashboard Benchmark tab.
- **React dashboard**: human-vs-agent graph (4 modes, colour-coded, pulsing divergence), replay scrubber, timeline, metrics, failure summary, test export, recording import.
- FastAPI backend with **event-sourcing** + **hexagonal** core/adapters; in-memory store (default) and a **PostgreSQL** persistence adapter.
- Demo recordings for checkout, flaky checkout (500 → retry), CRM, and calendar.
- Docs: architecture, event schema, workflow graph, evaluation, deployment, DeepSeek, real recordings.

- **Offline-first dashboard**: bundles a demo fixture and falls back to it when the API is unreachable; a Live/Demo-mode indicator in the app bar.
- **Hosted demo** deploy configs: GitHub Pages workflow (zero-backend static demo), `vercel.json`, and a `render.yaml` blueprint (API + web).
- **Object storage** adapter (filesystem) + `GET /v1/blobs/{key}`; the live recorder captures real screenshots and the replay panel renders them.
- Real Playwright **e2e** against the built dashboard (offline); friendly API root index; a **Makefile** of one-command workflows.

### Notes
- LLMs are used only for human-readable summaries and the optional `llm` driver, never for core logic.

[Unreleased]: https://github.com/Zwc-11/agentreplay/commits/main
