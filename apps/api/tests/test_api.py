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


def test_import_recording_compiles_and_runs():
    payload = {
        "sessionId": "imported-smoke",
        "workflowId": "imported-smoke",
        "name": "Imported smoke workflow",
        "goal": "confirm imported flow",
        "events": [
            {
                "sessionId": "imported-smoke",
                "stepIndex": 0,
                "eventType": "navigation",
                "url": "https://example.local/start",
                "timestamp": "2026-06-22T20:00:00Z",
            },
            {
                "sessionId": "imported-smoke",
                "stepIndex": 1,
                "eventType": "click",
                "url": "https://example.local/start",
                "timestamp": "2026-06-22T20:00:01Z",
                "target": {"selector": "#confirm", "role": "button", "text": "Confirm"},
            },
            {
                "sessionId": "imported-smoke",
                "stepIndex": 2,
                "eventType": "assertion",
                "url": "https://example.local/start",
                "timestamp": "2026-06-22T20:00:02Z",
                "target": {"selector": ".done", "text": "Done"},
            },
        ],
    }
    imported = client.post("/v1/recordings:import", json=payload).json()
    assert imported["workflowId"] == "imported-smoke"
    assert len(imported["workflow"]["nodes"]) == 3

    workflows = client.get("/v1/workflows").json()["workflows"]
    assert any(w["id"] == "imported-smoke" and w["name"] == "Imported smoke workflow" for w in workflows)

    run = client.post("/v1/workflows/imported-smoke/runs?driver=scripted").json()
    assert run["success"] is True
    assert run["summary"]["summary"].startswith("Agent completed confirm imported flow")


def test_import_recording_rejects_empty_events():
    response = client.post(
        "/v1/recordings:import",
        json={"sessionId": "empty-import", "name": "Empty import", "events": []},
    )
    assert response.status_code == 422


def test_root_index_orients_the_user():
    r = client.get("/").json()
    assert r["name"] == "AgentReplay"
    assert r["endpoints"]["workflows"] == "/v1/workflows"
    assert r["docs"] == "/docs"
