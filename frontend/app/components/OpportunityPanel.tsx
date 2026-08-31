"use client";

export function OpportunityPanel({
  assessments,
}: {
  assessments?: Array<Record<string, unknown>>;
}) {
  const items = assessments ?? [];
  if (!items.length) return null;

  return (
    <section className="rounded-xl border border-slate-200 bg-white shadow-sm">
      <header className="border-b border-slate-100 px-6 py-4">
        <h2 className="text-lg font-semibold text-slate-900">Opportunity viability</h2>
        <p className="mt-1 text-sm text-slate-600">Each role assessed — no opaque ranking score.</p>
      </header>
      <ul className="divide-y divide-slate-100">
        {items.map((o) => {
          const dims = (o.dimensions as Record<string, unknown>) ?? {};
          return (
            <li key={String(o.opportunity_id)} className="px-6 py-4">
              <div className="flex flex-wrap items-start justify-between gap-2">
                <div>
                  <p className="font-semibold text-slate-900">{String(o.opportunity_title ?? o.opportunity_id)}</p>
                  <p className="mt-1 text-sm font-medium text-teal-800">{String(o.viability_state ?? "—")}</p>
                </div>
                {Boolean(o.proof_required) && (
                  <span className="rounded bg-violet-100 px-2 py-0.5 text-xs font-semibold text-violet-900">
                    PROOF REQUIRED
                  </span>
                )}
              </div>
              <dl className="mt-3 grid grid-cols-2 gap-2 text-xs text-slate-600 sm:grid-cols-4">
                {Object.entries(dims).slice(0, 8).map(([k, v]) => (
                  <div key={k}>
                    <dt className="uppercase text-slate-400">{k.replace(/_/g, " ")}</dt>
                    <dd className="font-medium text-slate-800">{String(v)}</dd>
                  </div>
                ))}
              </dl>
            </li>
          );
        })}
      </ul>
    </section>
  );
}
