from fastapi import APIRouter

from app import state
from app.schemas.events import EventBatch
from app.services.pipeline import compile_session, ingest

router = APIRouter(tags=["events"])


@router.post("/events:batch")
def ingest_batch(batch: EventBatch, sessionId: str = "session", name: str = "Workflow") -> dict:
    """Validate and append a batch of BrowserEvents (idempotent per sessionId+stepIndex)."""
    events = [e.model_dump() for e in batch.events]
    accepted = ingest(state.store, sessionId, name, events)
    return {"accepted": accepted, "sessionId": sessionId}


@router.post("/sessions/{session_id}/compile")
def compile_route(session_id: str) -> dict:
    """Compile a recorded session into a workflow graph."""
    return compile_session(state.store, session_id).to_dict()
