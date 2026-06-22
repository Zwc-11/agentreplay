"""Rebuild the browser state at step N by folding the event log (event sourcing)."""
from __future__ import annotations

import time


def reconstruct_at(events: list[dict], step_index: int) -> dict:
    t0 = time.perf_counter()
    ev = sorted(events, key=lambda e: e["stepIndex"])
    url = last_action = screenshot = dom = None
    network: list = []
    console: list = []

    for e in ev:
        if e["stepIndex"] > step_index:
            break
        if e.get("url"):
            url = e["url"]
        if e["eventType"] == "network" and e.get("network"):
            network.append(e["network"])
        if e.get("screenshotKey"):
            screenshot = e["screenshotKey"]
        if e.get("domSnapshotKey"):
            dom = e["domSnapshotKey"]
        if e["eventType"] in ("click", "input", "assertion"):
            last_action = e
        msg = (e.get("payload") or {}).get("console")
        if msg:
            console.append(msg)

    return {
        "url": url,
        "stepIndex": step_index,
        "lastAction": last_action,
        "network": network,
        "console": console,
        "screenshotKey": screenshot,
        "domSnapshotKey": dom,
        "replayLatencyMs": int((time.perf_counter() - t0) * 1000),
    }
