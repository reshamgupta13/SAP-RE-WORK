"use client";

import { formatLabel, formatOpportunityId } from "../../lib/format";

export function OpportunityPanel({
  assessments,
}: {
  assessments?: Array<Record<string, unknown>>;
}) {
  const items = assessments ?? [];
  if (!items.length) return null;

  return (
    <section className="surface-card">
      <header className="border-b border-border px-6 py-4">
        <p className="kicker">Opportunity intelligence</p>
        <h2 className="section-heading mt-1">Role viability</h2>
        <p className="mt-1 text-sm text-muted">Each role assessed — no opaque ranking score.</p>
      </header>
      <ul className="divide-y divide-border">
        {items.map((o) => {
          const dims = (o.dimensions as Record<string, unknown>) ?? {};
          return (
            <li key={String(o.opportunity_id)} className="px-6 py-4">
              <div className="flex flex-wrap items-start justify-between gap-2">
                <div>
                  <p className="font-semibold text-ink">{formatOpportunityId(String(o.opportunity_title ?? o.opportunity_id))}</p>
                  <p className="mt-1 text-sm font-medium text-accent">{formatLabel(o.viability_state)}</p>
                </div>
                {Boolean(o.proof_required) && (
                  <span className="rounded bg-ocean/10 px-2 py-0.5 text-xs font-semibold text-ocean">
                    PROOF REQUIRED
                  </span>
                )}
              </div>
              <dl className="mt-3 grid grid-cols-2 gap-2 text-xs sm:grid-cols-4">
                {Object.entries(dims).slice(0, 8).map(([k, v]) => (
                  <div key={k}>
                    <dt className="font-mono uppercase text-muted">{k.replace(/_/g, " ")}</dt>
                    <dd className="font-medium text-ink">{String(v)}</dd>
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
