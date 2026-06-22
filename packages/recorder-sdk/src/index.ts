import type { BrowserEvent } from "@agentreplay/shared-types";

export type RawCapture = Omit<BrowserEvent, "sessionId" | "stepIndex">;
export type RecorderOptions = { sessionId: string; ingestUrl: string; apiKey?: string; batchSize?: number };

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
  private cleanup: Array<() => void> = [];
  private originalFetch: typeof fetch | undefined;
  private originalPushState: History["pushState"] | undefined;
  private originalReplaceState: History["replaceState"] | undefined;

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
        const url = new URL(this.opts.ingestUrl);
        if (!url.searchParams.has("sessionId")) url.searchParams.set("sessionId", this.opts.sessionId);
        await fetch(url.toString(), {
          method: "POST",
          headers: {
            "content-type": "application/json",
            ...(this.opts.apiKey ? { "x-api-key": this.opts.apiKey } : {}),
          },
          body: JSON.stringify({ events: batch }),
        });
      } catch {
        /* offline; events remain captured in `flushed` */
      }
    }
  }

  start(): void {
    if (typeof window === "undefined" || typeof document === "undefined") return;
    this.stopListening();

    this.capture({ timestamp: now(), eventType: "navigation", url: window.location.href });

    const onClick = (event: MouseEvent) => {
      const target = targetFor(event.target);
      if (!target) return;
      this.capture({ timestamp: now(), eventType: "click", url: window.location.href, target });
    };
    document.addEventListener("click", onClick, true);
    this.cleanup.push(() => document.removeEventListener("click", onClick, true));

    const onInput = (event: Event) => {
      const target = targetFor(event.target);
      if (!target) return;
      const value = valueFor(event.target);
      this.capture({
        timestamp: now(),
        eventType: "input",
        url: window.location.href,
        target,
        payload: value == null ? undefined : { value },
      });
    };
    document.addEventListener("input", onInput, true);
    document.addEventListener("change", onInput, true);
    this.cleanup.push(() => {
      document.removeEventListener("input", onInput, true);
      document.removeEventListener("change", onInput, true);
    });

    const onError = (event: ErrorEvent) => {
      this.capture({
        timestamp: now(),
        eventType: "error",
        url: window.location.href,
        payload: { message: event.message, source: event.filename },
      });
    };
    window.addEventListener("error", onError);
    this.cleanup.push(() => window.removeEventListener("error", onError));

    this.patchNavigation();
    this.patchFetch();
  }

  stop(): void {
    this.stopListening();
    void this.flush();
  }

  exportRecording(name = "Recorded workflow", goal = "the workflow") {
    return {
      sessionId: this.opts.sessionId,
      name,
      goal,
      events: [...this.flushed.flat(), ...this.buffer],
    };
  }

  private stopListening(): void {
    while (this.cleanup.length) this.cleanup.pop()?.();
    if (this.originalFetch) {
      window.fetch = this.originalFetch;
      this.originalFetch = undefined;
    }
    if (this.originalPushState) {
      history.pushState = this.originalPushState;
      this.originalPushState = undefined;
    }
    if (this.originalReplaceState) {
      history.replaceState = this.originalReplaceState;
      this.originalReplaceState = undefined;
    }
  }

  private patchNavigation(): void {
    this.originalPushState = history.pushState;
    this.originalReplaceState = history.replaceState;
    const recordNavigation = () => {
      queueMicrotask(() => {
        this.capture({ timestamp: now(), eventType: "navigation", url: window.location.href });
      });
    };

    history.pushState = ((...args: Parameters<History["pushState"]>) => {
      const result = this.originalPushState?.apply(history, args);
      recordNavigation();
      return result;
    }) as History["pushState"];

    history.replaceState = ((...args: Parameters<History["replaceState"]>) => {
      const result = this.originalReplaceState?.apply(history, args);
      recordNavigation();
      return result;
    }) as History["replaceState"];

    window.addEventListener("popstate", recordNavigation);
    this.cleanup.push(() => window.removeEventListener("popstate", recordNavigation));
  }

  private patchFetch(): void {
    if (typeof fetch !== "function") return;
    this.originalFetch = window.fetch.bind(window);
    window.fetch = (async (input: RequestInfo | URL, init?: RequestInit) => {
      const started = performance.now();
      const method = methodFor(input, init);
      const path = pathFor(input);
      try {
        const response = await this.originalFetch!(input, init);
        this.capture({
          timestamp: now(),
          eventType: "network",
          url: window.location.href,
          network: {
            method,
            path,
            status: response.status,
            latencyMs: Math.round(performance.now() - started),
          },
        });
        return response;
      } catch (error) {
        this.capture({
          timestamp: now(),
          eventType: "error",
          url: window.location.href,
          payload: { message: error instanceof Error ? error.message : String(error), path },
        });
        throw error;
      }
    }) as typeof fetch;
  }
}

