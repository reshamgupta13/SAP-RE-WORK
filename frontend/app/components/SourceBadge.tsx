export function SourceBadge({ mode }: { mode?: string }) {
  const label = mode ?? "SYNTHETIC";
  const colors: Record<string, string> = {
    LIVE: "bg-emerald-100 text-emerald-800",
    SIMULATED: "bg-amber-100 text-amber-900",
    SYNTHETIC: "bg-slate-100 text-slate-700",
    MOCKED: "bg-purple-100 text-purple-800",
    USER_PROVIDED: "bg-blue-100 text-blue-800",
  };
  return (
    <span
      className={`inline-flex rounded px-1.5 py-0.5 text-[10px] font-medium uppercase tracking-wide ${colors[label] ?? colors.SYNTHETIC}`}
      aria-label={`Source: ${label}`}
    >
      {label}
    </span>
  );
}
