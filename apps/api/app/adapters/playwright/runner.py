"""Execute workflow commands in a real browser via Playwright.

The browser is abstracted behind a tiny Page-like interface (get_by_role,
get_by_text, locator, goto, on), so command->Playwright translation and failure
handling are unit-tested with a fake page. A live run lazily imports playwright
and drives Chromium.
"""
from __future__ import annotations

from urllib.parse import urlparse

from app.core.agent import AgentRunResult, WorkflowTask
from app.core.graph.model import Command

DEFAULT_TIMEOUT_MS = 5000


def response_path(url: str) -> str:
    u = urlparse(url)
    return u.path + (f"?{u.query}" if u.query else "")


def absolutize(url: str | None, base_url: str | None) -> str | None:
    if url and base_url and url.startswith("/"):
        return base_url.rstrip("/") + url
    return url


def locator_for(page, c: Command):
    name = c.name or c.text
    if c.role and name:
        return page.get_by_role(c.role, name=name)
    if c.text:
        return page.get_by_text(c.text)
    return page.locator(c.selector)


def execute_command(page, c: Command, base_url: str | None = None, timeout_ms: int = DEFAULT_TIMEOUT_MS) -> None:
    """Run a single command against a Page. Raises on a live failure."""
    if c.kind == "goto":
        page.goto(absolutize(c.url, base_url))
        return
    loc = locator_for(page, c)
    if c.kind == "click":
        loc.click(timeout=timeout_ms)
    elif c.kind == "fill":
        loc.fill(c.value or "", timeout=timeout_ms)
    elif c.kind == "assertVisible":
        if not loc.is_visible():
            raise RuntimeError("element not visible")


def attach_network(page, sink: list) -> None:
    """Record response status/path into `sink` when the page exposes `.on`."""
    if hasattr(page, "on"):
        page.on(
            "response",
            lambda r: sink.append(
                {"method": r.request.method, "path": response_path(r.url), "status": r.status, "latencyMs": 0}
            ),
        )


class PlaywrightAgentDriver:
    name = "playwright"

    def __init__(self, base_url: str | None = None, headless: bool = True, timeout_ms: int = DEFAULT_TIMEOUT_MS, page=None):
        self.base_url = base_url
        self.headless = headless
        self.timeout_ms = timeout_ms
        self._page = page  # inject a Page-like object for tests

    def run(self, task: WorkflowTask) -> AgentRunResult:
        if self._page is not None:
            return self._run_with_page(self._page, task)
        return self._run_live(task)

    def _run_live(self, task: WorkflowTask) -> AgentRunResult:  # pragma: no cover - needs a browser
        from playwright.sync_api import sync_playwright

        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=self.headless)
            page = browser.new_page()
            try:
                return self._run_with_page(page, task)
            finally:
                browser.close()

    def _run_with_page(self, page, task: WorkflowTask) -> AgentRunResult:
        network: list = []
        attach_network(page, network)
        executed: list = []
        error = None
        for cmd in task.human_commands:
            try:
                execute_command(page, cmd, self.base_url, self.timeout_ms)
                executed.append(cmd)
            except Exception as e:  # noqa: BLE001 - a live failure is a real signal, not a crash
                error = f"step {len(executed) + 1} ({cmd.kind}): {e}"
                break
        success = len(executed) == len(task.human_commands)
        return AgentRunResult(self.name, success=success, commands=executed, network=list(network), error=error)
