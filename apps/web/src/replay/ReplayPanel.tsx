import { Card } from "../design-system";
import { blobUrl } from "../lib/api";
import { reconstructAt } from "../lib/replay";
import type { BrowserEvent } from "../lib/types";

export function ReplayPanel({
  events, step, maxStep, onStep,
}: {
  events: BrowserEvent[]; step: number; maxStep: number; onStep: (n: number) => void;
}) {
  const snap = reconstructAt(events, step);
  return (
    <Card title="Browser Replay">
      <div className="aspect-video rounded-lg bg-black/40 border border-white/5 grid place-items-center text-gray-500 text-xs relative overflow-hidden">
        {snap.screenshotKey && (
          <img
            src={blobUrl(snap.screenshotKey)}
            alt={`screenshot at step ${step}`}
            className="absolute inset-0 w-full h-full object-cover"
            onError={(e) => {
              (e.currentTarget as HTMLImageElement).style.display = "none";
            }}
          />
        )}
        <span className="absolute top-2 left-2 z-10 text-[11px] text-gray-400 font-mono truncate max-w-[90%]">
          {snap.url ?? "about:blank"}
        </span>
        <span className="relative z-0">
          {snap.screenshotKey ? `screenshot · step ${step}` : `DOM snapshot @ step ${step}`}
        </span>
      </div>

      <input
        type="range"
        min={0}
        max={maxStep}
        value={step}
        onChange={(e) => onStep(Number(e.target.value))}
        className="w-full mt-3 accent-emerald-400"
      />

      <div className="mt-2 grid grid-cols-3 gap-2 text-[11px] text-gray-400">
        <div><div className="text-gray-500">Step</div>{step} / {maxStep}</div>
        <div><div className="text-gray-500">Network</div>{snap.network.length} call(s)</div>
        <div><div className="text-gray-500">Last action</div>{snap.lastAction?.eventType ?? "—"}</div>
      </div>

      {snap.network.length > 0 && (
        <div className="mt-2 text-[11px] font-mono space-y-0.5">
          {snap.network.slice(-3).map((n, i) => (
            <div key={i} className={n.status >= 400 ? "text-red-400" : "text-gray-400"}>
              {n.method} {n.path} → {n.status} ({n.latencyMs}ms)
            </div>
          ))}
        </div>
      )}
    </Card>
  );
}
