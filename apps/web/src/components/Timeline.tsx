import { useState } from "react";
import { Card } from "../design-system";
import type { BrowserEvent } from "../lib/types";

const TYPES = ["all", "click", "input", "navigation", "network", "assertion", "error"];

function label(e: BrowserEvent): string {
  if (e.eventType === "network") return `${e.network?.method} ${e.network?.path} -> ${e.network?.status}`;
  if (e.eventType === "navigation") return e.url;
  const t = e.target || {};
  return t.label || t.text || t.selector || "";
}

export function Timeline({
  events,
  step,
  onSelect,
}: {
  events: BrowserEvent[];
  step: number;
  onSelect: (n: number) => void;
}) {
  const [filter, setFilter] = useState("all");
  const rows = [...events]
    .sort((a, b) => a.stepIndex - b.stepIndex)
    .filter((e) => filter === "all" || e.eventType === filter);

  return (
    <Card title="Timeline - DOM / Network / Logs">
      <div className="flex flex-wrap gap-1 mb-2">
        {TYPES.map((t) => (
          <button
            key={t}
            onClick={() => setFilter(t)}
            className={`px-1.5 py-0.5 rounded text-[10px] ${
              filter === t ? "bg-white/15 text-white" : "bg-white/5 text-gray-400 hover:text-gray-200"
            }`}
          >
            {t}
          </button>
        ))}
      </div>
      <div className="max-h-64 overflow-auto divide-y divide-white/5">
        {rows.map((e) => (
          <button
            key={e.stepIndex}
            onClick={() => onSelect(e.stepIndex)}
            className={`w-full text-left py-1.5 px-1 flex items-center gap-2 text-[11px] hover:bg-white/5 ${
              e.stepIndex === step ? "bg-white/10" : ""
            }`}
          >
            <span className="w-6 text-gray-600">{e.stepIndex}</span>
            <span className="w-20 text-gray-400">{e.eventType}</span>
            <span className="flex-1 truncate text-gray-300">{label(e)}</span>
          </button>
        ))}
      </div>
    </Card>
  );
}
