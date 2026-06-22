import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    database_url: str = os.getenv("DATABASE_URL", "postgresql://agentreplay:agentreplay@localhost:5432/agentreplay")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    storage_backend: str = os.getenv("STORAGE_BACKEND", "filesystem")
    storage_dir: str = os.getenv("STORAGE_DIR", "./storage")
    cors_origins: str = os.getenv("API_CORS_ORIGINS", "http://localhost:3000")


settings = Settings()
