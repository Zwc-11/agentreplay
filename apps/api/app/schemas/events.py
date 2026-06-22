from typing import Literal, Optional

from pydantic import BaseModel, Field

EventType = Literal["click", "input", "navigation", "network", "assertion", "error"]


class Target(BaseModel):
    selector: str
    role: Optional[str] = None
    label: Optional[str] = None
    text: Optional[str] = None
    bbox: Optional[dict] = None


class Network(BaseModel):
    method: str
    path: str
    status: int
    latencyMs: int


class BrowserEvent(BaseModel):
    sessionId: str
    stepIndex: int
    timestamp: str
    eventType: EventType
    url: str
    target: Optional[Target] = None
    network: Optional[Network] = None
    screenshotKey: Optional[str] = None
    domSnapshotKey: Optional[str] = None
    payload: Optional[dict] = None


class EventBatch(BaseModel):
    events: list[BrowserEvent]


class RecordingImport(BaseModel):
    sessionId: str
    name: str = "Imported workflow"
    goal: str = "the workflow"
    workflowId: Optional[str] = None
    events: list[BrowserEvent] = Field(min_length=1)
