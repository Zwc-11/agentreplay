from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import state
from app.config import settings
from app.routes import agent_runs, events, health, workflows


@asynccontextmanager
async def lifespan(app: FastAPI):
    state.seed()  # load + compile the demo workflow on startup
    yield


app = FastAPI(title="AgentReplay API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(events.router, prefix="/v1")
app.include_router(workflows.router, prefix="/v1")
app.include_router(agent_runs.router, prefix="/v1")
