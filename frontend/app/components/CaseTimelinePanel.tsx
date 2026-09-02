"use client";

export function CaseTimelinePanel({ timeline }: { timeline?: Array<Record<string, unknown>> }) {
  const entries = timeline ?? [];
  if (!entries.length) return null;

  return (
    <section className="surface-panel p-4">
      <h3 className="kicker">Case timeline</h3>
      <ol className="relative mt-4 space-y-0 border-l-2 border-sage/30 pl-4">
        {entries.map((e, idx) => (
          <li key={String(e.index ?? idx)} className="relative pb-4 last:pb-0">
            <span className="absolute -left-[1.35rem] top-1 h-2.5 w-2.5 rounded-full bg-sage ring-4 ring-surface-raised" />
            <p className="text-sm font-medium text-ink">{String(e.label ?? "")}</p>
            <p className="font-mono-data text-muted">{String(e.event_type ?? "")}</p>
          </li>
        ))}
      </ol>
    </section>
  );
}
