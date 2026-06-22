"""Repository port. The Postgres implementation lives in app/adapters/postgres."""
from typing import Protocol

from app.schemas.events import BrowserEvent


class WorkflowRepository(Protocol):
    def save_event(self, event: BrowserEvent) -> None: ...
    def load_session(self, session_id: str) -> list[BrowserEvent]: ...
    def save_graph(self, graph: dict) -> None: ...
