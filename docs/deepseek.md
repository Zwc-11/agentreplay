# Using the DeepSeek v4 Pro thinking model

AgentReplay can use DeepSeek's thinking model in two places:

1. **LLM agent driver** (`driver=llm`) — DeepSeek chooses the next browser action at each state; AgentReplay compares its path to the human recording and shows the first divergence.
2. **AI failure summary** - when a run fails, DeepSeek writes the root-cause narrative. Falls back to the built-in heuristic when no key is set.

DeepSeek is OpenAI-SDK compatible, so this uses the `openai` package pointed at `https://api.deepseek.com`. Request shape (verified against the [thinking-mode docs](https://api-docs.deepseek.com/guides/thinking_mode)): `model="deepseek-v4-pro"`, `reasoning_effort="high"`, `extra_body={"thinking": {"type": "enabled"}}`; `message.reasoning_content` may be returned, but AgentReplay does not expose raw reasoning in user-facing summaries.

## 1. Install

```powershell
cd C:\AgentReplay\apps\api
pip install -e ".[dev]"      # installs openai (needs Python 3.11+)
```

## 2. Configure the key

The app auto-loads a `.env` file from the repo root. Easiest: put your key there once.

```powershell
# from C:\AgentReplay
Copy-Item .env.example .env
notepad .env                 # set DEEPSEEK_API_KEY=<your-deepseek-api-key>
```

`.env`:

```bash
DEEPSEEK_API_KEY=<your-deepseek-api-key>
DEEPSEEK_MODEL=deepseek-v4-pro
DEEPSEEK_REASONING_EFFORT=high     # high | max
DEEPSEEK_THINKING=enabled          # enabled | disabled
```

Or set it for the current shell instead of using `.env`:

```powershell
# PowerShell (Windows)
$env:DEEPSEEK_API_KEY = "<your-deepseek-api-key>"
```
```bash
# macOS / Linux
export DEEPSEEK_API_KEY=<your-deepseek-api-key>
```

> Note: `<your-deepseek-api-key>` is a placeholder. Use your actual key locally.

## 3. Verify the connection

```powershell
cd C:\AgentReplay\apps\api
python -m app.scripts.deepseek_check
```

Expected: it prints whether `reasoning_content` was returned and a `content` line. If it says "DeepSeek is NOT configured", the key isn't being read.

## 4. Run it

**DeepSeek as the agent under test (CLI):**

```powershell
python -m app.scripts.demo llm
```

The model is shown the goal and a shuffled list of candidate actions at each step (the correct next action plus distractors such as a lookalike "Special offer" ad) and must pick one. Its picks form the agent path; if it ever picks a distractor, that step becomes the divergence.

**Via the API:**

```powershell
uvicorn app.main:app --port 8000
# then, in another shell:
curl.exe -X POST "http://localhost:8000/v1/workflows/demo-checkout/runs?driver=llm"
```

The response includes `llmEnabled: true`, the agent's `comparison`, `metrics`, and a DeepSeek-written `summary` (with `"model": "deepseek"`). **Failure summaries** use DeepSeek automatically whenever the key is set.

## What to fix / configure (checklist)

- **Set `DEEPSEEK_API_KEY`** (in `.env` or `$env:`) — the one required step. Without it, `driver=llm` falls back to the correct path and summaries stay heuristic.
- **Python 3.11+** — `pyproject.toml` requires it; `pip install -e ".[dev]"` will refuse on 3.10.
- **Install `openai`** — included via `pip install -e ".[dev]"`, or `pip install openai`.
- **Model id** — use `deepseek-v4-pro` (thinking) or `deepseek-v4-flash`. The legacy `deepseek-reasoner`/`deepseek-chat` ids retire **2026-07-24**.
- **PowerShell env syntax** — `$env:DEEPSEEK_API_KEY="..."`, not `DEEPSEEK_API_KEY=... python` (that bash form errors in PowerShell).
- **SOCKS proxy** — if you run behind one you'll see `Using SOCKS proxy, but 'socksio' is not installed`; fix with `pip install "httpx[socks]"`.
- **Thinking-mode params** — `temperature`, `top_p`, `presence_penalty`, `frequency_penalty` are ignored in thinking mode.
- **Cost / latency** — the agent driver makes one thinking call per workflow step; use `deepseek-v4-flash` or lower `DEEPSEEK_REASONING_EFFORT` for cheaper runs, and add retry/backoff in `DeepSeekClient.complete` for big batches.

## Where it lives

- `apps/api/app/adapters/llm/deepseek.py` — the client (`DeepSeekClient`, `get_default_client`).
- `apps/api/app/adapters/playwright/drivers.py` — `LLMAgentDriver` (registered as `llm`).
- `apps/api/app/adapters/llm/summary.py` — DeepSeek-refined failure summary.
- `apps/api/app/config.py` — `DEEPSEEK_*` settings + `.env` auto-loader.
- `apps/api/app/scripts/deepseek_check.py` — connection smoke test.
