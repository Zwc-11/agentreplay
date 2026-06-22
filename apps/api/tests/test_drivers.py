from app.adapters.playwright.drivers import DivergentAgentDriver, RandomAgentDriver, ScriptedAgentDriver, get_driver
from app.core.agent import WorkflowTask
from app.core.graph.model import Command

HUMAN = [
    Command("click", role="textbox", name="Email"),
    Command("click", role="button", text="Sign in"),
    Command("click", role="button", text="Place order"),
]


def _task():
    return WorkflowTask("w", "goal", "https://x.local", HUMAN)


def test_scripted_follows_human_and_succeeds():
    r = ScriptedAgentDriver().run(_task())
    assert r.success is True
    assert len(r.commands) == len(HUMAN)


def test_divergent_diverges_at_last_click():
    r = DivergentAgentDriver().run(_task())
    assert r.success is False
    assert r.commands[:2] == HUMAN[:2]
    assert r.commands[-1].name == "Special offer"


def test_random_is_deterministic():
    a = RandomAgentDriver(seed=7).run(_task()).commands
    b = RandomAgentDriver(seed=7).run(_task()).commands
    assert [c.to_dict() for c in a] == [c.to_dict() for c in b]


def test_get_driver_unknown_raises():
    try:
        get_driver("nope")
        assert False, "expected ValueError"
    except ValueError:
        pass