function now(): string {
  return new Date().toISOString();
}

function targetFor(value: EventTarget | null): BrowserEvent["target"] | undefined {
  if (!(value instanceof Element)) return undefined;
  const rect = value.getBoundingClientRect();
  const text = textFor(value);
  return {
    selector: selectorFor(value),
    role: value.getAttribute("role") ?? roleFor(value),
    label: labelFor(value),
    text,
    bbox: {
      x: Math.round(rect.x),
      y: Math.round(rect.y),
      width: Math.round(rect.width),
      height: Math.round(rect.height),
    },
  };
}

function selectorFor(element: Element): string {
  if (element.id) return `#${cssEscape(element.id)}`;
  const testId = element.getAttribute("data-testid");
  if (testId) return `[data-testid="${cssEscape(testId)}"]`;
  const name = element.getAttribute("name");
  if (name) return `${element.tagName.toLowerCase()}[name="${cssEscape(name)}"]`;
  const classes = [...element.classList].slice(0, 2).map((c) => `.${cssEscape(c)}`).join("");
  return `${element.tagName.toLowerCase()}${classes}`;
}

function cssEscape(value: string): string {
  if (typeof CSS !== "undefined" && CSS.escape) return CSS.escape(value);
  return value.replace(/["\\]/g, "\\$&");
}

function roleFor(element: Element): string | undefined {
  const tag = element.tagName.toLowerCase();
  if (tag === "button") return "button";
  if (tag === "a") return "link";
  if (tag === "select") return "combobox";
  if (tag === "textarea") return "textbox";
  if (tag === "input") {
    const type = (element as HTMLInputElement).type;
    if (type === "search") return "searchbox";
    if (["button", "submit", "reset"].includes(type)) return "button";
    if (["checkbox", "radio"].includes(type)) return type;
    return "textbox";
  }
  return undefined;
}

function labelFor(element: Element): string | undefined {
  const aria = element.getAttribute("aria-label");
  if (aria) return aria.trim();
  if (element.id) {
    const label = document.querySelector(`label[for="${cssEscape(element.id)}"]`);
    if (label?.textContent) return label.textContent.trim();
  }
  const wrappingLabel = element.closest("label");
  if (wrappingLabel?.textContent) return wrappingLabel.textContent.trim();
  return undefined;
}

function textFor(element: Element): string | undefined {
  if (element instanceof HTMLInputElement || element instanceof HTMLTextAreaElement) return undefined;
  const text = element.textContent?.trim().replace(/\s+/g, " ");
  return text || undefined;
}

function valueFor(target: EventTarget | null): string | undefined {
  if (target instanceof HTMLInputElement) return target.value;
  if (target instanceof HTMLTextAreaElement) return target.value;
  if (target instanceof HTMLSelectElement) return target.value;
  return undefined;
}

function methodFor(input: RequestInfo | URL, init?: RequestInit): string {
  if (init?.method) return init.method.toUpperCase();
  if (input instanceof Request) return input.method.toUpperCase();
  return "GET";
}

function pathFor(input: RequestInfo | URL): string {
  const raw = input instanceof Request ? input.url : String(input);
  try {
    const url = new URL(raw, window.location.href);
    return `${url.pathname}${url.search}`;
  } catch {
    return raw;
  }
}
