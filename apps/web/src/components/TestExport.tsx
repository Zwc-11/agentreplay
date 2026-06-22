import { Card, CodeBlock } from "../design-system";

export function TestExport({ test }: { test: string }) {
  const download = () => {
    const blob = new Blob([test], { type: "text/plain" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "workflow.spec.ts";
    a.click();
  };
  return (
    <Card title="Generated Playwright test">
      <CodeBlock code={test} />
      <div className="mt-2 flex gap-2">
        <button
          onClick={download}
          className="text-xs px-3 py-1.5 rounded-lg bg-white/5 border border-white/10 text-gray-200 hover:bg-white/10"
        >
          Download .spec.ts
        </button>
      </div>
    </Card>
  );
}
