"""Agent domain types and the AgentDriver port (strategy pattern)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from app.core.graph.model import Command


@dataclass
class WorkflowTask:
    workflow_id: str
    goal: str
    start_url: str
    human_commands: list[Command] = field(default_factory=list)


@dataclass
class AgentRunResult:
    driver_name: str
    success: bool
    commands: list[Command] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "driverName": self.driver_name,
            "success": self.success,
            "commands": [c.to_dict() for c in self.commands],
        }


class AgentDriver(Protocol):
    name: str

    def run(self, task: WorkflowTask) -> AgentRunResult: ...
