"""Framework-free domain model for the workflow graph.

A graph is a projection of the event log: each node is a browser state, each
edge is an action carrying a typed Command. No framework / DB / browser imports.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Literal, Optional

CommandKind = Literal["click", "fill", "goto", "assertVisible"]
NodeKind = Literal["page-state", "user-action", "agent-action", "network", "assertion", "failure"]
EdgeKind = Literal["human-path", "agent-path", "network-dependency", "divergence"]


@dataclass
class Command:
    """A typed browser action. Maps onto Playwright generation and agent execution."""

    kind: CommandKind
    selector: Optional[str] = None
    role: Optional[str] = None
    name: Optional[str] = None  # accessible name
    text: Optional[str] = None
    value: Optional[str] = None
    url: Optional[str] = None

    def key(self) -> tuple:
        """Identity used to compare agent vs human actions.

        Compares by kind + role + accessible name/text + selector. Deliberately
        ignores the typed value and raw pixel position.
        """
        label = (self.name or self.text or "").strip().lower()
        return (self.kind, self.role, label, self.selector)

    def to_dict(self) -> dict:
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class Node:
    id: str
    kind: NodeKind
    label: str
    step_index: int
    url: Optional[str] = None
    screenshot_key: Optional[str] = None
    dom_snapshot_key: Optional[str] = None
    meta: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        d: dict = {"id": self.id, "kind": self.kind, "label": self.label, "stepIndex": self.step_index}
        if self.url:
            d["url"] = self.url
        if self.screenshot_key:
            d["screenshotKey"] = self.screenshot_key
        if self.dom_snapshot_key:
            d["domSnapshotKey"] = self.dom_snapshot_key
        if self.meta:
            d["meta"] = self.meta
        return d


@dataclass
class Edge:
    id: str
    source: str
    target: str
    kind: EdgeKind
    command: Optional[Command] = None
    label: Optional[str] = None

    def to_dict(self) -> dict:
        d: dict = {"id": self.id, "source": self.source, "target": self.target, "kind": self.kind}
        if self.command:
            d["command"] = self.command.to_dict()
        if self.label:
            d["label"] = self.label
        return d


@dataclass
class Graph:
    id: str
    session_id: str
    nodes: list = field(default_factory=list)
    edges: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "sessionId": self.session_id,
            "nodes": [n.to_dict() for n in self.nodes],
            "edges": [e.to_dict() for e in self.edges],
        }

    def human_commands(self) -> list:
        """Ordered list of Commands along the recorded human path."""
        return [e.command for e in self.edges if e.kind == "human-path" and e.command]

    def state_nodes(self) -> list:
        return [n for n in self.nodes if n.kind in ("page-state", "assertion")]
