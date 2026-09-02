import { formatLabel, formatSkillName } from "../../lib/format";
import type { FitRequirementRow, FitSkillRow } from "../../lib/types";

function statusTone(status?: string) {
  if (status === "MATCHED") return "text-sage bg-sage/10";
  if (status === "GENUINE_CAPABILITY_GAP") return "text-amber bg-amber/10";
  if (status === "INSUFFICIENT_EVIDENCE") return "text-muted bg-parchment";
  return "text-ocean bg-ocean/10";
}

function statusMark(status?: string) {
  if (status === "MATCHED") return "✓";
  if (status === "GENUINE_CAPABILITY_GAP") return "△";
  if (status === "INSUFFICIENT_EVIDENCE") return "○";
  return "⚠";
}

export function RequirementFitPanel({
  skills,
  requirements,
}: {
  skills?: FitSkillRow[];
  requirements?: FitRequirementRow[];
}) {
  if (!skills?.length && !requirements?.length) {
    return <p className="text-sm text-muted">Requirement fit will appear after diagnosis.</p>;
  }

  return (
    <section className="surface-card p-6">
      <p className="kicker">Job requirements vs candidate capabilities</p>
      <h2 className="section-heading mt-2">What does this job actually require?</h2>
      <ul className="mt-5 space-y-3">
        {(skills ?? []).map((row) => (
          <li key={String(row.skill_id)} className="surface-panel p-3">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <span className="font-medium text-ink">{formatSkillName(String(row.skill_name || row.skill_id))}</span>
              <span className={`rounded-full px-2 py-0.5 text-[11px] font-semibold ${statusTone(row.gap_status)}`}>
                {statusMark(row.gap_status)} {formatLabel(row.gap_status)}
              </span>
            </div>
            <p className="mt-2 font-mono text-xs text-muted">
              Candidate {row.candidate_proficiency?.toFixed(2) ?? "—"} · Required {row.required_proficiency?.toFixed(2) ?? "—"}
            </p>
            {row.rationale && <p className="font-body mt-2 text-sm text-muted">{row.rationale}</p>}
          </li>
        ))}
      </ul>
      {(requirements ?? []).length > 0 && (
        <div className="mt-6">
          <p className="text-xs font-semibold uppercase tracking-wide text-muted">Requirements for human review</p>
          <ul className="mt-2 space-y-2">
            {requirements?.map((row) => (
              <li key={row.requirement_text} className="rounded-lg border border-ocean/20 bg-ocean/5 px-3 py-2 text-sm">
                <span className="font-medium text-ink">{row.requirement_text}</span>
                <span className="ml-2 text-xs text-ocean">{formatLabel(row.diagnosis_type)}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}
