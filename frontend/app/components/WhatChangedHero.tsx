"use client";

export function WhatChangedHero({ changes }: { changes?: Array<Record<string, unknown>> }) {
  if (!changes?.length) return null;

  return (
    <section className="rounded-2xl border-2 border-teal-600 bg-gradient-to-r from-teal-950 to-slate-900 p-6 text-white shadow-lg">
      <h2 className="text-sm font-bold uppercase tracking-widest text-teal-300">What changed?</h2>
      <p className="mt-2 text-sm text-teal-100">
        The recommendation changed because new evidence changed the capability diagnosis — not because AI &quot;fixed&quot; the candidate.
      </p>
      <div className="mt-4 grid gap-4 sm:grid-cols-2">
        {changes.map((c) => (
          <div key={String(c.dimension)} className="rounded-lg bg-white/10 p-4 backdrop-blur">
            <p className="text-xs uppercase text-teal-300">{String(c.dimension)}</p>
            <p className="mt-2 text-sm text-slate-300">{String(c.before)}</p>
            <p className="mt-1 text-lg font-semibold text-white">→ {String(c.after)}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
