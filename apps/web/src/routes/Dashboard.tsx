import { useMemo, useState } from "react";
import demo from "../demoData.json";
import { Button, Card, GraphLegend, StatusBadge, Tabs } from "../design-system";
import { WorkflowGraphView } from "../graph/WorkflowGraphView";
import { ReplayPanel } from "../replay/ReplayPanel";
import { Timeline } from "../components/Timeline";
import { MetricsPanel } from "../components/MetricsPanel";
import { FailureSummary } from "../components/FailureSummary";
import { TestExport } from "../components/TestExport";
import type { Mode } from "../lib/graphLayout";
import type { DemoData, Run } from "../lib/types";

const data = demo as unknown as DemoData;

const MODE_TABS = [
  { id: "human", label: "Human" },
  { id: "compare", label: "Human vs Agent" },
  { id: "state", label: "State" },
  { id: "network", label: "Network" },
];

export function Dashboard() {
  const [driver, setDriver] = useState<"divergent" | "scripted">("divergent");
  const run: Run = driver === "scripted" ? data.runs.scripted : data.runs.divergent;

  const [mode, setMode] = useState<Mode>("compare");
  const maxStep = useMemo(() => Math.max(...data.events.map((e) => e.stepIndex)), []);
  const [step, setStep] = useState(maxStep);
  const [selected, setSelected] = useState<string | undefined>(undefined);

  return (
    <div className="min-h-screen p-4 space-y-4 max-w-[1400px] mx-auto">
      <header className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <h1 className="text-lg font-semibold">AgentReplay</h1>
          <span className="text-gray-500 text-sm">Project: {data.workflow.sessionId}</span>
          <StatusBadge status={run.success ? "success" : "failure"} label={`${run.driver} agent`} />
        </div>
        <div className="flex items-center gap-2">
          <select
            value={driver}
            onChange={(e) => setDriver(e.target.value as "divergent" | "scripted")}
            className="text-xs bg-white/5 border border-white/10 rounded-lg px-2 py-1.5 text-gray-200"
          >
            <option value="divergent">divergent agent</option>
            <option value="scripted">scripted agent</option>
          </select>
          <Button>Run Agent</Button>
          <Button variant="ghost">Export Test</Button>
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <ReplayPanel events={data.events} step={step} maxStep={maxStep} onStep={setStep} />
        <Card title="Workflow Graph">
          <div className="flex items-center justify-between mb-2">
            <Tabs tabs={MODE_TABS} active={mode} onChange={(id) => setMode(id as Mode)} />
          </div>
          <div className="h-[380px] rounded-lg overflow-hidden border border-white/5 bg-black/20">
            <WorkflowGraphView
              workflow={data.workflow}
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
        <Timeline events={data.events} step={step} onSelect={setStep} />
        <FailureSummary run={run} />
      </div>

      <TestExport test={run.generatedTest} />
    </div>
  );
}
