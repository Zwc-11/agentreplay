export type Command = {
  kind: "click" | "fill" | "goto" | "assertVisible";
  selector?: string; role?: string; name?: string; text?: string; value?: string; url?: string;
};

export type GNode = {
  id: string; kind: string; label: string; stepIndex: number;
  url?: string; screenshotKey?: string; domSnapshotKey?: string; meta?: any;
};
export type GEdge = { id: string; source: string; target: string; kind: string; command?: Command; label?: string };
export type WorkflowGraph = { id: string; sessionId: string; nodes: GNode[]; edges: GEdge[] };

export type Metrics = {
  task_success: boolean; step_accuracy: number; wrong_click_count: number;
  divergence_step: number | null; recovered: boolean; network_caused_failure: boolean;
  failure_category: string | null; replay_latency_ms: number;
};
export type Summary = {
  category: string | null; summary: string; rootCause: string | null;
  githubIssue: { title: string; body: string } | null;
  model?: string | null;
};
export type Comparison = { divergenceStep: number | null; nodes: GNode[]; edges: GEdge[] };
export type Run = {
  id: string; workflowId: string; driver: string; status: string; success: boolean;
  agentCommands: Command[]; comparison: Comparison; metrics: Metrics; summary: Summary; generatedTest: string;
  llmEnabled?: boolean;
};

export type BrowserEvent = {
  sessionId: string; stepIndex: number; eventType: string; url: string; timestamp: string;
  target?: any; network?: any; screenshotKey?: string; domSnapshotKey?: string; payload?: any;
};

export type WorkflowSummary = {
  id: string; name: string; steps: number; runs: number; successRate: number | null;
};
export type DemoData = { workflow: WorkflowGraph; events: BrowserEvent[]; run: Run };
export type RecordingImport = {
  sessionId: string;
  workflowId?: string;
  name?: string;
  goal?: string;
  events: BrowserEvent[];
};
export type ImportResult = {
  accepted: number;
  sessionId: string;
  workflowId: string;
  workflow: WorkflowGraph;
};

export type DriverAggregate = {
  driver: string; workflows: number; taskSuccessRate: number; meanStepAccuracy: number;
  totalWrongClicks: number; meanFirstDivergence: number | null; networkCausedFailures: number;
};
export type BenchmarkRow = {
  workflow: string; driver: string; success: boolean;
  stepAccuracy: number; divergenceStep: number | null; category: string | null;
};
export type Benchmark = {
  workflows: number;
  drivers: Record<string, DriverAggregate>;
  rows: BenchmarkRow[];
  categories: Record<string, number>;
};
