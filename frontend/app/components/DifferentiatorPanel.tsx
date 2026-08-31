"use client";

type Props = {
  diagnosis?: {
    capability_gaps?: Array<Record<string, unknown>>;
    requirement_diagnoses?: Array<Record<string, unknown>>;
  };
};

const MATCHED_SKILLS = ["sql", "excel", "communication", "data_analysis"];

export function DifferentiatorPanel({ diagnosis }: Props) {
  const gaps = diagnosis?.capability_gaps ?? [];
  const reqs = diagnosis?.requirement_diagnoses ?? [];

  const genuineGap = gaps.find((g) => g.gap_status === "GENUINE_CAPABILITY_GAP");
  const proxies = reqs.filter(
    (r) => r.diagnosis_type === "ELIGIBILITY_PROXY" || r.review_tag === "POTENTIAL_PROXY",
  );
  const constraints = reqs.filter((r) => r.diagnosis_type === "WORKPLACE_CONSTRAINT");

  return (
    <section className="overflow-hidden rounded-2xl border border-slate-200 bg-gradient-to-br from-slate-50 via-white to-slate-100 shadow-sm">
      <div className="grid gap-0 lg:grid-cols-2">
        <div className="border-b border-slate-200 bg-slate-100/80 p-6 lg:border-b-0 lg:border-r">
          <p className="text-xs font-bold uppercase tracking-widest text-slate-500">Traditional hiring</p>
          <ul className="mt-4 space-y-3 text-sm text-slate-600">
            <li className="flex items-center gap-2"><span className="text-red-500">✗</span> 3 years continuous experience</li>
            <li className="flex items-center gap-2"><span className="text-red-500">✗</span> Career gap after caregiving</li>
            <li className="flex items-center gap-2"><span className="text-red-500">✗</span> Premier institute filter</li>
            <li className="flex items-center gap-2"><span className="text-red-500">✗</span> Power BI not evidenced</li>
          </ul>
        </div>
        <div className="p-6">
          <p className="text-xs font-bold uppercase tracking-widest text-teal-700">RE:WORK reasoning</p>
          <p className="mt-2 text-sm font-medium text-slate-800">Task → Capability → Evidence</p>
          <ul className="mt-4 space-y-2 text-sm">
            {MATCHED_SKILLS.map((skill) => (
              <li key={skill} className="flex items-center justify-between rounded-lg bg-white px-3 py-2 ring-1 ring-slate-200">
                <span className="capitalize">{skill.replace("_", " ")}</span>
                <span className="rounded-full bg-emerald-100 px-2 py-0.5 text-xs font-semibold text-emerald-800">✓ MATCHED</span>
              </li>
            ))}
            <li className="flex items-center justify-between rounded-lg bg-white px-3 py-2 ring-1 ring-amber-200">
              <span>Power BI</span>
              <span className="rounded-full bg-amber-100 px-2 py-0.5 text-xs font-semibold text-amber-900">
                △ {genuineGap ? "GENUINE GAP" : "GAP"}
              </span>
            </li>
            {proxies.slice(0, 1).map((p) => (
              <li key={String(p.id)} className="flex items-center justify-between rounded-lg bg-white px-3 py-2 ring-1 ring-violet-200">
                <span className="text-xs">{String(p.requirement_text ?? "Experience requirement").slice(0, 40)}…</span>
                <span className="rounded-full bg-violet-100 px-2 py-0.5 text-xs font-semibold text-violet-900">⚠ PROXY</span>
              </li>
            ))}
            {constraints.slice(0, 1).map((c) => (
              <li key={String(c.id)} className="flex items-center justify-between rounded-lg bg-white px-3 py-2 ring-1 ring-slate-300">
                <span className="text-xs">{String(c.requirement_text ?? "Workplace").slice(0, 40)}…</span>
                <span className="rounded-full bg-slate-200 px-2 py-0.5 text-xs font-semibold text-slate-700">⊘ CONSTRAINT</span>
              </li>
            ))}
          </ul>
          <p className="mt-4 text-sm leading-relaxed text-slate-700">
            The candidate does not fail the job. One genuine capability gap plus requirements that require human review.
          </p>
        </div>
      </div>
    </section>
  );
}
