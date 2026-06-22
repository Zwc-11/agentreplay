import type {
  BrowserEvent,
  DemoData,
  ImportResult,
  RecordingImport,
  Run,
  WorkflowSummary,
} from "./types";

const BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export async function fetchWorkflows(): Promise<WorkflowSummary[]> {
  const res = await fetch(`${BASE}/v1/workflows`);
  if (!res.ok) throw new Error(`workflow fetch failed: ${res.status}`);
  const data = await res.json();
  return data.workflows;
}

export async function fetchDemo(workflowId?: string): Promise<DemoData> {
  const qs = workflowId ? `?workflow_id=${encodeURIComponent(workflowId)}` : "";
  const res = await fetch(`${BASE}/v1/demo${qs}`);
  if (!res.ok) throw new Error(`demo fetch failed: ${res.status}`);
  return res.json();
}

export async function fetchEvents(workflowId: string): Promise<BrowserEvent[]> {
  const res = await fetch(`${BASE}/v1/workflows/${workflowId}/events`);
  if (!res.ok) throw new Error(`events fetch failed: ${res.status}`);
  const data = await res.json();
  return data.events;
}

export async function startRun(workflowId: string, driver = "divergent"): Promise<Run> {
  const res = await fetch(`${BASE}/v1/workflows/${workflowId}/runs?driver=${driver}`, { method: "POST" });
  if (!res.ok) throw new Error(`run failed: ${res.status}`);
  return res.json();
}

export async function importRecording(recording: RecordingImport): Promise<ImportResult> {
  const res = await fetch(`${BASE}/v1/recordings:import`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(recording),
  });
  if (!res.ok) throw new Error(`recording import failed: ${res.status}`);
  return res.json();
}
