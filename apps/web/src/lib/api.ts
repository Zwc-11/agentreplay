import benchmarkData from "../benchmarkData.json";
import offlineData from "../fixtures/offline.json";
import type {
  Benchmark,
  BrowserEvent,
  DemoData,
  ImportResult,
  RecordingImport,
  Run,
  WorkflowGraph,
  WorkflowSummary,
} from "./types";

const BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
const DEMO_ID = "demo-checkout";

const OFFLINE = offlineData as unknown as {
  workflows: WorkflowSummary[];
  byWorkflow: Record<string, { workflow: WorkflowGraph; events: BrowserEvent[]; runs: Record<string, Run> }>;
};

let _offline = false;
/** True once any API call has fallen back to the bundled demo fixture. */
export function isOffline(): boolean {
  return _offline;
}

async function withFallback<T>(live: () => Promise<T>, bundled: () => T): Promise<T> {
  try {
    const value = await live();
    _offline = false;
    return value;
  } catch {
    if (!_offline) {
      _offline = true;
      console.info("[AgentReplay] API unreachable — showing the bundled demo fixture (offline mode).");
    }
    return bundled();
  }
}

function wf(id: string) {
  return OFFLINE.byWorkflow[id] ?? OFFLINE.byWorkflow[DEMO_ID];
}

export async function fetchWorkflows(): Promise<WorkflowSummary[]> {
  return withFallback(
    async () => {
      const res = await fetch(`${BASE}/v1/workflows`);
      if (!res.ok) throw new Error(String(res.status));
      return (await res.json()).workflows;
    },
    () => OFFLINE.workflows,
  );
}

export async function fetchDemo(workflowId?: string): Promise<DemoData> {
  return withFallback(
    async () => {
      const qs = workflowId ? `?workflow_id=${encodeURIComponent(workflowId)}` : "";
      const res = await fetch(`${BASE}/v1/demo${qs}`);
      if (!res.ok) throw new Error(String(res.status));
      return res.json();
    },
    () => {
      const w = wf(workflowId ?? DEMO_ID);
      return { workflow: w.workflow, events: w.events, run: w.runs.divergent };
    },
  );
}

export async function fetchEvents(workflowId: string): Promise<BrowserEvent[]> {
  return withFallback(
    async () => {
      const res = await fetch(`${BASE}/v1/workflows/${workflowId}/events`);
      if (!res.ok) throw new Error(String(res.status));
      return (await res.json()).events;
    },
    () => wf(workflowId).events,
  );
}

export async function startRun(workflowId: string, driver = "divergent"): Promise<Run> {
  return withFallback(
    async () => {
      const res = await fetch(`${BASE}/v1/workflows/${workflowId}/runs?driver=${driver}`, { method: "POST" });
      if (!res.ok) throw new Error(String(res.status));
      return res.json();
    },
    () => {
      const runs = wf(workflowId).runs;
      return runs[driver] ?? runs.divergent;
    },
  );
}

export async function fetchBenchmark(drivers = "scripted,divergent,random"): Promise<Benchmark> {
  return withFallback(
    async () => {
      const res = await fetch(`${BASE}/v1/benchmark?drivers=${encodeURIComponent(drivers)}`);
      if (!res.ok) throw new Error(String(res.status));
      return res.json();
    },
    () => benchmarkData as unknown as Benchmark,
  );
}

export async function importRecording(recording: RecordingImport): Promise<ImportResult> {
  // Importing persists server-side, so it needs the API running.
  const res = await fetch(`${BASE}/v1/recordings:import`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(recording),
  });
  if (!res.ok) throw new Error(`Import needs the API running (got ${res.status}). Start it with: uvicorn app.main:app`);
  return res.json();
}

/** Lightweight health check used by the connection indicator. */
export async function pingApi(): Promise<boolean> {
  try {
    const res = await fetch(`${BASE}/health`);
    return res.ok;
  } catch {
    return false;
  }
}

/** URL for a stored screenshot / DOM snapshot blob. */
export function blobUrl(key: string): string {
  return `${BASE}/v1/blobs/${key}`;
}
