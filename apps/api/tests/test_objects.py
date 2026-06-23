import pytest
from fastapi.testclient import TestClient

from app.adapters.storage import objects as objmod
from app.adapters.storage.objects import FilesystemObjectStore
from app.main import app

client = TestClient(app)


def test_roundtrip_and_content_type(tmp_path):
    s = FilesystemObjectStore(str(tmp_path))
    s.put("shot/demo/0.png", b"PNGDATA", "image/png")
    got = s.get("shot/demo/0.png")
    assert got == (b"PNGDATA", "image/png")
    assert s.exists("shot/demo/0.png")
    assert s.get("nope.png") is None


def test_rejects_path_traversal(tmp_path):
    s = FilesystemObjectStore(str(tmp_path))
    with pytest.raises(ValueError):
        s.put("../escape.txt", b"x")
    assert s.get("../../etc/passwd") is None


def test_blob_endpoint_serves_and_404s(tmp_path, monkeypatch):
    store = FilesystemObjectStore(str(tmp_path))
    monkeypatch.setattr(objmod, "_default", store)
    store.put("shot/x/1.png", b"PNG", "image/png")
    ok = client.get("/v1/blobs/shot/x/1.png")
    assert ok.status_code == 200 and ok.content == b"PNG"
    assert client.get("/v1/blobs/missing.png").status_code == 404
