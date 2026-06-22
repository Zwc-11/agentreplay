from fastapi import APIRouter, HTTPException

from app import state
from app.services.pipeline import run_agent

router = APIRouter(tags=["agent-runs"])


@router.post("/workflows/{workflow_id}/runs")
def start_run(workflow_id: str, driver: str = "divergent") -> dict:
    """Run an agent (scripted | divergent | random) and evaluate it against the human path."""
    state.seed()
    try:
        return run_agent(state.store, workflow_id, driver, goal="complete a checkout")
    except ValueError as e:
        raise HTTPException(404, str(e))


@router.get("/runs/{run_id}")
def get_run(run_id: str) -> dict:
    run = state.store.get_run(run_id)
    if run is None:
        raise HTTPException(404, "run not found")
    return run
