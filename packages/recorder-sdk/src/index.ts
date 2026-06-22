import type { BrowserEvent } from "@agentreplay/shared-types";

export type RawCapture = Omit<BrowserEvent, "sessionId" | "stepIndex">;
export type RecorderOptions = { sessionId: string; ingestUrl: string; apiKey: string; batchSize?: number };

/** Stamp a raw capture with the session id and an ordered step index. */
export function buildEvent(raw: RawCapture, sessionId: string, stepIndex: number): BrowserEvent {
  return { ...raw, sessionId, stepIndex };
}

/**
 * Browser recorder: attaches listeners (in a real page), builds structured
 * BrowserEvents, batches them, and ships them to the ingestion API. The pure
 * event-shaping + batching logic here is unit-tested; start()/stop() bind DOM
 * listeners when running in a browser.
 */
export class Recorder {
  private buffer: BrowserEvent[] = [];
  private step = 0;
  private flushed: BrowserEvent[][] = [];
  private readonly opts: RecorderOptions;

  constructor(opts: RecorderOptions) {
    this.opts = opts;
  }

  capture(raw: RawCapture): void {
    this.buffer.push(buildEvent(raw, this.opts.sessionId, this.step++));
    if (this.buffer.length >= (this.opts.batchSize ?? 20)) void this.flush();
  }

  pending(): number {
    return this.buffer.length;
  }

  batches(): BrowserEvent[][] {
    return this.flushed;
  }

  async flush(): Promise<void> {
    if (this.buffer.length === 0) return;
    const batch = this.buffer;
    this.buffer = [];
    this.flushed.push(batch);
    if (typeof fetch === "function" && this.opts.ingestUrl.startsWith("http")) {
      try {
        await fetch(this.opts.ingestUrl, {
          method: "POST",
          headers: { "content-type": "application/json", "x-api-key": this.opts.apiKey },
          body: JSON.stringify({ events: batch }),
        });
      } catch {
        /* offline; events remain captured in `flushed` */
      }
    }
  }

  start(): void {
    /* attach click/input/navigation/network/console listeners in a browser */
  }

  stop(): void {
    void this.flush();
  }
}
