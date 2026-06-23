import os
import pathlib
from dataclasses import dataclass


def _load_dotenv() -> None:
    """Minimal .env loader (no dependency). Populates only vars not already set,
    searching the current directory and this file's parent directories so that
    `cp .env.example .env` works for `python -m ...` and uvicorn, not just Docker."""
    for d in [pathlib.Path.cwd(), *pathlib.Path(__file__).resolve().parents]:
        f = d / ".env"
        if f.is_file():
            try:
                for line in f.read_text().splitlines():
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
            except OSError:
                pass
            break


_load_dotenv()


@dataclass(frozen=True)
class Settings:
    database_url: str = os.getenv(
        "DATABASE_URL", "postgresql://agentreplay:agentreplay@localhost:5432/agentreplay"
    )
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    storage_backend: str = os.getenv("STORAGE_BACKEND", "filesystem")
    storage_dir: str = os.getenv("STORAGE_DIR", "./storage")
    store_backend: str = os.getenv("STORE_BACKEND", "memory")  # memory | postgres
    cors_origins: str = os.getenv("API_CORS_ORIGINS", "http://localhost:3000")
    playwright_base_url: str = os.getenv("PLAYWRIGHT_BASE_URL", "http://localhost:8080")

    # ---- DeepSeek (OpenAI-compatible) ----
    deepseek_api_key: str = os.getenv("DEEPSEEK_API_KEY", "")
    deepseek_base_url: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    deepseek_model: str = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-pro")
    deepseek_reasoning_effort: str = os.getenv("DEEPSEEK_REASONING_EFFORT", "high")
    deepseek_thinking: bool = os.getenv("DEEPSEEK_THINKING", "enabled") != "disabled"

    @property
    def llm_enabled(self) -> bool:
        return bool(self.deepseek_api_key)


settings = Settings()
