"""Find the first step where the agent path leaves the recorded human path."""
from __future__ import annotations

from app.core.graph.model import Command


def command_key(c) -> tuple:
    """Comparable identity for a Command (object or dict)."""
    if isinstance(c, Command):
        return c.key()
    label = (c.get("name") or c.get("text") or "").strip().lower()
    return (c.get("kind"), c.get("role"), label, c.get("selector"))


def detect_divergence(human_commands: list, agent_commands: list) -> int | None:
    """Return the first index where the agent's action does not match the
    expected human action at the same step, or None if it stayed on path."""
    for i, hc in enumerate(human_commands):
        ac = agent_commands[i] if i < len(agent_commands) else None
        if ac is None or command_key(hc) != command_key(ac):
            return i
    return None
