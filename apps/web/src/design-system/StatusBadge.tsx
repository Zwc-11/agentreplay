import { statusColor, type Status } from "./tokens";

export function StatusBadge({ status, label }: { status: Status; label: string }) {
  return (
    <span
      className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs"
      style={{ color: statusColor[status], background: `${statusColor[status]}1a` }}
    >
      <span className="w-1.5 h-1.5 rounded-full" style={{ background: statusColor[status] }} />
      {label}
    </span>
  );
}
