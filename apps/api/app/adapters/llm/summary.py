"""Generate a human-readable failure summary + a ready-to-file GitHub issue.

Heuristic + deterministic by default (no key needed). When a DeepSeek client is
provided, the thinking model refines the root-cause narrative; the structured
root-cause logic stays here so it remains testable and never depends on the LLM.
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


def _refine_with_llm(client, goal, expected, actual, category, metrics) -> dict | None:
    """Ask DeepSeek to write a crisp root cause. Returns None on any failure."""
    try:
        facts = (
            f"Goal: {goal}\n"
            f"Expected action: {_describe(expected)}\n"
            f"Agent's action: {_describe(actual)}\n"
            f"Failure category: {category}\n"
            f"Step accuracy: {round(metrics['step_accuracy'] * 100)}%\n"
            f"Wrong actions: {metrics['wrong_click_count']}\n"
            f"Recovered: {'yes' if metrics['recovered'] else 'no'}"
        )
        messages = [
            {
                "role": "system",
                "content": "You analyze why a browser agent diverged from the correct workflow. In 2-3 sentences, give the concrete root cause and one prevention tip. No preamble.",
            },
            {"role": "user", "content": facts},
        ]
        out = client.complete(messages)
        content = (out.get("content") or "").strip()
        return (
            {"summary": content, "reasoningAvailable": bool(out.get("reasoning"))}
            if content
            else None
        )
    except Exception:
        return None


def generate_summary(
    graph,
    human: list,
    agent: list,
    metrics: dict,
    network_events=None,
    generated_test: str = "",
    goal: str = "the workflow",
    client=None,
) -> dict:
    div = metrics["divergence_step"]
    steps = len(human)

    if div is None and metrics["task_success"]:
        return {
            "category": None,
            "summary": f"Agent completed {goal}, matching the human path on all {steps} steps. Task succeeded.",
            "rootCause": None,
            "githubIssue": None,
            "model": None,
        }

    expected = human[div] if div is not None and div < len(human) else None
    actual = agent[div] if div is not None and div < len(agent) else None
    category = metrics["failure_category"]
    note = _CATEGORY_NOTE.get(category, "")

    base_summary = (
        f"The agent diverged at step {div + 1} of {steps}. "
        f"It was expected to {_describe(expected)}, but instead chose to {_describe(actual)}. {note}"
    )
    pct = round(metrics["step_accuracy"] * 100)
    metrics_line = (
        f"Step accuracy {pct}%, {metrics['wrong_click_count']} wrong action(s); "
        f"recovered: {'yes' if metrics['recovered'] else 'no'}."
    )

    summary_text = f"{base_summary} {metrics_line}"
    root_cause = note
    model_used = None

    refined = (
        _refine_with_llm(client, goal, expected, actual, category, metrics)
        if client is not None
        else None
    )
    if refined:
        summary_text = f"{refined['summary']} ({metrics_line})"
        root_cause = refined["summary"]
        model_used = "deepseek"

    issue_body = (
        f"## Agent divergence in {goal}\n\n"
        f"**Category:** {category}\n\n"
        f"**First divergence:** step {div + 1} of {steps}\n\n"
        f"- Expected: {_describe(expected)}\n"
        f"- Actual: {_describe(actual)}\n\n"
        f"{summary_text}\n\n"
        f"### Reproduce with the generated Playwright test\n\n"
        f"```ts\n{generated_test}```\n"
    )

    return {
        "category": category,
        "summary": summary_text,
        "rootCause": root_cause,
        "githubIssue": {
            "title": f"Agent diverged at step {div + 1} ({category}) in {goal}",
            "body": issue_body,
        },
        "model": model_used,
    }
