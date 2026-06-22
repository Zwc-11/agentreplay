"""Process-wide store + demo seeding. In-memory so the API runs with no DB."""
from __future__ import annotations

import json
import os

from app.adapters.storage.memory import InMemoryStore
from app.services.pipeline import compile_session, ingest

WORKFLOW_ID = "demo-checkout"
_HERE = os.path.dirname(os.path.abspath(__file__))
SEED_PATH = os.path.abspath(
    os.path.join(_HERE, "..", "..", "..", "examples", "demo-shop", "recordings", "checkout.json")
)

store = InMemoryStore()
_seeded = False


def seed():
    """Idempotently load the bundled checkout recording and compile it."""
    global _seeded
    if _seeded:
        return store.get_graph(WORKFLOW_ID)
    with open(SEED_PATH) as f:
        data = json.load(f)
    ingest(store, data["sessionId"], data.get("name", "Workflow"), data["events"])
    graph = compile_session(store, data["sessionId"], graph_id=WORKFLOW_ID)
    _seeded = True
    return graph
