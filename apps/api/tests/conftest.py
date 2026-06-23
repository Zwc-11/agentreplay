"""Test fixtures. Keep the suite hermetic: never use a real DeepSeek key, so
runs go through the deterministic heuristic path and make no network calls."""
import app.config as cfg

# A developer may have a real key in .env; tests must not use it.
object.__setattr__(cfg.settings, "deepseek_api_key", "")
