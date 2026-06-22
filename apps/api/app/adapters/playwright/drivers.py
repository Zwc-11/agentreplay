"""Agent drivers behind one interface (strategy pattern).

Cheap/deterministic drivers first (scripted, divergent, random) so the pipeline
works with no API keys. LLMAgentDriver plugs in a real model (DeepSeek v4 Pro)
that chooses the next browser action; AgentReplay then compares its path to the
human and surfaces the first divergence.
"""

from __future__ import annotations

import json
import random

from app.core.agent import AgentRunResult, WorkflowTask
from app.core.evaluation.divergence import command_key
from app.core.graph.model import Command


class ScriptedAgentDriver:
    """Replays the recorded human steps exactly. Baseline that always succeeds."""

    name = "scripted"

    def run(self, task: WorkflowTask) -> AgentRunResult:
        return AgentRunResult(self.name, success=True, commands=list(task.human_commands))


class DivergentAgentDriver:
    """Follows the human path until the last decisive click, then takes a wrong action."""

    name = "divergent"

    def __init__(self, diverge_at: int | None = None, wrong: Command | None = None):
        self.diverge_at = diverge_at
        self.wrong = wrong or Command(
            "click", selector=".promo-ad", role="link", name="Special offer"
        )

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
        return AgentRunResult(self.name, success=False, commands=human[:i] + [wrong])


class LLMAgentDriver:
    """An LLM (DeepSeek v4 Pro thinking model) chooses the next action.

    At each state the model is shown the goal and a shuffled list of candidate
    actions - the correct next action plus distractors (e.g. a lookalike ad) -
    and must pick one. Its choices form the agent path; if it ever picks a
    distractor, that is the divergence. With no client configured it falls back
    to choosing the correct action so the pipeline still runs.
    """

    name = "llm"

    def __init__(self, client=None, distractors: list | None = None, seed: int = 13):
        self.client = client
        self.distractors = distractors or [
            Command("click", selector=".promo-ad", role="link", name="Special offer")
        ]
        self.rng = random.Random(seed)

    def run(self, task: WorkflowTask) -> AgentRunResult:
        human = task.human_commands
        commands: list = []
        for i, expected in enumerate(human):
            choice = self._choose(task, i, expected)
            commands.append(choice)
            if command_key(choice) != command_key(expected):
                break  # diverged; a real failing agent would not recover here
        success = len(commands) == len(human) and all(
            command_key(c) == command_key(h) for c, h in zip(commands, human)
        )
        return AgentRunResult(self.name, success=success, commands=commands)

    def _options(self, expected: Command) -> list:
        opts = [expected] + [d for d in self.distractors if command_key(d) != command_key(expected)]
        order = list(range(len(opts)))
        self.rng.shuffle(order)
        return [opts[j] for j in order]

    def _choose(self, task: WorkflowTask, i: int, expected: Command) -> Command:
        options = self._options(expected)
        if self.client is None:
            return expected  # graceful fallback when DeepSeek is not configured
        try:
            listing = "\n".join(f"{k}. {self._describe(o)}" for k, o in enumerate(options))
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a careful web-automation agent. Choose exactly ONE next action "
                        'that advances the task. Respond ONLY as JSON: {"choice": <number>}.'
                    ),
                },
                {
                    "role": "user",
                    "content": f"Goal: {task.goal}\nStep {i + 1}. Pick the next action:\n{listing}",
                },
            ]
            out = self.client.complete(messages, json_mode=True)
            idx = int(json.loads(out["content"])["choice"])
            return options[idx] if 0 <= idx < len(options) else expected
        except Exception:
            return expected  # never let a model hiccup crash a run

    @staticmethod
    def _describe(c: Command) -> str:
        target = c.name or c.text or c.selector or c.url or ""
        return f"{c.kind} {target}".strip()


def _llm_driver():
    from app.adapters.llm.deepseek import get_default_client

    return LLMAgentDriver(client=get_default_client())


DRIVERS = {
    ScriptedAgentDriver.name: lambda: ScriptedAgentDriver(),
    DivergentAgentDriver.name: lambda: DivergentAgentDriver(),
    RandomAgentDriver.name: lambda: RandomAgentDriver(),
    LLMAgentDriver.name: _llm_driver,
}


def get_driver(name: str):
    factory = DRIVERS.get(name)
    if not factory:
        raise ValueError(f"unknown driver: {name}")
    return factory()
