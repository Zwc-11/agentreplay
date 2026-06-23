"""Choose the storage backend. Defaults to in-memory so the app runs with no DB;
set STORE_BACKEND=postgres (+ DATABASE_URL) for persistence. Falls back to
in-memory if Postgres can't be reached, so a misconfiguration never hard-crashes."""
from __future__ import annotations

import sys

from app.adapters.storage.memory import InMemoryStore
from app.config import settings


def get_store():
    if settings.store_backend == "postgres":
        try:
            from app.adapters.postgres.store import PostgresStore

            return PostgresStore(settings.database_url)
        except Exception as e:  # noqa: BLE001 - degrade, don't crash, on a bad DB config
            print(f"[agentreplay] Postgres unavailable ({e}); using in-memory store.", file=sys.stderr)
    return InMemoryStore()
