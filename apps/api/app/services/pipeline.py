"""Application orchestration: ingest -> compile -> run -> evaluate -> summarize."""

from __future__ import annotations

import uuid

from app.adapters.llm.deepseek import get_default_client
from app.adapters.llm.summary import generate_summary
from app.adapters.playwright.drivers import get_driver
from app.adapters.playwright.generator import generate_test
from app.core.agent import WorkflowTask
from app.core.evaluation.metrics import compute_metrics
from app.core.graph.compare import build_comparison
from app.core.replay.reconstruct import reconstruct_at
from app.core.workflow.compiler import compile_graph


def ingest(store, session_id: str, name: str, events: list):
    store.save_session(session_id, name)
    store.save_events(session_id, events)
    return len(events)


def compile_session(store, session_id: str, graph_id: str | None = None):
    events = store.load_events(session_id)
    graph = compile_graph(events, session_id, graph_id=graph_id)
    store.save_graph(graph, session_id)
    return graph


_UNSET = object()


def run_agent(
    store, workflow_id: str, driver_name: str = "divergent", goal: str = "the workflow", client=_UNSET
) -> dict:
    graph = store.get_graph(workflow_id)
    if graph is None:
        raise ValueError(f"unknown workflow: {workflow_id}")

    human = graph.human_commands()
    session_id = store.session_for(workflow_id)
    events = store.load_events(session_id)
    network_events = [
        e["network"] for e in events if e["eventType"] == "network" and e.get("network")
    ]
    start_url = next((c.url for c in human if c.kind == "goto"), None)

    task = WorkflowTask(workflow_id, goal, start_url, human)
    result = get_driver(driver_name).run(task)
    if getattr(result, "network", None):
        network_events = result.network  # live observations override the recording

    last_step = max((e["stepIndex"] for e in events), default=0)
    snap = reconstruct_at(events, last_step)
    metrics = compute_metrics(
        human, result.commands, result.success, network_events, snap["replayLatencyMs"]
    )
    comparison = build_comparison(graph, result.commands)
    test = generate_test(graph, test_name=goal)
    if client is _UNSET:
        client = get_default_client()
    summary = generate_summary(
        graph,
        human,
        result.commands,
        metrics,
        network_events,
        generated_test=test,
        goal=goal,
        client=client,
    )

    run = {
        "id": str(uuid.uuid4()),
        "workflowId": workflow_id,
        "driver": driver_name,
        "status": "completed",
        "success": result.success,
        "agentCommands": [c.to_dict() for c in result.commands],
        "comparison": comparison,
        "metrics": metrics,
        "summary": summary,
        "generatedTest": test,
        "llmEnabled": client is not None,
    }
    store.save_run(run)
    return run
