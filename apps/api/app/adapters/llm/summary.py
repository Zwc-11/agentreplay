"""Generate a human-readable failure summary + a ready-to-file GitHub issue.

Deterministic and dependency-free by default. If an LLM is configured it could
refine the prose, but the root-cause logic stays here so it is testable.
"""
from __future__ import annotations

from app.core.graph.model import Command

_CATEGORY_NOTE = {
    "network-caused": "A failing network response (HTTP >= 400) around this step left the intended control unavailable, so the agent could not proceed correctly.",
    "stale-state": "The agent repeated its previous action, acting before the page state had settled.",
    "missing-recovery": "The agent ran out of actions before reaching the goal and never recovered to the human path.",
    "wrong-element": "The agent selected a lookalike or incorrect element instead of the intended control.",
    "assertion-failed": "An expected element was not visible at this point in the workflow.",
}


def _describe(c: Command | None) -> str:
    if c is None:
        return "take no action"
    target = c.name or c.text or c.selector or "an element"
    if c.kind == "goto":
        return f"navigate to {c.url}"
    if c.kind == "fill":
        return f'fill the "{target}" field'
    if c.kind == "click":
        return f'click "{target}"'
    if c.kind == "assertVisible":
        return f'confirm "{target}" is visible'
    return c.kind


def generate_summary(graph, human: list, agent: list, metrics: dict, network_events=None, generated_test: str = "", goal: str = "the workflow") -> dict:
    div = metrics["divergence_step"]
    steps = len(human)

    if div is None and metrics["task_success"]:
        return {
            "category": None,
            "summary": f"Agent completed {goal}, matching the human path on all {steps} steps. Task succeeded.",
            "rootCause": None,
            "githubIssue": None,
        }

    expected = human[div] if div is not None and div < len(human) else None
    actual = agent[div] if div is not None and div < len(agent) else None
    category = metrics["failure_category"]
    note = _CATEGORY_NOTE.get(category, "")

    summary = (
        f"The agent diverged at step {div + 1} of {steps}. "
        f"It was expected to {_describe(expected)}, but instead chose to {_describe(actual)}. {note}"
    )
    pct = round(metrics["step_accuracy"] * 100)
    metrics_line = (
        f"Step accuracy {pct}%, {metrics['wrong_click_count']} wrong action(s); "
        f"recovered: {'yes' if metrics['recovered'] else 'no'}."
    )

    issue_body = (
        f"## Agent divergence in {goal}\n\n"
        f"**Category:** {category}\n\n"
        f"**First divergence:** step {div + 1} of {steps}\n\n"
        f"- Expected: {_describe(expected)}\n"
        f"- Actual: {_describe(actual)}\n\n"
        f"{note}\n\n"
        f"**Metrics:** {metrics_line}\n\n"
        f"### Reproduce with the generated Playwright test\n\n"
        f"```ts\n{generated_test}```\n"
    )

    return {
        "category": category,
        "summary": f"{summary} {metrics_line}",
        "rootCause": note,
        "githubIssue": {
            "title": f"Agent diverged at step {div + 1} ({category}) in {goal}",
            "body": issue_body,
        },
    }
