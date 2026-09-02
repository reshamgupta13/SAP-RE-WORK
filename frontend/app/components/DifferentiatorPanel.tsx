"use client";

import { formatSkillName } from "../../lib/format";

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
    <section className="surface-card overflow-hidden">
      <div className="grid gap-0 lg:grid-cols-2">
        <div className="border-b border-border bg-parchment/40 p-6 lg:border-b-0 lg:border-r">
          <p className="kicker">Traditional hiring</p>
          <ul className="mt-4 space-y-3 text-sm text-muted">
            <li className="flex items-center gap-2"><span className="text-amber">✗</span> 3 years continuous experience</li>
            <li className="flex items-center gap-2"><span className="text-amber">✗</span> Career gap after caregiving</li>
            <li className="flex items-center gap-2"><span className="text-amber">✗</span> Premier institute filter</li>
            <li className="flex items-center gap-2"><span className="text-amber">✗</span> Power BI not evidenced</li>
          </ul>
        </div>
        <div className="p-6">
          <p className="kicker text-sage">RE:WORK reasoning</p>
          <p className="mt-2 text-sm font-medium text-ink">Task → Capability → Evidence</p>
          <ul className="mt-4 space-y-2 text-sm">
            {MATCHED_SKILLS.map((skill) => (
              <li key={skill} className="flex items-center justify-between rounded-lg bg-surface px-3 py-2 ring-1 ring-border">
                <span>{formatSkillName(skill)}</span>
                <span className="rounded-full bg-sage/15 px-2 py-0.5 text-xs font-semibold text-sage">✓ Matched</span>
              </li>
            ))}
            <li className="flex items-center justify-between rounded-lg bg-surface px-3 py-2 ring-1 ring-amber/30">
              <span>Power BI</span>
              <span className="rounded-full bg-amber/15 px-2 py-0.5 text-xs font-semibold text-amber">
                △ {genuineGap ? "Genuine gap" : "Gap"}
              </span>
            </li>
            {proxies.slice(0, 1).map((p) => (
              <li key={String(p.id)} className="flex items-center justify-between gap-2 rounded-lg bg-surface px-3 py-2 ring-1 ring-ocean/20">
                <span className="min-w-0 flex-1 truncate text-xs">{String(p.requirement_text ?? "Experience requirement")}</span>
                <span className="shrink-0 rounded-full bg-ocean/10 px-2 py-0.5 text-xs font-semibold text-ocean">⚠ Proxy</span>
              </li>
            ))}
            {constraints.slice(0, 1).map((c) => (
              <li key={String(c.id)} className="flex items-center justify-between gap-2 rounded-lg bg-surface px-3 py-2 ring-1 ring-border">
                <span className="min-w-0 flex-1 truncate text-xs">{String(c.requirement_text ?? "Workplace")}</span>
                <span className="shrink-0 rounded-full bg-parchment px-2 py-0.5 text-xs font-semibold text-muted">⊘ Constraint</span>
              </li>
            ))}
          </ul>
          <p className="font-body mt-4 text-sm leading-relaxed text-muted">
            The candidate does not fail the job. One genuine capability gap plus requirements that require human review.
          </p>
        </div>
      </div>
    </section>
  );
}
