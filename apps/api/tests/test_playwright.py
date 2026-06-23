from types import SimpleNamespace

from app.adapters.playwright.recorder import PlaywrightRecorder
from app.adapters.playwright.runner import PlaywrightAgentDriver
from app.core.agent import WorkflowTask
from app.core.evaluation.metrics import compute_metrics
from app.core.graph.model import Command
from app.core.workflow.compiler import compile_graph


def _response(status, url="http://x/api/checkout", method="POST"):
    return SimpleNamespace(request=SimpleNamespace(method=method), url=url, status=status)


class _Loc:
    def __init__(self, page, key):
        self.page, self.key = page, key

    def click(self, timeout=None):
        self.page.calls.append(("click", self.key))
        b = self.page.behavior.get(self.key, {})
        if "raise" in b:
            raise RuntimeError(b["raise"])
        if "fire" in b:
            self.page._emit(b["fire"])

    def fill(self, value, timeout=None):
        self.page.calls.append(("fill", self.key, value))

    def is_visible(self):
        return self.page.behavior.get(self.key, {}).get("visible", True)


class FakePage:
    def __init__(self, behavior=None):
        self.behavior = behavior or {}
        self.calls = []
        self._handlers = {}

    def on(self, event, cb):
        self._handlers.setdefault(event, []).append(cb)

    def _emit(self, resp):
        for cb in self._handlers.get("response", []):
            cb(resp)

    def goto(self, url):
        self.calls.append(("goto", url))

    def get_by_role(self, role, name=None):
        return _Loc(self, name)

    def get_by_text(self, text):
        return _Loc(self, text)

    def locator(self, selector):
        return _Loc(self, selector)


HUMAN = [
    Command("goto", url="/"),
    Command("click", role="button", text="Place order", selector="#po"),
    Command("assertVisible", text="Order confirmed", selector=".c"),
]


def test_driver_executes_full_path_successfully():
    page = FakePage()
    r = PlaywrightAgentDriver(base_url="http://x", page=page).run(WorkflowTask("w", "g", "http://x", HUMAN))
    assert r.success is True
    assert len(r.commands) == len(HUMAN)
    assert ("goto", "http://x/") in page.calls  # base_url absolutized


def test_driver_stops_at_live_failure_and_records_error():
    page = FakePage({"Place order": {"raise": "timeout 5000ms exceeded"}})
    r = PlaywrightAgentDriver(base_url="http://x", page=page).run(WorkflowTask("w", "g", "http://x", HUMAN))
    assert r.success is False
    assert len(r.commands) == 1  # only the goto executed
    assert "click" in r.error


def test_driver_captures_network_and_eval_flags_network_caused():
    page = FakePage({"Place order": {"fire": _response(500)}, "Order confirmed": {"visible": False}})
    r = PlaywrightAgentDriver(base_url="http://x", page=page).run(WorkflowTask("w", "g", "http://x", HUMAN))
    assert r.success is False
    assert any(n["status"] == 500 for n in r.network)
    m = compute_metrics(HUMAN, r.commands, r.success, r.network)
    assert m["network_caused_failure"] is True
    assert m["divergence_step"] == 2


def test_recorder_builds_recording_that_compiles():
    actions = [
        Command("goto", url="/"),
        Command("click", role="button", text="Buy", selector="#b"),
        Command("fill", role="textbox", name="Qty", value="2", selector="#q"),
        Command("assertVisible", text="Done", selector=".d"),
    ]
    page = FakePage({"Buy": {"fire": _response(200, url="http://x/api/buy")}})
    rec = PlaywrightRecorder("s", "n", "complete", base_url="http://x", page=page).record(actions)
    types = [e["eventType"] for e in rec["events"]]
    assert types == ["navigation", "click", "network", "input", "assertion"]
    assert rec["events"][2]["network"]["status"] == 200
    graph = compile_graph(rec["events"], "s")
    assert any(e.kind == "network-dependency" for e in graph.edges)
    assert len(graph.human_commands()) == 3  # goto is the initial state, then click+fill+assert
