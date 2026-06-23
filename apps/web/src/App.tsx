import { useState } from "react";
import { BenchmarkView } from "./components/BenchmarkView";
import { AppBar } from "./design-system";
import { Dashboard } from "./routes/Dashboard";

const VIEWS = [
  { id: "workflow", label: "Workflow" },
  { id: "benchmark", label: "Benchmark" },
];

export function App() {
  const [view, setView] = useState("workflow");
  return (
    <div className="min-h-screen">
      <AppBar nav={VIEWS} active={view} onNav={setView} />
      {view === "workflow" ? (
        <Dashboard />
      ) : (
        <div className="max-w-[1400px] mx-auto p-4">
          <BenchmarkView />
        </div>
      )}
    </div>
  );
}
