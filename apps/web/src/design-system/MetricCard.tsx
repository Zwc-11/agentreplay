export function MetricCard({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="glass p-4" aria-label={`${label}: ${value}`}>
      <div className="text-xs uppercase tracking-wide text-gray-500">{label}</div>
      <div className="mt-1 text-2xl font-semibold text-gray-100">{value}</div>
    </div>
  );
}
