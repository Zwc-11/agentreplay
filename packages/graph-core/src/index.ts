import type { BrowserEvent, Command, WorkflowEdge, WorkflowGraph, WorkflowNode } from "@agentreplay/shared-types";

function route(url?: string): string {
  if (!url) return "page";
  try {
    const u = new URL(url);
    const segs = u.pathname.split("/").filter(Boolean);
    return segs.length ? segs[segs.length - 1] : u.hostname || "home";
  } catch {
    return "page";
  }
}

export function normalize(events: BrowserEvent[]): BrowserEvent[] {
  const ev = [...events].sort((a, b) => a.stepIndex - b.stepIndex);
  const out: BrowserEvent[] = [];
  for (const e of ev) {
    const last = out[out.length - 1];
    if (e.eventType === "input" && last && last.eventType === "input" && last.target?.selector === e.target?.selector) {
      out[out.length - 1] = e; // keep latest typed value
    } else {
      out.push(e);
    }
  }
  return out;
}

function commandFor(e: BrowserEvent): Command | null {
  const t = e.target || ({} as NonNullable<BrowserEvent["target"]>);
  switch (e.eventType) {
    case "navigation":
      return { kind: "goto", url: e.url };
    case "click":
      return { kind: "click", selector: t.selector, role: t.role, name: t.label, text: t.text };
    case "input":
      return { kind: "fill", selector: t.selector, role: t.role, name: t.label, value: e.payload?.value ?? t.text ?? "" };
    case "assertion":
      return { kind: "assertVisible", selector: t.selector, text: t.text, name: t.label };
    default:
      return null;
  }
}

function stateLabel(e: BrowserEvent, r: string): string {
  const t = e.target || ({} as any);
  const name = t.label || t.text || "";
  switch (e.eventType) {
    case "navigation":
      return r.charAt(0).toUpperCase() + r.slice(1);
    case "click":
      return ["textbox", "combobox", "searchbox"].includes(t.role) ? `${name} focused`.trim() : name ? `${name} clicked` : "clicked";
    case "input":
      return name ? `${name} filled` : "filled";
    case "assertion":
      return `Assert: ${t.text || name}`.trim();
    default:
      return r;
  }
}

function edgeLabel(e: BrowserEvent): string {
  const t = e.target || ({} as any);
  const name = t.label || t.text || t.selector || "";
  const m: Record<string, string> = {
    navigation: `goto ${e.url}`,
    click: `click ${name}`,
    input: `type ${name}`,
    assertion: `assert ${t.text || name}`,
  };
  return m[e.eventType] ?? e.eventType;
}

export function compile(events: BrowserEvent[], sessionId: string, graphId?: string): WorkflowGraph {
  const ev = normalize(events);
  const nodes: WorkflowNode[] = [];
  const edges: WorkflowEdge[] = [];
  let prev: WorkflowNode | null = null;
  let currentUrl: string | undefined;
  let si = 0, ni = 0, ei = 0;

  for (const e of ev) {
    if (e.eventType === "navigation") currentUrl = e.url;

    if (e.eventType === "network") {
      const net = e.network || ({} as any);
      const id = `net${ni++}`;
      nodes.push({ id, kind: "network", label: `${net.method ?? ""} ${net.path ?? ""} -> ${net.status ?? ""}`.trim(), stepIndex: e.stepIndex, url: currentUrl, meta: { network: net } });
      if (prev) edges.push({ id: `e${ei++}`, source: prev.id, target: id, kind: "network-dependency", label: String(net.status ?? "") });
      continue;
    }

    if (e.eventType === "error") {
      const id = `fail${ni++}`;
      nodes.push({ id, kind: "failure", label: e.payload?.message ?? "Error", stepIndex: e.stepIndex, url: currentUrl });
      if (prev) edges.push({ id: `e${ei++}`, source: prev.id, target: id, kind: "divergence" });
      prev = nodes[nodes.length - 1];
      continue;
    }

    const cmd = commandFor(e);
    const id = `s${si++}`;
    const node: WorkflowNode = {
      id,
      kind: e.eventType === "assertion" ? "assertion" : "page-state",
      label: stateLabel(e, route(currentUrl)),
      stepIndex: e.stepIndex,
      url: currentUrl,
      screenshotKey: e.screenshotKey,
      domSnapshotKey: e.domSnapshotKey,
    };
    nodes.push(node);
    if (prev && cmd) edges.push({ id: `e${ei++}`, source: prev.id, target: id, kind: "human-path", command: cmd, label: edgeLabel(e) });
    prev = node;
  }

  return { id: graphId ?? cryptoRandomId(), sessionId, nodes, edges };
}

function cryptoRandomId(): string {
  return (globalThis as any).crypto?.randomUUID?.() ?? `g-${Math.random().toString(36).slice(2)}`;
}

export function humanCommands(graph: WorkflowGraph): Command[] {
  return graph.edges.filter((e) => e.kind === "human-path" && e.command).map((e) => e.command as Command);
}
