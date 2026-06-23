.DEFAULT_GOAL := help
.PHONY: help install api web dev demo bench live test typecheck lint up

help:  ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-11s\033[0m %s\n", $$1, $$2}'

install:  ## Install backend + frontend dependencies
	cd apps/api && pip install -e ".[dev]"
	npm install

api:  ## Run the API at http://localhost:8000
	cd apps/api && uvicorn app.main:app --reload --port 8000

web:  ## Run the dashboard at http://localhost:3000 (works offline)
	npm run dev -w @agentreplay/web

demo:  ## Run the full pipeline in the terminal (DRIVER=divergent|scripted|random|llm)
	cd apps/api && python -m app.scripts.demo $(DRIVER) 

bench:  ## Print the benchmark table (all drivers x all workflows)
	cd apps/api && python -m app.scripts.benchmark

live:  ## Live Playwright capture + run (needs: python -m playwright install chromium)
	cd apps/api && python -m app.scripts.live

test:  ## Run all tests (TS packages + backend)
	npm test

typecheck:  ## Typecheck every package + the web app
	npm run typecheck

lint:  ## Lint the backend
	cd apps/api && ruff check app

up:  ## Start everything with Docker Compose
	docker compose -f infra/docker-compose.yml up

