import json

from app.adapters.llm.summary import generate_summary
from app.adapters.playwright.drivers import LLMAgentDriver, get_driver
from app.core.agent import WorkflowTask
from app.core.evaluation.metrics import compute_metrics
from app.core.graph.model import Command

HUMAN = [
    Command("click", role="textbox", name="Email"),
    Command("fill", role="textbox", name="Email", value="a@b.c"),
    Command("click", role="button", text="Place order"),
]


class PickKeyword:
    """Fake DeepSeek client that picks the option whose line contains `kw`."""

    def __init__(self, kw):
        self.kw = kw

    def complete(self, messages, json_mode=False):
        user = messages[-1]["content"]
        idx = 0
        for line in user.splitlines():
            head = line.split(".", 1)[0].strip()
            if head.isdigit() and self.kw in line:
                idx = int(head)
                break
        return {"content": json.dumps({"choice": idx}), "reasoning": "chain of thought"}


class FixedText:
    def __init__(self, text):
        self.text = text

    def complete(self, messages, json_mode=False):
        return {"content": self.text, "reasoning": "because the ad looked like the button"}


def _task():
    return WorkflowTask("w", "complete a checkout", "https://x.local", HUMAN)


def test_llm_driver_diverges_when_model_picks_distractor():
    r = LLMAgentDriver(client=PickKeyword("Special offer")).run(_task())
    assert r.success is False
    assert r.commands[-1].name == "Special offer"


def test_llm_driver_without_client_falls_back_to_correct_path():
    r = LLMAgentDriver(client=None).run(_task())
    assert r.success is True
    assert len(r.commands) == len(HUMAN)


def test_get_driver_llm_is_registered():
    d = get_driver("llm")
    assert d.name == "llm"


def test_summary_uses_deepseek_when_client_present():
    agent = HUMAN[:2] + [Command("click", selector=".ad", role="link", name="Special offer")]
    m = compute_metrics(HUMAN, agent, success=False)
    s = generate_summary(
        None,
        HUMAN,
        agent,
        m,
        goal="checkout",
        client=FixedText("Root cause: it clicked a lookalike ad."),
    )
    assert s["model"] == "deepseek"
    assert "lookalike ad" in s["summary"]
    assert s["rootCause"] == "Root cause: it clicked a lookalike ad."


def test_summary_falls_back_without_client():
    agent = HUMAN[:2] + [Command("click", selector=".ad", role="link", name="Special offer")]
    m = compute_metrics(HUMAN, agent, success=False)
    s = generate_summary(None, HUMAN, agent, m, goal="checkout", client=None)
    assert s["model"] is None
    assert "diverged at step 3" in s["summary"]
