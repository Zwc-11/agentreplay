"""Step-level metrics for an agent run, derived from aligned paths."""
from __future__ import annotations

from app.core.evaluation.divergence import command_key, detect_divergence

FailureCategory = str  # wrong-element | stale-state | network-caused | missing-recovery | assertion-failed


def classify_failure(human: list, agent: list, divergence_step: int | None, network_events: list | None) -> FailureCategory | None:
    if divergence_step is None:
        return None
    if any(int((n or {}).get("status", 0)) >= 400 for n in (network_events or [])):
        return "network-caused"
    if divergence_step >= len(agent):
        return "missing-recovery"
    expected = human[divergence_step] if divergence_step < len(human) else None
    if expected is not None and command_key(expected)[0] == "assertVisible":
        return "assertion-failed"
    # stale-state: agent repeated its previous action (acted before the state settled)
    if divergence_step > 0 and command_key(agent[divergence_step]) == command_key(agent[divergence_step - 1]):
        return "stale-state"
    return "wrong-element"


def compute_metrics(human: list, agent: list, success: bool, network_events: list | None = None, replay_latency_ms: int = 0) -> dict:
    div = detect_divergence(human, agent)
    matched = div if div is not None else min(len(human), len(agent))
    step_accuracy = round(matched / len(human), 4) if human else 0.0
    wrong_click_count = max(0, len(agent) - matched)

    recovered = False
    if div is not None and agent and human:
        recovered = command_key(agent[-1]) == command_key(human[-1])

    category = classify_failure(human, agent, div, network_events)
    return {
        "task_success": bool(success),
        "step_accuracy": step_accuracy,
        "wrong_click_count": wrong_click_count,
        "divergence_step": div,
        "recovered": recovered,
        "network_caused_failure": category == "network-caused",
        "failure_category": category,
        "replay_latency_ms": replay_latency_ms,
    }
