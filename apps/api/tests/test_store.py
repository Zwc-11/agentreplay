import json
import os

import pytest

from app.adapters.storage.memory import InMemoryStore
from app.core.workflow.compiler import compile_graph

HERE = os.path.dirname(__file__)
SEED = os.path.abspath(os.path.join(HERE, "..", "..", "..", "examples", "demo-shop", "recordings", "checkout.json"))


def _events():
    with open(SEED) as f:
        return json.load(f)["events"]


def _exercise(store):
    events = _events()
    store.save_session("checkout-demo", "Checkout Demo")
    store.save_events("checkout-demo", events)
    assert len(store.load_events("checkout-demo")) == len(events)

    g = compile_graph(events, "checkout-demo", graph_id="demo-checkout")
    store.save_graph(g, "checkout-demo")
    loaded = store.get_graph("demo-checkout")
    assert loaded is not None
    assert len(loaded.human_commands()) == len(g.human_commands())
    assert store.session_for("demo-checkout") == "checkout-demo"

    wf = [w for w in store.list_workflows() if w["id"] == "demo-checkout"]
    assert wf and wf[0]["steps"] == len(g.human_commands())

    store.save_run({"id": "r1", "workflowId": "demo-checkout", "success": False, "metrics": {}})
    assert store.get_run("r1")["id"] == "r1"
    assert any(r["id"] == "r1" for r in store.list_runs("demo-checkout"))


def test_inmemory_store_conformance():
    _exercise(InMemoryStore())


def test_postgres_store_conformance():
    pytest.importorskip("psycopg")
    from app.adapters.postgres.store import PostgresStore
    from app.config import settings

    try:
        store = PostgresStore(settings.database_url)
    except Exception as e:  # noqa: BLE001
        pytest.skip(f"no reachable Postgres: {e}")
    _exercise(store)
