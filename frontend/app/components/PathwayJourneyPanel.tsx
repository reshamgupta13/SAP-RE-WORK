"use client";

export function PathwayJourneyPanel({ pathway }: { pathway: Record<string, unknown> | null }) {
  if (!pathway) {
    return (
      <section className="surface-panel border-dashed p-6 text-center text-sm text-muted">
        Pathway not yet generated for this case stage.
      </section>
    );
  }

  const milestones = (pathway.milestones as Array<Record<string, unknown>>) ?? [];
  const items = (pathway.learning_items as Array<Record<string, unknown>>) ?? [];
  const steps = [
    { id: "gap", label: "Gap identified", detail: String(pathway.target_capabilities ?? "").replace(/,/g, ", ") },
    { id: "pathway", label: "Minimum-effective pathway", detail: String(pathway.why ?? pathway.what ?? "") },
    ...milestones.map((m, idx) => ({
      id: String(m.id ?? `milestone-${idx}`),
      label: String(m.title ?? m.label ?? "Milestone"),
      detail: String(m.practice_task ?? m.description ?? ""),
    })),
    { id: "proof", label: "Proof-of-skill", detail: String(pathway.proof_of_skill_id ?? "Assessment required") },
    { id: "reassess", label: "Reassessment", detail: "Capability diagnosis updated from new evidence" },
  ];

  return (
    <section className="surface-card">
      <header className="border-b border-border px-6 py-4">
        <p className="kicker">Learning pathway</p>
        <h2 className="section-heading mt-1">Minimum-effective route</h2>
        <p className="mt-1 text-sm text-muted">{String(pathway.target_state ?? "")}</p>
        {items[0] && (
          <p className="font-mono-data mt-2">
            SAP Learning: {String(items[0].title)} · source: {String(items[0].source_mode ?? "SIMULATED")}
          </p>
        )}
      </header>
      <ol className="space-y-0 p-6">
        {steps.map((step, i) => (
          <li key={step.id} className="flex gap-4">
            <div className="flex flex-col items-center">
              <span className="flex h-8 w-8 items-center justify-center rounded-full bg-sage text-xs font-bold text-white">
                {i + 1}
              </span>
              {i < steps.length - 1 && <span className="my-1 w-px flex-1 bg-sage/30" />}
            </div>
            <div className="pb-6">
              <p className="font-medium text-ink">{step.label}</p>
              <p className="mt-1 text-sm text-muted">{step.detail}</p>
            </div>
          </li>
        ))}
      </ol>
    </section>
  );
}
