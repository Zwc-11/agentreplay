"""Workflow compiler: events -> normalized -> states -> actions -> graph.

Pure domain logic. Accepts plain event dicts (the canonical BrowserEvent JSON),
so it depends on no framework or DB.
"""
from __future__ import annotations

import uuid
from urllib.parse import urlparse

from app.core.graph.model import Command, Edge, Graph, Node


def _route(url: str | None) -> str:
    if not url:
        return "page"
    p = urlparse(url)
    segs = [s for s in p.path.split("/") if s]
    return segs[-1] if segs else (p.netloc or "home")


def normalize(events: list[dict]) -> list[dict]:
    """Sort by step, coalesce consecutive input bursts on the same target."""
    ev = sorted(events, key=lambda e: e["stepIndex"])
    out: list[dict] = []
    for e in ev:
        same_input = (
            e["eventType"] == "input"
            and out
            and out[-1]["eventType"] == "input"
            and (out[-1].get("target") or {}).get("selector") == (e.get("target") or {}).get("selector")
        )
        if same_input:
            out[-1] = e  # keep the latest (final typed value)
        else:
            out.append(e)
    return out


def _command_for(e: dict) -> Command | None:
    t = e.get("target") or {}
    et = e["eventType"]
    if et == "navigation":
        return Command("goto", url=e.get("url"))
    if et == "click":
        return Command("click", selector=t.get("selector"), role=t.get("role"), name=t.get("label"), text=t.get("text"))
    if et == "input":
        value = (e.get("payload") or {}).get("value") or t.get("text") or ""
        return Command("fill", selector=t.get("selector"), role=t.get("role"), name=t.get("label"), value=value)
    if et == "assertion":
        return Command("assertVisible", selector=t.get("selector"), text=t.get("text"), name=t.get("label"))
    return None


def _state_label(e: dict, route: str) -> str:
    t = e.get("target") or {}
    name = t.get("label") or t.get("text") or ""
    et = e["eventType"]
    if et == "navigation":
        return route.capitalize()
    if et == "click":
        if t.get("role") in ("textbox", "combobox", "searchbox"):
            return f"{name} focused".strip()
        return f"{name} clicked".strip() if name else "clicked"
    if et == "input":
        return f"{name} filled".strip() if name else "filled"
    if et == "assertion":
        return f"Assert: {t.get('text') or name}".strip()
    return route


def _edge_label(e: dict) -> str:
    t = e.get("target") or {}
    name = t.get("label") or t.get("text") or t.get("selector") or ""
    et = e["eventType"]
    return {
        "navigation": f"goto {e.get('url')}",
        "click": f"click {name}",
        "input": f"type {name}",
        "assertion": f"assert {t.get('text') or name}",
    }.get(et, et)


def compile_graph(events: list[dict], session_id: str, graph_id: str | None = None) -> Graph:
    ev = normalize(events)
    g = Graph(id=graph_id or str(uuid.uuid4()), session_id=session_id)
    prev: Node | None = None
    current_url: str | None = None
    si = ni = ei = 0

    for e in ev:
        et = e["eventType"]
        if et == "navigation":
            current_url = e.get("url")

        if et == "network":
            net = e.get("network") or {}
            nid = f"net{ni}"
            ni += 1
            label = f"{net.get('method', '')} {net.get('path', '')} -> {net.get('status', '')}".strip()
            g.nodes.append(Node(nid, "network", label, e["stepIndex"], url=current_url, meta={"network": net}))
            if prev is not None:
                g.edges.append(Edge(f"e{ei}", prev.id, nid, "network-dependency", label=str(net.get("status", ""))))
                ei += 1
            continue

        if et == "error":
            fid = f"fail{ni}"
            ni += 1
            msg = (e.get("payload") or {}).get("message", "Error")
            g.nodes.append(Node(fid, "failure", msg, e["stepIndex"], url=current_url))
            if prev is not None:
                g.edges.append(Edge(f"e{ei}", prev.id, fid, "divergence"))
                ei += 1
            prev = g.nodes[-1]
            continue

        # state-producing event: navigation / click / input / assertion
        cmd = _command_for(e)
        route = _route(current_url)
        sid = f"s{si}"
        si += 1
        kind = "assertion" if et == "assertion" else "page-state"
        node = Node(
            sid, kind, _state_label(e, route), e["stepIndex"], url=current_url,
            screenshot_key=e.get("screenshotKey"), dom_snapshot_key=e.get("domSnapshotKey"),
        )
        g.nodes.append(node)
        if prev is not None and cmd is not None:
            g.edges.append(Edge(f"e{ei}", prev.id, sid, "human-path", command=cmd, label=_edge_label(e)))
            ei += 1
        prev = node

    return g
