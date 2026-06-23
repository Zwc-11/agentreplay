"""Drive a live page with Playwright and capture a BrowserEvent recording.

This is a 'scripted capture': it executes a known action script against a real
browser while recording the resulting events (actions interleaved with the
network responses they triggered). The event-building core is unit-tested with
a fake page; a live capture lazily imports playwright.
"""
from __future__ import annotations

from datetime import datetime, timezone

from app.adapters.playwright.runner import DEFAULT_TIMEOUT_MS, absolutize, attach_network, execute_command
from app.core.graph.model import Command


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _target(c: Command) -> dict:
    t: dict = {}
    if c.selector:
        t["selector"] = c.selector
    if c.role:
        t["role"] = c.role
    if c.name:
        t["label"] = c.name
    if c.text:
        t["text"] = c.text
    return t


def _event_for(c: Command, step: int, url: str | None, session_id: str) -> dict:
    base = {"sessionId": session_id, "stepIndex": step, "timestamp": _now(), "url": url}
    if c.kind == "goto":
        return {**base, "eventType": "navigation", "url": url or c.url}
    if c.kind == "click":
        return {**base, "eventType": "click", "target": _target(c)}
    if c.kind == "fill":
        return {**base, "eventType": "input", "target": _target(c), "payload": {"value": c.value or ""}}
    if c.kind == "assertVisible":
        return {**base, "eventType": "assertion", "target": _target(c)}
    return {**base, "eventType": "error"}


# Default capture script for the bundled demo-shop SPA.
CHECKOUT_ACTIONS = [
    Command("goto", url="/"),
    Command("click", role="textbox", name="Email", selector="#email"),
    Command("fill", role="textbox", name="Email", value="demo@shop.test", selector="#email"),
    Command("click", role="textbox", name="Password", selector="#password"),
    Command("fill", role="textbox", name="Password", value="hunter2", selector="#password"),
    Command("click", role="button", text="Sign in", selector="#signin"),
    Command("click", role="searchbox", name="Search products", selector="#search"),
    Command("fill", role="searchbox", name="Search products", value="wireless headphones", selector="#search"),
    Command("click", role="button", text="Search", selector="#search-btn"),
    Command("click", role="button", text="Add to cart", selector="#add"),
    Command("click", role="link", text="Checkout", selector="#checkout"),
    Command("click", role="button", text="Place order", selector="#place-order"),
    Command("assertVisible", text="Order confirmed", selector=".confirmation"),
]


class PlaywrightRecorder:
    def __init__(self, session_id: str, name: str, goal: str, base_url: str | None = None, headless: bool = True, page=None, object_store=None):
        self.session_id = session_id
        self.name = name
        self.goal = goal
        self.base_url = base_url
        self.headless = headless
        self.timeout_ms = DEFAULT_TIMEOUT_MS
        self._page = page
        self.object_store = object_store

    def record(self, actions: list[Command]) -> dict:
        if self._page is not None:
            return self._record_with_page(self._page, actions)
        return self._record_live(actions)

    def _record_live(self, actions: list[Command]) -> dict:  # pragma: no cover - needs a browser
        from playwright.sync_api import sync_playwright

        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=self.headless)
            page = browser.new_page()
            try:
                return self._record_with_page(page, actions)
            finally:
                browser.close()

    def _record_with_page(self, page, actions: list[Command]) -> dict:
        net: list = []
        attach_network(page, net)
        events: list = []
        step = 0
        url = self.base_url
        for a in actions:
            seen = len(net)
            execute_command(page, a, self.base_url, self.timeout_ms)
            if a.kind == "goto":
                url = absolutize(a.url, self.base_url) or url
            events.append(_event_for(a, step, url, self.session_id))
            if self.object_store is not None and hasattr(page, "screenshot"):
                try:
                    key = f"shot/{self.session_id}/{step}.png"
                    self.object_store.put(key, page.screenshot(), "image/png")
                    events[-1]["screenshotKey"] = key
                except Exception:
                    pass
            step += 1
            for nrec in net[seen:]:  # network triggered by this action
                events.append({
                    "sessionId": self.session_id, "stepIndex": step, "timestamp": _now(),
                    "url": url, "eventType": "network", "network": nrec,
                })
                step += 1
        return {"sessionId": self.session_id, "name": self.name, "goal": self.goal, "events": events}
