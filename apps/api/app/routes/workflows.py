from fastapi import APIRouter, HTTPException, Query

from app import state
from app.adapters.playwright.generator import generate_test
from app.core.replay.reconstruct import reconstruct_at
from app.services.pipeline import run_agent

router = APIRouter(tags=["workflows"])


@router.get("/workflows")
def list_workflows() -> dict:
    state.seed()
    return {"workflows": state.store.list_workflows()}


@router.get("/demo")
def demo() -> dict:
    """One-shot payload for the dashboard's demo mode: the workflow + a divergent run."""
    state.seed()
    graph = state.store.get_graph(state.WORKFLOW_ID)
    run = run_agent(state.store, state.WORKFLOW_ID, "divergent", goal="complete a checkout")
    return {"workflow": graph.to_dict(), "run": run}


@router.get("/workflows/{workflow_id}/graph")
def get_graph(workflow_id: str) -> dict:
    state.seed()
    graph = state.store.get_graph(workflow_id)
    if graph is None:
        raise HTTPException(404, "workflow not found")
    return graph.to_dict()


@router.get("/workflows/{workflow_id}/test")
def export_test(workflow_id: str) -> dict:
    state.seed()
    graph = state.store.get_graph(workflow_id)
    if graph is None:
        raise HTTPException(404, "workflow not found")
    return {"id": workflow_id, "test": generate_test(graph)}


@router.get("/workflows/{workflow_id}/replay")
def replay(workflow_id: str, step: int = Query(0, ge=0)) -> dict:
    state.seed()
    graph = state.store.get_graph(workflow_id)
    if graph is None:
        raise HTTPException(404, "workflow not found")
    session_id = state.store.graph_session[workflow_id]
    return reconstruct_at(state.store.load_events(session_id), step)
