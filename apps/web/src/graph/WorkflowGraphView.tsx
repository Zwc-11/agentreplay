import ReactFlow, { Background, Controls } from "reactflow";
import "reactflow/dist/style.css";
import { buildFlow, type Mode } from "../lib/graphLayout";
import type { Run, WorkflowGraph } from "../lib/types";

export function WorkflowGraphView({
  workflow, run, mode, selectedId, onSelect,
}: {
  workflow: WorkflowGraph; run: Run | null; mode: Mode;
  selectedId?: string; onSelect?: (id: string) => void;
}) {
  const { nodes, edges } = buildFlow(workflow, run, mode, selectedId);
  return (
    <div className="h-full w-full">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        fitView
        minZoom={0.2}
        nodesDraggable={false}
        nodesConnectable={false}
        onNodeClick={(_, n) => onSelect?.(n.id)}
        proOptions={{ hideAttribution: true }}
      >
        <Background gap={28} color="#1b1f27" />
        <Controls showInteractive={false} />
      </ReactFlow>
    </div>
  );
}
