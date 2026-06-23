from fastapi import APIRouter, Query

from app import state
from app.services.benchmark import DEFAULT_DRIVERS, run_benchmark

router = APIRouter(tags=["benchmark"])


@router.get("/benchmark")
def benchmark(drivers: str = Query(",".join(DEFAULT_DRIVERS))) -> dict:
    """Run every selected driver across every workflow and return aggregate metrics."""
    state.seed()
    names = [d.strip() for d in drivers.split(",") if d.strip()]
    return run_benchmark(state.store, drivers=names, goal_for=state.goal_for_workflow)
