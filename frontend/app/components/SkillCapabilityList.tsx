"use client";

import { formatLabel, formatSkillName, proficiencyBand } from "../../lib/format";
import type { PersonSkill } from "../../lib/types";
import { EvidenceDrawer } from "./EvidenceDrawer";

function barWidth(value?: number) {
  if (value == null) return "0%";
  return `${Math.round(Math.min(1, Math.max(0, value)) * 100)}%`;
}

export function SkillCapabilityList({ skills }: { skills: PersonSkill[] }) {
  if (!skills.length) {
    return <p className="text-sm text-muted">No SAP records available for candidate skills.</p>;
  }

  return (
    <ul className="space-y-4">
      {skills.map((skill) => (
        <li key={skill.skill_id} className="surface-panel p-4">
          <div className="flex flex-wrap items-start justify-between gap-2">
            <div>
              <p className="font-medium text-ink">{formatSkillName(skill.skill_name || skill.skill_id)}</p>
              <p className="mt-0.5 text-xs text-muted">{proficiencyBand(skill.proficiency)}</p>
            </div>
            <span className="font-mono text-xs text-muted">
              {skill.proficiency != null ? skill.proficiency.toFixed(2) : "—"}
            </span>
          </div>
          <div className="proficiency-track mt-3" aria-hidden>
            <div className="proficiency-fill" style={{ width: barWidth(skill.proficiency) }} />
          </div>
          <div className="mt-3 flex flex-wrap items-center gap-2">
            {skill.gap_status && (
              <span className="rounded-full bg-parchment px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-muted">
                {formatLabel(skill.gap_status)}
              </span>
            )}
            <EvidenceDrawer skill={skill} />
          </div>
        </li>
      ))}
    </ul>
  );
}
