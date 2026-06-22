import { useState } from "react";

export function CodeBlock({ code }: { code: string }) {
  const [copied, setCopied] = useState(false);
  const copy = async () => {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 1200);
    } catch {
      /* clipboard unavailable */
    }
  };
  return (
    <div className="relative">
      <button
        onClick={copy}
        className="absolute right-2 top-2 text-xs px-2 py-0.5 rounded bg-white/10 hover:bg-white/20 text-gray-200"
      >
        {copied ? "Copied" : "Copy"}
      </button>
      <pre className="overflow-auto rounded-lg bg-black/50 p-3 text-xs leading-relaxed text-gray-200">
        <code>{code}</code>
      </pre>
    </div>
  );
}
