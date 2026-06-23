"""Object storage for screenshots & DOM snapshots (referenced by key in events).

Filesystem-backed by default (STORAGE_DIR); the same interface fronts S3/R2
later. Keys are sanitised to prevent path traversal.
"""
from __future__ import annotations

import os
from typing import Optional, Protocol

_CONTENT_TYPES = {
    ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
    ".webp": "image/webp", ".json": "application/json", ".html": "text/html",
}


class ObjectStore(Protocol):
    def put(self, key: str, data: bytes, content_type: str = "application/octet-stream") -> str: ...
    def get(self, key: str) -> Optional[tuple[bytes, str]]: ...
    def exists(self, key: str) -> bool: ...


def _safe_rel(key: str) -> str:
    norm = key.replace("\\", "/").lstrip("/")
    parts = [p for p in norm.split("/") if p not in ("", ".")]
    if any(p == ".." for p in parts):
        raise ValueError(f"invalid object key: {key!r}")
    return "/".join(parts)


class FilesystemObjectStore:
    def __init__(self, base_dir: str):
        self.base = os.path.abspath(base_dir)
        os.makedirs(self.base, exist_ok=True)

    def _path(self, key: str) -> str:
        p = os.path.abspath(os.path.join(self.base, _safe_rel(key)))
        if p != self.base and not p.startswith(self.base + os.sep):
            raise ValueError(f"invalid object key: {key!r}")
        return p

    def put(self, key: str, data: bytes, content_type: str = "application/octet-stream") -> str:
        p = self._path(key)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "wb") as f:
            f.write(data)
        return key

    def get(self, key: str) -> Optional[tuple[bytes, str]]:
        try:
            p = self._path(key)
        except ValueError:
            return None
        if not os.path.isfile(p):
            return None
        ct = _CONTENT_TYPES.get(os.path.splitext(p)[1].lower(), "application/octet-stream")
        with open(p, "rb") as f:
            return f.read(), ct

    def exists(self, key: str) -> bool:
        try:
            return os.path.isfile(self._path(key))
        except ValueError:
            return False


_default: Optional[FilesystemObjectStore] = None


def get_object_store() -> FilesystemObjectStore:
    global _default
    if _default is None:
        from app.config import settings

        _default = FilesystemObjectStore(settings.storage_dir)
    return _default
