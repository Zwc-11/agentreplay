// Shared status palette. One product, consistent states.
export type Status = "success" | "warning" | "failure" | "neutral" | "running";

export const statusColor: Record<Status, string> = {
  success: "#34d399",
  warning: "#fbbf24",
  failure: "#f87171",
  neutral: "#9ca3af",
  running: "#60a5fa",
};
