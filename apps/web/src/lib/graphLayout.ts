import { MarkerType } from "reactflow";
import type { GNode, Run, WorkflowGraph } from "./types";

export type Mode = "human" | "compare" | "state" | "network";

export const COLOR = {
  human: "#34d399",
  divergence: "#f87171",
  agent: "#fb923c",
  network: "#60a5fa",
  assertion: "#fbbf24",
  agentNode: "#a78bfa",
};

const X_STATE = 160;
const X_SIDE = 520;
const Y0 = 40;
const DY = 84;

function mkEdge(id: string, source: string, target: string, color: string, o: any = {}) {
  return {
    id, source, target, label: o.label, animated: !!o.animated,
    markerEnd: { type: MarkerType.ArrowClosed, color },
    style: { stroke: color, strokeWidth: o.width || 2, strokeDasharray: o.dashed ? "6 4" : undefined },
    labelStyle: { fill: "#9ca3af", fontSize: 10 },
    labelBgStyle: { fill: "#0a0b0e", fillOpacity: 0.85 },
  };
}

export function buildFlow(workflow: WorkflowGraph, run: Run | null, mode: Mode, selectedId?: string) {
  const states = workflow.nodes.filter((n) => n.kind === "page-state" || n.kind === "assertion");
  const stateIndex = new Map(states.map((n, i) => [n.id, i]));
  const nodes: any[] = [];
  const edges: any[] = [];

  const push = (n: GNode, x: number, y: number, color: string, o: any = {}) =>
    nodes.push({
      id: n.id, position: { x, y }, data: { label: n.label },
      className: o.className,
      style: {
        background: selectedId === n.id ? "#1b2030" : "#13151a",
        color: "#e5e7eb", border: `1px solid ${color}`, borderRadius: 10,
        padding: "8px 12px", fontSize: 12, width: o.width || 178, ...(o.style || {}),
      },
    });

  states.forEach((n, i) => push(n, X_STATE, Y0 + i * DY, n.kind === "assertion" ? COLOR.assertion : COLOR.human));

  if (mode !== "network") {
    workflow.edges.filter((e) => e.kind === "human-path").forEach((e) =>
      edges.push(mkEdge(e.id, e.source, e.target, COLOR.human, { label: e.label, width: 2 })));
  }

  if (mode === "network") {
    workflow.nodes.filter((n) => n.kind === "network").forEach((n) => {
      const dep = workflow.edges.find((e) => e.kind === "network-dependency" && e.target === n.id);
      const idx = dep ? stateIndex.get(dep.source) ?? 0 : 0;
      const status = n.meta?.network?.status ?? 0;
      push(n, X_SIDE, Y0 + idx * DY, status >= 400 ? COLOR.divergence : COLOR.network, { width: 210 });
    });
    workflow.edges.filter((e) => e.kind === "network-dependency").forEach((e) =>
      edges.push(mkEdge(e.id, e.source, e.target, COLOR.network, { dashed: true, label: e.label })));
  }

  if (mode === "compare" && run?.comparison?.divergenceStep != null) {
    const div = run.comparison.divergenceStep;
    const divState = states[div] ?? states[0];
    const baseY = Y0 + (stateIndex.get(divState.id) ?? 0) * DY;
    run.comparison.nodes.forEach((n, k) => {
      const first = n.id === `a${div}`;
      push(n, X_SIDE, baseY + (k + 1) * DY, first ? COLOR.divergence : COLOR.agentNode, {
        className: first ? "rf-pulse" : undefined,
      });
    });
    run.comparison.edges.forEach((e) => {
      const isDiv = e.kind === "divergence";
      edges.push(mkEdge(e.id, e.source, e.target, isDiv ? COLOR.divergence : COLOR.agent, {
        dashed: !isDiv, animated: isDiv, width: isDiv ? 3 : 2, label: e.label,
      }));
    });
  }

  return { nodes, edges };
}
