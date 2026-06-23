"""End-to-end LIVE demo (needs a browser): serve the app, record it with
Playwright, then run the Playwright agent against a BROKEN variant and show
exactly where it fails live.

    pip install playwright && playwright install chromium
    python -m app.scripts.live
"""
from __future__ import annotations

import threading
import time
from http.server import ThreadingHTTPServer

from app.adapters.playwright.recorder import CHECKOUT_ACTIONS, PlaywrightRecorder
from app.adapters.playwright.runner import PlaywrightAgentDriver
from app.adapters.storage.objects import get_object_store
from app.core.agent import WorkflowTask
from app.core.evaluation.metrics import compute_metrics
from app.core.graph.model import Command
from app.core.workflow.compiler import compile_graph
from app.scripts import serve_demo


def main() -> None:
    port = 8090
    srv = ThreadingHTTPServer(("127.0.0.1", port), serve_demo.Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    time.sleep(0.3)
    base = f"http://127.0.0.1:{port}"
    print(f"serving demo-shop at {base}")

    # 1) record the happy path live
    recording = PlaywrightRecorder("live-checkout", "Live checkout", "complete a checkout", base_url=base, object_store=get_object_store()).record(CHECKOUT_ACTIONS)
    graph = compile_graph(recording["events"], recording["sessionId"], "live-checkout")
    human = graph.human_commands()
    print(f"recorded {len(recording['events'])} events -> compiled {len(graph.nodes)} nodes, {len(human)} actions")

    # 2) run the agent against the BROKEN app (checkout returns 500)
    broken_path = [Command("goto", url="/?broken=1") if c.kind == "goto" else c for c in human]
    result = PlaywrightAgentDriver(base_url=base).run(WorkflowTask("live-checkout", "complete a checkout", base, broken_path))
    metrics = compute_metrics(human, result.commands, result.success, result.network)

    print("\n=== LIVE agent run (broken checkout) ===")
    print(f"success         : {result.success}")
    print(f"executed steps  : {len(result.commands)} of {len(human)}")
    print(f"error           : {result.error}")
    ds = metrics["divergence_step"]
    print(f"divergence step : {None if ds is None else ds + 1}")
    print(f"category        : {metrics['failure_category']}  | network-caused: {metrics['network_caused_failure']}")
    srv.shutdown()


if __name__ == "__main__":
    main()
