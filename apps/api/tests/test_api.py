from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_list_workflows():
    r = client.get("/v1/workflows").json()
    assert any(w["id"] == "demo-checkout" for w in r["workflows"])


def test_demo_payload_has_graph_and_divergent_run():
    r = client.get("/v1/demo").json()
    assert r["workflow"]["nodes"]
    assert r["run"]["metrics"]["divergence_step"] == 13


def test_graph_and_test_endpoints():
    g = client.get("/v1/workflows/demo-checkout/graph").json()
    assert len(g["nodes"]) == 21
    t = client.get("/v1/workflows/demo-checkout/test").json()
    assert "@playwright/test" in t["test"]


def test_run_and_fetch():
    run = client.post("/v1/workflows/demo-checkout/runs?driver=divergent").json()
    fetched = client.get(f"/v1/runs/{run['id']}").json()
    assert fetched["id"] == run["id"]
    assert fetched["metrics"]["failure_category"] == "wrong-element"
