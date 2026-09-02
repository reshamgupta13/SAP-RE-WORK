"use client";

import { useState } from "react";
import { formatLabel, formatSkillName } from "../../lib/format";
import type { PersonSkill } from "../../lib/types";

export function EvidenceDrawer({ skill }: { skill: PersonSkill }) {
  const [open, setOpen] = useState(false);
  const evidence = skill.evidence ?? [];

  return (
    <>
      <button type="button" className="text-[11px] font-medium text-ocean underline-offset-2 hover:underline" onClick={() => setOpen(true)}>
        {evidence.length ? "View evidence" : "Why this matters"}
      </button>
      {open && (
        <div className="fixed inset-0 z-50 flex items-end justify-center bg-ink/40 p-4 sm:items-center" role="dialog" aria-modal="true">
          <div className="max-h-[85vh] w-full max-w-md overflow-y-auto rounded-xl bg-surface-raised p-5 shadow-lift">
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="kicker">Evidence</p>
                <h3 className="mt-1 font-display text-xl text-ink">{formatSkillName(skill.skill_name || skill.skill_id)}</h3>
              </div>
              <button type="button" className="text-muted" onClick={() => setOpen(false)} aria-label="Close">
                ✕
              </button>
            </div>
            <p className="mt-2 text-xs text-muted">
              This is what can be demonstrated — not a hiring score.
            </p>
            {evidence.length === 0 ? (
              <p className="mt-4 text-sm text-amber">Insufficient evidence</p>
            ) : (
              <ul className="mt-4 space-y-3">
                {evidence.map((ev) => (
                  <li key={ev.id} className="surface-panel p-3">
                    <p className="text-sm font-medium text-ink">{ev.title}</p>
                    <p className="mt-1 text-xs text-muted">{ev.description}</p>
                    <p className="mt-2 font-mono text-[10px] uppercase tracking-wide text-muted">
                      {formatLabel(ev.type)} · {formatLabel(ev.verification_status)}
                      {ev.occurred_on ? ` · ${ev.occurred_on}` : ""}
                    </p>
                  </li>
                ))}
              </ul>
            )}
            {skill.valid_from && (
              <p className="mt-4 text-xs text-muted">Valid from {skill.valid_from}{skill.valid_to ? ` → ${skill.valid_to}` : " → present"}</p>
            )}
          </div>
        </div>
      )}
    </>
  );
}
