# Workflow graph

The workflow compiler is the brain of AgentReplay. It converts a raw event stream into a **workflow graph** where each **node is a browser state** and each **edge is an action**.

```
Raw events → normalized events → browser states → edges/actions → workflow graph
```

## Worked example

```
State 1: Login page
  Edge: click email input
State 2: Email focused
  Edge: type email
State 3: Email filled
  Edge: click submit
State 4: Dashboard
```

This graph is the shared foundation for visualization, metrics, replay, and human-vs-agent comparison.

## Graph model

```ts
type WorkflowNode = {
  id: string;
  kind: "page-state" | "user-action" | "agent-action" | "network" | "assertion" | "failure";
  label: string;
  url?: string;
  stepIndex: number;
  screenshotKey?: string;
  domSnapshotKey?: string;
};

type WorkflowEdge = {
  id: string;
  from: string;
  to: string;
  kind: "human-path" | "agent-path" | "network-dependency" | "divergence";
  command?: BrowserCommand; // the action this edge represents
};

type WorkflowGraph = {
  id: string;
  sessionId: string;
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
};
```

## Compilation pipeline

1. **Normalize** — coalesce noisy raw DOM events (e.g. many `input` keystrokes → one "type email" action), drop duplicates, and order by `stepIndex`.
2. **Group into states** — a new **page-state** node is opened on navigation/route change or a material DOM change; intermediate events attach to the current state.
3. **Infer actions** — each state transition becomes an action edge carrying a typed `BrowserCommand` (`click | fill | goto | assertVisible`).
4. **Build graph** — assemble nodes + edges into a `WorkflowGraph`.
5. **Compute metrics** — see [evaluation.md](evaluation.md).
6. **Generate replay** — produce the step-indexed timeline the dashboard scrubs through.

Each stage is a pure transformation, so the compiler is tested stage-by-stage with fixture event streams.

## Node & edge types

**Node kinds:** `page-state`, `user-action`, `agent-action`, `network`, `assertion`, `failure`.
**Edge kinds:** `human-path`, `agent-path`, `network-dependency`, `divergence`.

## The four graph modes

The graph must answer *where did the agent go wrong?* in about three seconds.

### Mode 1 — Human path
The correct workflow: `Login → Search → Add Item → Checkout → Success`.

### Mode 2 — Human vs. agent (the WOW demo)
Both paths overlaid. The human path is the clean success route; the agent path is the diverging route; the **divergence node pulses red**.

```
Human:  Login → Search → Add to cart → Checkout → Success
Agent:  Login → Search → Click ad → Wrong page → Fail
                              ▲ first divergence
```

### Mode 3 — Browser-state graph
Each node is a state snapshot. Clicking a node reveals its screenshot, URL, DOM summary, available actions, network calls, and console logs.

### Mode 4 — Network causality
Shows how a network failure cascades into UI/agent failure:

```
Click Submit → POST /checkout → 500 response → disabled button → repeated wrong clicks → failure
```

## Rendering

The dashboard renders graphs with [React Flow](https://reactflow.dev), which is purpose-built for customizable node-based UIs and interactive diagrams. Node and edge components live in `apps/web/src/graph` and use the shared design-system tokens (green = success path, red = divergence, yellow = uncertain, blue/purple = AI summary).

## Persistence

A compiled graph is stored in `workflow_graphs (nodes jsonb, edges jsonb)` keyed by `session_id`, and is always reproducible by re-projecting the event log.
