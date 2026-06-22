// @agentreplay/shared-types — the contract shared by recorder, API, compiler, dashboard.

export type EventType = "click" | "input" | "navigation" | "network" | "assertion" | "error";

export type BrowserEvent = {
  sessionId: string;
  stepIndex: number;
  timestamp: string; // ISO 8601
  eventType: EventType;
  url: string;
  target?: {
    selector: string;
    role?: string;
    label?: string;
    text?: string;
    bbox?: { x: number; y: number; width: number; height: number };
  };
  network?: { method: string; path: string; status: number; latencyMs: number };
  screenshotKey?: string;
  domSnapshotKey?: string;
  payload?: Record<string, any>;
};

export type CommandKind = "click" | "fill" | "goto" | "assertVisible";

/** A typed browser action. Maps onto Playwright generation and agent execution. */
export type Command = {
  kind: CommandKind;
  selector?: string;
  role?: string;
  name?: string; // accessible name
  text?: string;
  value?: string;
  url?: string;
};
export type BrowserCommand = Command; // backwards-compatible alias

export type WorkflowNodeKind = "page-state" | "user-action" | "agent-action" | "network" | "assertion" | "failure";
export type WorkflowEdgeKind = "human-path" | "agent-path" | "network-dependency" | "divergence";

export type WorkflowNode = {
  id: string;
  kind: WorkflowNodeKind;
  label: string;
  stepIndex: number;
  url?: string;
  screenshotKey?: string;
  domSnapshotKey?: string;
  meta?: Record<string, any>;
};

export type WorkflowEdge = {
  id: string;
  source: string;
  target: string;
  kind: WorkflowEdgeKind;
  command?: Command;
  label?: string;
};

export type WorkflowGraph = { id: string; sessionId: string; nodes: WorkflowNode[]; edges: WorkflowEdge[] };

export type WorkflowTask = { workflowId: string; goal: string; startUrl: string; humanCommands?: Command[] };
export type AgentAction = { stepIndex: number; command: Command; resultUrl?: string };
export type AgentRunResult = { driverName: string; success: boolean; commands: Command[] };

export interface AgentDriver {
  name: string;
  run(task: WorkflowTask): Promise<AgentRunResult> | AgentRunResult;
}

export type EvaluationMetrics = {
  taskSuccess: boolean;
  stepAccuracy: number;
  wrongClickCount: number;
  divergenceStep: number | null;
  recovered: boolean;
  networkCausedFailure: boolean;
  failureCategory: string | null;
  replayLatencyMs: number;
};

export type FailureCategory = "wrong-element" | "stale-state" | "network-caused" | "missing-recovery" | "assertion-failed";
