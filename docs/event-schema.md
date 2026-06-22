# Event schema

AgentReplay records **structured browser state**, not just screenshots. Every recording is an ordered stream of `BrowserEvent`s. This schema is the contract between the recorder SDK, the ingestion API, and the workflow compiler.

## `BrowserEvent`

```ts
type BrowserEvent = {
  sessionId: string;
  stepIndex: number;
  timestamp: string; // ISO 8601
  eventType: "click" | "input" | "navigation" | "network" | "assertion" | "error";
  url: string;
  target?: {
    selector: string;          // stable selector (prefer role/text-based)
    role?: string;             // ARIA role
    label?: string;            // accessible name
    text?: string;             // visible text
    bbox?: { x: number; y: number; width: number; height: number };
  };
  network?: {
    method: string;
    path: string;
    status: number;
    latencyMs: number;
  };
  screenshotKey?: string;      // object-storage key
  domSnapshotKey?: string;     // object-storage key
};
```

## Field notes

- **`sessionId` + `stepIndex`** order the stream and make events idempotent on re-ingest.
- **`eventType`** is the discriminant the compiler switches on. `click` and `input` become action edges; `navigation` typically opens a new state; `network` events are attached to the surrounding state for the network-causality view; `assertion` becomes a Playwright `expect`; `error` flags a failure candidate.
- **`target`** captures enough to regenerate a robust selector. We prefer **role + accessible name** (e.g. `getByRole("button", { name: "Continue" })`) over brittle CSS/XPath, falling back to `selector` when needed. `bbox` powers the replay overlay.
- **`network`** is populated for `network` events and lets the evaluator attribute failures to a bad response (e.g. a `500` that disabled a control).
- **`screenshotKey` / `domSnapshotKey`** reference object storage rather than inlining binary blobs into Postgres.

## Storage mapping

| Field | Stored as |
| --- | --- |
| `sessionId`, `stepIndex`, `eventType`, `timestamp`, `url` | relational columns on `events` |
| `target` | `events.target` (JSONB) |
| `network` | `events.network` (JSONB) |
| anything else | `events.payload` (JSONB) |
| screenshots, DOM snapshots | object storage, referenced by key |

Keeping `target`/`network`/`payload` as JSONB lets the schema evolve without a migration for every new captured attribute, while still being indexable for the queries that need it.

## Capture checklist (recorder SDK)

The recorder captures: DOM events, clicks, typed input, navigations/route changes, screenshots, network requests/responses, console logs, accessibility-tree snapshots, and element metadata (role, label, text, selector, bounding box).

## Example stream (login)

```jsonc
[
  { "sessionId": "s1", "stepIndex": 0, "eventType": "navigation", "url": "/login",
    "timestamp": "2026-01-01T00:00:00Z" },
  { "sessionId": "s1", "stepIndex": 1, "eventType": "click", "url": "/login",
    "timestamp": "2026-01-01T00:00:01Z",
    "target": { "selector": "#email", "role": "textbox", "label": "Email" } },
  { "sessionId": "s1", "stepIndex": 2, "eventType": "input", "url": "/login",
    "timestamp": "2026-01-01T00:00:02Z",
    "target": { "selector": "#email", "role": "textbox", "label": "Email" } },
  { "sessionId": "s1", "stepIndex": 3, "eventType": "click", "url": "/login",
    "timestamp": "2026-01-01T00:00:03Z",
    "target": { "selector": "button[type=submit]", "role": "button", "text": "Sign in" } },
  { "sessionId": "s1", "stepIndex": 4, "eventType": "network", "url": "/login",
    "timestamp": "2026-01-01T00:00:03Z",
    "network": { "method": "POST", "path": "/api/session", "status": 200, "latencyMs": 142 } },
  { "sessionId": "s1", "stepIndex": 5, "eventType": "navigation", "url": "/dashboard",
    "timestamp": "2026-01-01T00:00:04Z" }
]
```

This stream compiles into the workflow graph described in [workflow-graph.md](workflow-graph.md).

## Ingestion contract

- `POST /v1/events:batch` accepts an array of `BrowserEvent`s plus a project API key.
- The API validates each event against this schema, rejects malformed events with a per-item error, and appends valid events to the log.
- Re-sending the same `(sessionId, stepIndex)` is idempotent.
