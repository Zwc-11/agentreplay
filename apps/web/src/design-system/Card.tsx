import type { ReactNode } from "react";

export function Card({ title, children }: { title?: string; children: ReactNode }) {
  return (
    <div className="glass p-4">
      {title && <h3 className="text-sm font-semibold text-gray-300 mb-3">{title}</h3>}
      {children}
    </div>
  );
}
