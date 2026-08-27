type Stage = { stage: string; status: string };

export function PipelineStrip({ stages }: { stages: Stage[] }) {
  return (
    <nav aria-label="Pipeline progress" className="flex flex-wrap gap-2">
      {stages.map((s) => (
        <div
          key={s.stage}
          className={`flex items-center gap-1 rounded-full px-3 py-1 text-xs font-medium ${
            s.status === "completed"
              ? "bg-teal-100 text-teal-900"
              : s.status === "active"
                ? "bg-teal-600 text-white ring-2 ring-teal-300"
                : "bg-slate-100 text-slate-500"
          }`}
        >
          <span aria-hidden>{s.status === "completed" ? "✓" : s.status === "active" ? "●" : "○"}</span>
          {s.stage}
        </div>
      ))}
    </nav>
  );
}
