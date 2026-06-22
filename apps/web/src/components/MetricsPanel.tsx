import { MetricCard } from "../design-system";
import type { Metrics } from "../lib/types";

export function MetricsPanel({ m }: { m: Metrics }) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
      <MetricCard label="Task success" value={m.task_success ? "Pass" : "Fail"} />
      <MetricCard label="Step accuracy" value={`${Math.round(m.step_accuracy * 100)}%`} />
      <MetricCard label="First divergence" value={m.divergence_step == null ? "-" : `step ${m.divergence_step + 1}`} />
      <MetricCard label="Wrong clicks" value={m.wrong_click_count} />
      <MetricCard label="Recovered" value={m.recovered ? "Yes" : "No"} />
      <MetricCard label="Replay latency" value={`${m.replay_latency_ms}ms`} />
    </div>
  );
}
