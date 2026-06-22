from app.core.evaluation.divergence import detect_divergence
from app.core.evaluation.metrics import compute_metrics
from app.core.graph.model import Command

HUMAN = [
    Command("click", selector="#email", role="textbox", name="Email"),
    Command("fill", selector="#email", role="textbox", name="Email", value="a@b.c"),
    Command("click", selector="#submit", role="button", text="Continue"),
]


def test_no_divergence_when_paths_match():
    assert detect_divergence(HUMAN, HUMAN) is None


def test_divergence_at_first_mismatch():
    agent = HUMAN[:2] + [Command("click", selector=".ad", role="link", name="Ad")]
    assert detect_divergence(HUMAN, agent) == 2


def test_metrics_for_wrong_element():
    agent = HUMAN[:2] + [Command("click", selector=".ad", role="link", name="Ad")]
    m = compute_metrics(HUMAN, agent, success=False)
    assert m["step_accuracy"] == round(2 / 3, 4)
    assert m["divergence_step"] == 2
    assert m["wrong_click_count"] == 1
    assert m["failure_category"] == "wrong-element"
    assert m["recovered"] is False


def test_network_caused_failure_classification():
    agent = HUMAN[:2] + [Command("click", selector=".ad", role="link", name="Ad")]
    m = compute_metrics(HUMAN, agent, success=False, network_events=[{"status": 500}])
    assert m["failure_category"] == "network-caused"
    assert m["network_caused_failure"] is True


def test_full_success_has_no_category():
    m = compute_metrics(HUMAN, HUMAN, success=True)
    assert m["divergence_step"] is None
    assert m["failure_category"] is None
    assert m["step_accuracy"] == 1.0
