"use client";

import { formatLabel } from "../../lib/format";

export function ProofJourneyPanel({
  proof,
  pathway,
}: {
  proof: { result?: Record<string, unknown> | null; assessment?: Record<string, unknown> | null };
  pathway: Record<string, unknown> | null;
}) {
  const assessment = proof.assessment;
  const result = proof.result;
  const rubric = (assessment?.rubric_criteria as Array<Record<string, unknown>>) ?? [];
  const criterionResults = (result?.criterion_results as Array<Record<string, unknown>>) ?? [];

  if (!assessment && !result) {
    return (
      <section className="surface-panel border-dashed p-6 text-center text-sm text-muted">
        Proof-of-skill activates after pathway generation.
      </section>
    );
  }

  return (
    <section className="surface-card overflow-hidden">
      <header className="border-b border-border px-6 py-4">
        <p className="kicker">Checkpoint</p>
        <h2 className="section-heading mt-1">Proof-of-skill</h2>
        <p className="mt-1 text-sm text-muted">
          {String(assessment?.task_description ?? pathway?.proof_of_skill_id ?? "Structured assessment")}
        </p>
        {Boolean(result?.is_demo) && (
          <span className="mt-2 inline-block rounded bg-amber/15 px-2 py-0.5 text-xs font-semibold text-amber">
            Demo synthetic proof
          </span>
        )}
      </header>
      <div className="grid gap-4 p-6 md:grid-cols-2">
        <div>
          <h3 className="font-mono text-[10px] font-semibold uppercase tracking-wider text-muted">Rubric</h3>
          <ul className="mt-2 space-y-2 text-sm">
            {(criterionResults.length ? criterionResults : rubric).map((c) => (
              <li
                key={String(c.id ?? c.criterion)}
                className="flex items-center justify-between gap-3 rounded-lg bg-surface px-3 py-2 ring-1 ring-border"
              >
                <span className="font-medium text-ink">{String(c.criterion ?? c.id)}</span>
                <span className="shrink-0 font-mono text-accent">
                  {c.score != null ? Number(c.score).toFixed(2) : "—"}
                </span>
              </li>
            ))}
          </ul>
        </div>
        <div className="rounded-lg p-4" style={{ backgroundColor: "var(--color-brand)", color: "var(--color-brand-text)" }}>
          <p className="font-mono text-[10px] uppercase tracking-wider opacity-70">Result</p>
          <p className="mt-2 text-2xl font-semibold">{formatLabel(result?.result ?? "PENDING")}</p>
          <p className="mt-2 text-sm opacity-80">
            Score: {result?.total != null ? String(result.total) : "—"} / threshold 0.70
          </p>
          <p className="mt-4 text-xs opacity-70">
            Evidence changed → capability reassessed → viability may update.
          </p>
        </div>
      </div>
    </section>
  );
}
