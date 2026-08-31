"use client";

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
      <section className="rounded-xl border border-dashed border-slate-300 bg-slate-50 p-6 text-sm text-slate-500">
        Proof-of-skill activates after pathway generation.
      </section>
    );
  }

  return (
    <section className="rounded-xl border border-slate-200 bg-white shadow-sm">
      <header className="border-b border-slate-100 px-6 py-4">
        <h2 className="text-lg font-semibold text-slate-900">Proof-of-skill</h2>
        <p className="mt-1 text-sm text-slate-600">
          {String(assessment?.task_description ?? pathway?.proof_of_skill_id ?? "Structured assessment")}
        </p>
        {Boolean(result?.is_demo) && (
          <span className="mt-2 inline-block rounded bg-amber-100 px-2 py-0.5 text-xs font-semibold text-amber-900">
            DEMO SYNTHETIC PROOF
          </span>
        )}
      </header>
      <div className="grid gap-4 p-6 md:grid-cols-2">
        <div>
          <h3 className="text-xs font-semibold uppercase text-slate-500">Rubric</h3>
          <ul className="mt-2 space-y-2 text-sm">
            {(criterionResults.length ? criterionResults : rubric).map((c) => (
              <li key={String(c.id ?? c.criterion)} className="flex justify-between rounded bg-slate-50 px-3 py-2">
                <span>{String(c.criterion ?? c.id)}</span>
                <span className="font-mono text-teal-700">
                  {c.score != null ? Number(c.score).toFixed(2) : "—"}
                </span>
              </li>
            ))}
          </ul>
        </div>
        <div className="rounded-lg bg-slate-900 p-4 text-white">
          <p className="text-xs uppercase text-slate-400">Result</p>
          <p className="mt-2 text-2xl font-semibold">{String(result?.result ?? "PENDING")}</p>
          <p className="mt-2 text-sm text-slate-300">
            Score: {result?.total != null ? String(result.total) : "—"} / threshold 0.70
          </p>
          <p className="mt-4 text-xs text-slate-400">
            Evidence changed → capability reassessed → viability may update.
          </p>
        </div>
      </div>
    </section>
  );
}
