"use client";

export function CaseTimelinePanel({ timeline }: { timeline?: Array<Record<string, unknown>> }) {
  const entries = timeline ?? [];
  if (!entries.length) return null;

  return (
    <section className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <h3 className="text-xs font-semibold uppercase tracking-widest text-slate-500">Case timeline</h3>
      <ol className="relative mt-4 space-y-0 border-l-2 border-teal-200 pl-4">
        {entries.map((e, idx) => (
          <li key={String(e.index ?? idx)} className="relative pb-4 last:pb-0">
            <span className="absolute -left-[1.35rem] top-1 h-2.5 w-2.5 rounded-full bg-teal-600 ring-4 ring-white" />
            <p className="text-sm font-medium text-slate-900">{String(e.label ?? "")}</p>
            <p className="text-xs text-slate-500">{String(e.event_type ?? "")}</p>
          </li>
        ))}
      </ol>
    </section>
  );
}
