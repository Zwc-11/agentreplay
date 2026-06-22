import test from "node:test";
import assert from "node:assert/strict";
import { Recorder, buildEvent } from "../src/index.ts";

test("buildEvent stamps sessionId + stepIndex", () => {
  const e = buildEvent({ timestamp: "t", eventType: "click", url: "/x" } as any, "sess", 4);
  assert.equal(e.sessionId, "sess");
  assert.equal(e.stepIndex, 4);
  assert.equal(e.eventType, "click");
});

test("capture auto-increments steps and flushes a full batch", async () => {
  const r = new Recorder({ sessionId: "s", ingestUrl: "memory://x", apiKey: "k", batchSize: 2 });
  r.capture({ timestamp: "t", eventType: "click", url: "/a" } as any);
  assert.equal(r.pending(), 1);
  r.capture({ timestamp: "t", eventType: "input", url: "/a" } as any); // hits batchSize -> auto flush
  await new Promise((res) => setTimeout(res, 0));
  assert.equal(r.pending(), 0);
  assert.equal(r.batches().length, 1);
  assert.equal(r.batches()[0].length, 2);
  assert.equal(r.batches()[0][1].stepIndex, 1);
});
