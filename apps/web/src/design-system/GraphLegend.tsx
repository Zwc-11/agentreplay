import { COLOR } from "../lib/graphLayout";

const ITEMS: [string, string][] = [
  ["Human path", COLOR.human],
  ["Divergence", COLOR.divergence],
  ["Agent path", COLOR.agent],
  ["Network", COLOR.network],
  ["Assertion", COLOR.assertion],
];

export function GraphLegend() {
  return (
    <div className="flex flex-wrap gap-3 text-[11px] text-gray-400">
      {ITEMS.map(([label, c]) => (
        <span key={label} className="inline-flex items-center gap-1">
          <span className="w-2.5 h-2.5 rounded-full" style={{ background: c }} />
          {label}
        </span>
      ))}
    </div>
  );
}
