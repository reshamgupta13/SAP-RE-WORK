"use client";

export function WhatChangedHero({ changes }: { changes?: Array<Record<string, unknown>> }) {
  if (!changes?.length) return null;

  return (
    <section className="surface-card border-2 border-sage/40 bg-gradient-to-r from-parchment/80 to-surface p-6 md:p-8">
      <h2 className="kicker text-sage">What changed?</h2>
      <p className="font-body mt-2 text-sm text-muted">
        The recommendation changed because new evidence changed the capability diagnosis — not because AI &quot;fixed&quot; the candidate.
      </p>
      <div className="mt-4 grid gap-4 sm:grid-cols-2">
        {changes.map((c) => (
          <div key={String(c.dimension)} className="surface-panel p-4">
            <p className="font-mono text-[10px] uppercase tracking-wider text-sage">{String(c.dimension)}</p>
            <p className="mt-2 text-sm text-muted">{String(c.before)}</p>
            <p className="mt-1 font-display text-lg font-semibold text-ink">→ {String(c.after)}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
