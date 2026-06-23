from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def index() -> dict:
    """Friendly root so visitors land somewhere useful instead of a 404."""
    return {
        "name": "AgentReplay",
        "version": "0.1.0",
        "description": "A browser workflow flight recorder for AI agents.",
        "docs": "/docs",
        "endpoints": {
            "workflows": "/v1/workflows",
            "demo": "/v1/demo",
            "benchmark": "/v1/benchmark",
            "health": "/health",
        },
        "repo": "https://github.com/Zwc-11/agentreplay",
    }


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}
