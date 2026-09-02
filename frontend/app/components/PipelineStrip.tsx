import { formatLabel } from "../../lib/format";

type Stage = { stage: string; status: string };

export function PipelineStrip({ stages }: { stages: Stage[] }) {
  return (
    <nav aria-label="Pipeline progress" className="flex flex-wrap gap-2">
      {stages.map((s) => (
        <div
          key={s.stage}
          className={`flex items-center gap-1 rounded-full px-3 py-1 text-xs font-medium ${
            s.status === "completed"
              ? "bg-sage/15 text-sage"
              : s.status === "active"
                ? "text-white"
                : "bg-parchment text-muted"
          }`}
          style={
            s.status === "active"
              ? { backgroundColor: "var(--color-brand)", color: "var(--color-brand-text)" }
              : undefined
          }
        >
          <span aria-hidden>{s.status === "completed" ? "✓" : s.status === "active" ? "●" : "○"}</span>
          {formatLabel(s.stage)}
        </div>
      ))}
    </nav>
  );
}
