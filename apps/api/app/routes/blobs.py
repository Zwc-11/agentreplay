from fastapi import APIRouter, HTTPException, Response

from app.adapters.storage.objects import get_object_store

router = APIRouter(tags=["blobs"])


@router.get("/blobs/{key:path}")
def get_blob(key: str) -> Response:
    """Serve a stored screenshot / DOM snapshot by key (404 if absent)."""
    obj = get_object_store().get(key)
    if obj is None:
        raise HTTPException(404, "blob not found")
    data, content_type = obj
    return Response(content=data, media_type=content_type)
