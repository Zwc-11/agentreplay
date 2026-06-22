"""Agent drivers behind one interface (strategy pattern).

Cheap/deterministic drivers first so the whole pipeline works without a real
agent or API keys. A real PlaywrightAgentDriver / LLMAgentDriver plug in later
behind the same AgentDriver port.
"""
from __future__ import annotations

import random

from app.core.agent import AgentRunResult, WorkflowTask
from app.core.graph.model import Command


class ScriptedAgentDriver:
    """Replays the recorded human steps exactly. Baseline that always succeeds."""

    name = "scripted"

    def run(self, task: WorkflowTask) -> AgentRunResult:
        return AgentRunResult(self.name, success=True, commands=list(task.human_commands))


class DivergentAgentDriver:
    """Follows the human path until `diverge_at`, then takes a wrong action.

    Models the classic browser-agent failure: clicking a lookalike/ad/wrong
    control instead of the intended one, then failing to reach the goal.
    """

    name = "divergent"

    def __init__(self, diverge_at: int | None = None, wrong: Command | None = None):
        self.diverge_at = diverge_at
        self.wrong = wrong or Command("click", selector=".promo-ad", role="link", name="Special offer")

    def run(self, task: WorkflowTask) -> AgentRunResult:
        human = task.human_commands
        at = self.diverge_at
        if at is None:
            clicks = [i for i, c in enumerate(human) if c.kind == "click"]
            at = clicks[-1] if clicks else max(0, len(human) - 1)
        at = min(at, len(human))
        commands = list(human[:at]) + [self.wrong]
        return AgentRunResult(self.name, success=False, commands=commands)


class RandomAgentDriver:
    """Deterministically (seeded) replaces one step with a random wrong click."""

    name = "random"

    def __init__(self, seed: int = 7):
        self.rng = random.Random(seed)

    def run(self, task: WorkflowTask) -> AgentRunResult:
        human = list(task.human_commands)
        if not human:
            return AgentRunResult(self.name, success=False, commands=[])
        i = self.rng.randrange(len(human))
        wrong = Command("click", selector=f".rand-{i}", role="link", name=f"Distraction {i}")
        commands = human[:i] + [wrong]
        return AgentRunResult(self.name, success=False, commands=commands)


class PlaywrightAgentDriver:
    """Placeholder for real browser execution via Playwright (drives a live page)."""

    name = "playwright"

    def run(self, task: WorkflowTask) -> AgentRunResult:  # pragma: no cover
        raise NotImplementedError("Wire up a real Playwright session to drive the page.")


DRIVERS = {
    ScriptedAgentDriver.name: lambda: ScriptedAgentDriver(),
    DivergentAgentDriver.name: lambda: DivergentAgentDriver(),
    RandomAgentDriver.name: lambda: RandomAgentDriver(),
}


def get_driver(name: str):
    factory = DRIVERS.get(name)
    if not factory:
        raise ValueError(f"unknown driver: {name}")
    return factory()
