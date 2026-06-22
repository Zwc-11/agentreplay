import type { BrowserEvent } from "./types";

export type Snapshot = {
  url?: string; stepIndex: number; lastAction?: BrowserEvent;
  network: any[]; console: string[]; screenshotKey?: string; domSnapshotKey?: string;
};

export function reconstructAt(events: BrowserEvent[], stepIndex: number): Snapshot {
  const ev = [...events].sort((a, b) => a.stepIndex - b.stepIndex);
  const snap: Snapshot = { stepIndex, network: [], console: [] };
  for (const e of ev) {
    if (e.stepIndex > stepIndex) break;
    if (e.url) snap.url = e.url;
    if (e.eventType === "network" && e.network) snap.network.push(e.network);
    if (e.screenshotKey) snap.screenshotKey = e.screenshotKey;
    if (e.domSnapshotKey) snap.domSnapshotKey = e.domSnapshotKey;
    if (["click", "input", "assertion"].includes(e.eventType)) snap.lastAction = e;
    const c = e.payload?.console;
    if (c) snap.console.push(c);
  }
  return snap;
}
