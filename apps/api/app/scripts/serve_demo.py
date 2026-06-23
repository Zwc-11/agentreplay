"""Serve the demo-shop app + a fake JSON API so Playwright can drive it live.

    python -m app.scripts.serve_demo            # http://localhost:8080
    python -m app.scripts.serve_demo 9000       # custom port

Add ?broken=1 to the page URL to make POST /api/checkout return 500.
"""
from __future__ import annotations

import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

_APP = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "examples", "demo-shop", "app", "index.html")
)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):  # quiet
        pass

    def _send(self, status: int, body: bytes, ctype: str):
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlparse(self.path).path
        if path in ("/", "/index.html"):
            with open(_APP, "rb") as f:
                return self._send(200, f.read(), "text/html; charset=utf-8")
        if path.startswith("/api/"):
            return self._send(200, json.dumps({"ok": True}).encode(), "application/json")
        return self._send(404, b"not found", "text/plain")

    def do_POST(self):
        q = urlparse(self.path)
        if q.path == "/api/checkout" and "fail=1" in (q.query or ""):
            return self._send(500, json.dumps({"error": "checkout failed"}).encode(), "application/json")
        return self._send(200, json.dumps({"ok": True}).encode(), "application/json")


def main() -> None:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"demo-shop on http://127.0.0.1:{port}  (append ?broken=1 to break checkout)")
    server.serve_forever()


if __name__ == "__main__":
    main()
