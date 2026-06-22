"""Process-wide store + demo seeding. In-memory so the API runs with no DB."""
from __future__ import annotations

import json
import os

from app.adapters.storage.memory import InMemoryStore
from app.services.pipeline import compile_session, ingest

WORKFLOW_ID = "demo-checkout"
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", "..", ".."))
_EXAMPLES = os.path.join(_ROOT, "examples")

RECORDINGS = {
    WORKFLOW_ID: os.path.join(_EXAMPLES, "demo-shop", "recordings", "checkout.json"),
    "checkout-flaky": os.path.join(_EXAMPLES, "demo-shop", "recordings", "checkout_flaky.json"),
    "crm-demo": os.path.join(_EXAMPLES, "demo-crm", "recordings", "lead.json"),
    "calendar-demo": os.path.join(_EXAMPLES, "demo-calendar", "recordings", "event.json"),
}

store = InMemoryStore()
_seeded = False
workflow_goals: dict[str, str] = {}


def seed():
    """Idempotently load the bundled recordings and compile them."""
    global _seeded
    if _seeded:
        return store.get_graph(WORKFLOW_ID)
    for workflow_id, path in RECORDINGS.items():
        with open(path) as f:
            data = json.load(f)
        ingest(store, data["sessionId"], data.get("name", "Workflow"), data["events"])
        compile_session(store, data["sessionId"], graph_id=workflow_id)
        workflow_goals[workflow_id] = data.get("goal", data.get("name", "the workflow"))
    _seeded = True
    return store.get_graph(WORKFLOW_ID)


def goal_for_workflow(workflow_id: str) -> str:
    seed()
    return workflow_goals.get(workflow_id, "the workflow")
