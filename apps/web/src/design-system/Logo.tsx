export function Logo({ size = 22 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <rect x="1.25" y="1.25" width="21.5" height="21.5" rx="6" fill="#13151a" stroke="rgba(255,255,255,0.12)" />
      {/* human path (green) forks to an agent divergence (red) */}
      <path d="M5 9 H11 M11 9 L18 6.5" stroke="#34d399" strokeWidth="1.5" strokeLinecap="round" />
      <path d="M11 9 L17.5 14" stroke="#f87171" strokeWidth="1.5" strokeLinecap="round" strokeDasharray="2 2" />
      <circle cx="5" cy="9" r="1.7" fill="#34d399" />
      <circle cx="11" cy="9" r="1.7" fill="#34d399" />
      <circle cx="18" cy="6.5" r="1.7" fill="#34d399" />
      <circle cx="17.5" cy="14" r="1.9" fill="#f87171" />
    </svg>
  );
}
