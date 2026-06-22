import { useEffect, useMemo, useRef, useState } from "react";
import { fetchDemo, fetchWorkflows, importRecording, startRun } from "../lib/api";
import { Button, Card, GraphLegend, StatusBadge, Tabs } from "../design-system";
import { WorkflowGraphView } from "../graph/WorkflowGraphView";
import { ReplayPanel } from "../replay/ReplayPanel";
import { Timeline } from "../components/Timeline";
import { MetricsPanel } from "../components/MetricsPanel";
import { FailureSummary } from "../components/FailureSummary";
import { TestExport } from "../components/TestExport";
import type { Mode } from "../lib/graphLayout";
import type { BrowserEvent, Run, WorkflowGraph, WorkflowSummary } from "../lib/types";

const MODE_TABS = [
  { id: "human", label: "Human" },
  { id: "compare", label: "Human vs Agent" },
  { id: "state", label: "State" },
  { id: "network", label: "Network" },
];

const DRIVER_OPTIONS = [
  { id: "divergent", label: "divergent agent" },
  { id: "scripted", label: "scripted agent" },
  { id: "random", label: "random agent" },
  { id: "llm", label: "DeepSeek agent" },
];

export function Dashboard() {
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [workflows, setWorkflows] = useState<WorkflowSummary[]>([]);
  const [workflow, setWorkflow] = useState<WorkflowGraph | null>(null);
  const [events, setEvents] = useState<BrowserEvent[]>([]);
  const [run, setRun] = useState<Run | null>(null);
  const [workflowId, setWorkflowId] = useState("demo-checkout");
  const [driver, setDriver] = useState("divergent");
  const [mode, setMode] = useState<Mode>("compare");
  const [step, setStep] = useState(0);
  const [selected, setSelected] = useState<string | undefined>(undefined);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  const maxStep = useMemo(() => Math.max(0, ...events.map((e) => e.stepIndex)), [events]);

  function applyPayload(list: WorkflowSummary[], payload: Awaited<ReturnType<typeof fetchDemo>>) {
    setWorkflows(list);
    setWorkflow(payload.workflow);
    setEvents(payload.events);
    setRun(payload.run);
    setStep(Math.max(0, ...payload.events.map((e) => e.stepIndex)));
    setSelected(undefined);
  }

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    Promise.all([fetchWorkflows(), fetchDemo(workflowId)])
      .then(([list, payload]) => {
        if (cancelled) return;
        applyPayload(list, payload);
      })
      .catch((e) => {
        if (!cancelled) setError(e instanceof Error ? e.message : String(e));
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [workflowId]);

  async function runAgent() {
    if (!workflow) return;
    setRunning(true);
    setError(null);
    setNotice(null);
    try {
      const nextRun = await startRun(workflow.id, driver);
      setRun(nextRun);
      setMode("compare");
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setRunning(false);
    }
  }

  async function importRecordingFile(file: File) {
    setLoading(true);
    setError(null);
    setNotice(null);
    try {
      const text = await file.text();
      const recording = JSON.parse(text);
      if (!recording.sessionId || !Array.isArray(recording.events)) {
        throw new Error("Recording JSON must include sessionId and events[].");
      }
      const imported = await importRecording(recording);
      const [list, payload] = await Promise.all([fetchWorkflows(), fetchDemo(imported.workflowId)]);
      setWorkflowId(imported.workflowId);
      applyPayload(list, payload);
      setNotice(`Imported ${imported.accepted} events as ${imported.workflowId}.`);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  }

  function exportTest() {
    if (!run?.generatedTest) return;
    const blob = new Blob([run.generatedTest], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${workflow?.id ?? "workflow"}.spec.ts`;
    a.click();
    URL.revokeObjectURL(url);
  }

  if (loading || !workflow || !run) {
    return (
      <div className="min-h-screen p-4 max-w-[1400px] mx-auto">
        <Card title="AgentReplay">
          <div className="text-sm text-gray-400">{loading ? "Loading workflow data..." : "No workflow loaded."}</div>
          {error && <div className="mt-2 text-sm text-red-300">{error}</div>}
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-4 space-y-4 max-w-[1400px] mx-auto">
      <header className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <h1 className="text-lg font-semibold">AgentReplay</h1>
          <span className="text-gray-500 text-sm">Project: {workflow.sessionId}</span>
          <StatusBadge status={run.success ? "success" : "failure"} label={`${run.driver} agent`} />
        </div>
        <div className="flex items-center gap-2">
          <select
            value={workflowId}
            onChange={(e) => {
              setNotice(null);
              setWorkflowId(e.target.value);
            }}
            className="text-xs bg-white/5 border border-white/10 rounded-lg px-2 py-1.5 text-gray-200"
          >
            {workflows.map((w) => (
              <option key={w.id} value={w.id}>
                {w.name}
              </option>
            ))}
          </select>
          <select
            value={driver}
            onChange={(e) => setDriver(e.target.value)}
            className="text-xs bg-white/5 border border-white/10 rounded-lg px-2 py-1.5 text-gray-200"
          >
            {DRIVER_OPTIONS.map((option) => (
              <option key={option.id} value={option.id}>
                {option.label}
              </option>
            ))}
          </select>
          <Button onClick={runAgent} disabled={running}>{running ? "Running..." : "Run Agent"}</Button>
          <Button variant="ghost" onClick={() => fileInputRef.current?.click()}>Import Recording</Button>
          <Button variant="ghost" onClick={exportTest}>Export Test</Button>
          <input
            ref={fileInputRef}
            type="file"
            accept="application/json,.json"
            className="hidden"
            onChange={(e) => {
              const file = e.currentTarget.files?.[0];
              if (file) void importRecordingFile(file);
            }}
          />
        </div>
      </header>
      {error && <div className="text-sm text-red-300 bg-red-500/10 border border-red-500/20 rounded-lg p-3">{error}</div>}
      {notice && <div className="text-sm text-emerald-200 bg-emerald-500/10 border border-emerald-500/20 rounded-lg p-3">{notice}</div>}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <ReplayPanel events={events} step={step} maxStep={maxStep} onStep={setStep} />
        <Card title="Workflow Graph">
          <div className="flex items-center justify-between mb-2">
            <Tabs tabs={MODE_TABS} active={mode} onChange={(id) => setMode(id as Mode)} />
          </div>
          <div className="h-[380px] rounded-lg overflow-hidden border border-white/5 bg-black/20">
            <WorkflowGraphView
              workflow={workflow}
              run={run}
              mode={mode}
              selectedId={selected}
              onSelect={setSelected}
            />
          </div>
          <div className="mt-2">
            <GraphLegend />
          </div>
        </Card>
      </div>

      <MetricsPanel m={run.metrics} />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Timeline events={events} step={step} onSelect={setStep} />
        <FailureSummary run={run} />
      </div>

      <TestExport test={run.generatedTest} />
    </div>
  );
}
