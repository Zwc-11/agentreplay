from fastapi.testclient import TestClient

from app import state
from app.main import app
from app.services.benchmark import run_benchmark

client = TestClient(app)

EXPECTED_WORKFLOWS = {"demo-checkout", "checkout-flaky", "crm-demo", "calendar-demo"}


def test_all_seed_workflows_compile():
    state.seed()
    ids = {w["id"] for w in state.store.list_workflows()}
    assert EXPECTED_WORKFLOWS <= ids


def test_scripted_is_perfect_divergent_fails_everywhere():
    state.seed()
    res = run_benchmark(state.store, drivers=["scripted", "divergent"], goal_for=state.goal_for_workflow)
    assert res["workflows"] >= 4
    scripted, divergent = res["drivers"]["scripted"], res["drivers"]["divergent"]
    assert scripted["taskSuccessRate"] == 1.0
    assert scripted["meanStepAccuracy"] == 1.0
    assert divergent["taskSuccessRate"] == 0.0
    assert 0.0 < divergent["meanStepAccuracy"] < 1.0


def test_benchmark_surfaces_network_caused_category():
    state.seed()
    res = run_benchmark(state.store, drivers=["divergent"], goal_for=state.goal_for_workflow)
    assert res["categories"].get("network-caused", 0) >= 1


def test_benchmark_endpoint():
    r = client.get("/v1/benchmark?drivers=scripted,divergent").json()
    assert r["workflows"] >= 4
    assert r["drivers"]["scripted"]["taskSuccessRate"] == 1.0
    assert r["drivers"]["divergent"]["taskSuccessRate"] == 0.0
