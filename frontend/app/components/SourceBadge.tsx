import { sapStatusLabel } from "../../lib/format";

export function SourceBadge({ mode, liveVerified }: { mode?: string; liveVerified?: boolean }) {
  const label = sapStatusLabel(mode, liveVerified);
  const key = (mode ?? "SIMULATED").toUpperCase();
  const colors: Record<string, string> = {
    LIVE: "bg-sage/15 text-sage border-sage/30",
    SIMULATED: "bg-amber/15 text-amber border-amber/30",
    SYNTHETIC: "bg-parchment text-muted border-border",
    MOCKED: "bg-ocean/10 text-ocean border-ocean/20",
    USER_PROVIDED: "bg-accent/10 text-accent border-accent/20",
    NOT_CONNECTED: "bg-muted/20 text-muted border-border",
    ERROR: "bg-red-100 text-red-800 border-red-200",
  };
  return (
    <span
      className={`inline-flex rounded border px-1.5 py-0.5 font-mono text-[10px] font-medium uppercase tracking-wide ${colors[key] ?? colors.SIMULATED}`}
      aria-label={`Source: ${label}`}
    >
      {label}
    </span>
  );
}
