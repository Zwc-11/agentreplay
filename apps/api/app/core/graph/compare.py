"""Build the human-vs-agent overlay: extra agent-action nodes + edges that
branch off the human path at the divergence point."""
from __future__ import annotations

from app.core.evaluation.divergence import detect_divergence
from app.core.graph.model import Command, Edge, Graph, Node


def _label(c: Command) -> str:
    target = c.name or c.text or c.selector or c.url or ""
    return f"{c.kind} {target}".strip()


def build_comparison(graph: Graph, agent_commands: list) -> dict:
    human = graph.human_commands()
    div = detect_divergence(human, agent_commands)
    states = graph.state_nodes()

    if div is None:
        return {"divergenceStep": None, "nodes": [], "edges": []}

    src = states[div] if div < len(states) else states[-1]
    nodes: list = []
    edges: list = []
    prev = src.id
    for j in range(div, len(agent_commands)):
        c = agent_commands[j]
        aid = f"a{j}"
        nodes.append(Node(aid, "agent-action", _label(c), src.step_index, url=src.url))
        edges.append(Edge(f"ae{j}", prev, aid, "divergence" if j == div else "agent-path", command=c, label=_label(c)))
        prev = aid

    return {
        "divergenceStep": div,
        "nodes": [n.to_dict() for n in nodes],
        "edges": [e.to_dict() for e in edges],
    }
