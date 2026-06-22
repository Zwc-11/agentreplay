import type { Run, WorkflowGraph } from "./types";

const BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export async function fetchDemo(): Promise<{ workflow: WorkflowGraph; run: Run }> {
  const res = await fetch(`${BASE}/v1/demo`);
  if (!res.ok) throw new Error(`demo fetch failed: ${res.status}`);
  return res.json();
}

export async function startRun(workflowId: string, driver = "divergent"): Promise<Run> {
  const res = await fetch(`${BASE}/v1/workflows/${workflowId}/runs?driver=${driver}`, { method: "POST" });
  if (!res.ok) throw new Error(`run failed: ${res.status}`);
  return res.json();
}
