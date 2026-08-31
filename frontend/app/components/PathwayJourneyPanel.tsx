"use client";

export function PathwayJourneyPanel({ pathway }: { pathway: Record<string, unknown> | null }) {
  if (!pathway) {
    return (
      <section className="rounded-xl border border-dashed border-slate-300 bg-slate-50 p-6 text-center text-sm text-slate-500">
        Pathway not yet generated for this case stage.
      </section>
    );
  }

  const milestones = (pathway.milestones as Array<Record<string, unknown>>) ?? [];
  const items = (pathway.learning_items as Array<Record<string, unknown>>) ?? [];
  const steps = [
    { label: "Gap identified", detail: String(pathway.target_capabilities ?? "").replace(/,/g, ", ") },
    { label: "Minimum-effective pathway", detail: String(pathway.why ?? pathway.what ?? "") },
    ...milestones.map((m) => ({
      label: String(m.title ?? m.label ?? "Milestone"),
      detail: String(m.practice_task ?? m.description ?? ""),
    })),
    { label: "Proof-of-skill", detail: String(pathway.proof_of_skill_id ?? "Assessment required") },
    { label: "Reassessment", detail: "Capability diagnosis updated from new evidence" },
  ];

  return (
    <section className="rounded-xl border border-slate-200 bg-white shadow-sm">
      <header className="border-b border-slate-100 px-6 py-4">
        <h2 className="text-lg font-semibold text-slate-900">Learning pathway</h2>
        <p className="mt-1 text-sm text-slate-600">{String(pathway.target_state ?? "")}</p>
        {items[0] && (
          <p className="mt-2 text-xs text-slate-500">
            SAP Learning: {String(items[0].title)} · source: {String(items[0].source_mode ?? "SIMULATED")}
          </p>
        )}
      </header>
      <ol className="space-y-0 p-6">
        {steps.map((step, i) => (
          <li key={step.label} className="flex gap-4">
            <div className="flex flex-col items-center">
              <span className="flex h-8 w-8 items-center justify-center rounded-full bg-teal-700 text-xs font-bold text-white">
                {i + 1}
              </span>
              {i < steps.length - 1 && <span className="my-1 w-px flex-1 bg-teal-200" />}
            </div>
            <div className="pb-6">
              <p className="font-medium text-slate-900">{step.label}</p>
              <p className="mt-1 text-sm text-slate-600">{step.detail}</p>
            </div>
          </li>
        ))}
      </ol>
    </section>
  );
}
