import { useEffect, useState } from "react";
import benchmarkFallback from "../benchmarkData.json";
import { Card, MetricCard, StatusBadge } from "../design-system";
import { fetchBenchmark } from "../lib/api";
import type { Benchmark } from "../lib/types";

function successStatus(rate: number): "success" | "warning" | "failure" {
  if (rate >= 1) return "success";
  if (rate <= 0) return "failure";
  return "warning";
}

export function BenchmarkView() {
  const [data, setData] = useState<Benchmark | null>(null);
  const [offline, setOffline] = useState(false);

  useEffect(() => {
    let alive = true;
    fetchBenchmark()
      .then((d) => alive && setData(d))
      .catch(() => {
        if (!alive) return;
        setData(benchmarkFallback as unknown as Benchmark);
        setOffline(true);
      });
    return () => {
      alive = false;
    };
  }, []);

  if (!data) {
    return (
      <Card title="Benchmark">
        <div className="text-gray-500 text-sm p-4">Running benchmark…</div>
      </Card>
    );
  }

  const drivers = Object.values(data.drivers);

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <MetricCard label="Workflows" value={data.workflows} />
        <MetricCard label="Drivers" value={drivers.length} />
        <MetricCard label="Total runs" value={data.rows.length} />
        <MetricCard label="Failure types" value={Object.keys(data.categories).length} />
      </div>

      <Card title="Per-driver metrics">
        <div className="overflow-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-500 text-xs">
                <th className="py-2 pr-3">Driver</th>
                <th className="pr-3">Task success</th>
                <th className="pr-3">Mean step acc.</th>
                <th className="pr-3">Wrong clicks</th>
                <th className="pr-3">Mean 1st divergence</th>
                <th className="pr-3">Network-caused</th>
              </tr>
            </thead>
            <tbody>
              {drivers.map((d) => (
                <tr key={d.driver} className="border-t border-white/5">
                  <td className="py-2 pr-3">
                    <StatusBadge status={successStatus(d.taskSuccessRate)} label={d.driver} />
                  </td>
                  <td className="pr-3 text-gray-200">{Math.round(d.taskSuccessRate * 100)}%</td>
                  <td className="pr-3 text-gray-200">{Math.round(d.meanStepAccuracy * 100)}%</td>
                  <td className="pr-3 text-gray-200">{d.totalWrongClicks}</td>
                  <td className="pr-3 text-gray-200">{d.meanFirstDivergence ?? "—"}</td>
                  <td className="pr-3 text-gray-200">{d.networkCausedFailures}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      <Card title="Failure categories">
        <div className="flex flex-wrap gap-2">
          {Object.entries(data.categories).map(([k, v]) => (
            <span key={k} className="text-xs px-2 py-1 rounded-lg bg-white/5 border border-white/10 text-gray-200">
              {k}: <b>{v}</b>
            </span>
          ))}
          {Object.keys(data.categories).length === 0 && <span className="text-gray-500 text-sm">none</span>}
        </div>
      </Card>

      {offline && <div className="text-[11px] text-gray-600">offline — showing the bundled benchmark fixture</div>}
    </div>
  );
}
