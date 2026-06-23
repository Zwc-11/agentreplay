"""Record the bundled demo-shop app live with Playwright.

    python -m app.scripts.serve_demo &                 # in one shell
    python -m app.scripts.record --url http://localhost:8080 --out live-checkout.json
"""
from __future__ import annotations

import argparse
import json

from app.adapters.playwright.recorder import CHECKOUT_ACTIONS, PlaywrightRecorder
from app.adapters.storage.objects import get_object_store


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://localhost:8080")
    ap.add_argument("--out", default="live-checkout.json")
    ap.add_argument("--session", default="live-checkout")
    args = ap.parse_args()

    rec = PlaywrightRecorder(args.session, "Live checkout", "complete a checkout", base_url=args.url, object_store=get_object_store())
    recording = rec.record(CHECKOUT_ACTIONS)
    with open(args.out, "w") as f:
        json.dump(recording, f, indent=2)
    print(f"recorded {len(recording['events'])} events -> {args.out}")


if __name__ == "__main__":
    main()
