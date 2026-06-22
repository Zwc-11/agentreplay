from app import state
from app.services.pipeline import run_agent


def test_end_to_end_divergent_run():
    state.seed()
    run = run_agent(state.store, state.WORKFLOW_ID, "divergent", goal="complete a checkout")
    m = run["metrics"]
    assert run["success"] is False
    assert m["divergence_step"] == 13          # 14th step (Place order)
    assert m["failure_category"] == "wrong-element"
    assert m["wrong_click_count"] == 1
    assert run["comparison"]["divergenceStep"] == 13
    assert "@playwright/test" in run["generatedTest"]
    assert run["summary"]["githubIssue"]["title"].startswith("Agent diverged at step 14")


def test_scripted_run_succeeds_fully():
    state.seed()
    run = run_agent(state.store, state.WORKFLOW_ID, "scripted", goal="complete a checkout")
    assert run["success"] is True
    assert run["metrics"]["divergence_step"] is None
    assert run["metrics"]["step_accuracy"] == 1.0
