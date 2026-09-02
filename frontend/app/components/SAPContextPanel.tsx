"use client";

import { useState } from "react";
import { formatLabel } from "../../lib/format";

type SapContext = Record<string, unknown>;

function modeBadge(mode: string) {
  const m = mode.toUpperCase();
  if (m === "LIVE") return "bg-emerald/15 text-emerald";
  if (m === "ERROR") return "bg-rose/15 text-rose";
  if (m === "NOT_CONNECTED") return "bg-muted/20 text-muted";
  return "bg-amber/15 text-amber";
}

export function SAPContextPanel({ sapContext }: { sapContext?: SapContext }) {
  const [showTrace, setShowTrace] = useState(false);
  const mode = String(sapContext?.source_mode ?? sapContext?.success_factors ?? "SIMULATED");
  const bundle = (sapContext?.bundle as Record<string, unknown>) ?? {};
  const entityCounts = (sapContext?.entity_counts as Record<string, number>) ?? {};
  const retrievedAt = sapContext?.retrieved_at as string | undefined;

  const domains = [
    { key: "workforce_context", label: "Person", sliceKey: "workforce" },
    { key: "skills_context", label: "Qualifications", sliceKey: "skills" },
    { key: "role_context", label: "Job", sliceKey: "role" },
    { key: "learning_context", label: "Learning", sliceKey: "learning" },
    { key: "opportunity_context", label: "Opportunity", sliceKey: "opportunities" },
  ];

  const fromSap = [
    "Role context",
    "Organization",
    "Recorded skills",
    "Learning history",
    "Job requirements",
  ];

  const reworkStages = [
    "Diagnosis",
    "Pathway",
    "Proof",
    "Viability",
    "Explanation",
    "Human decision",
  ];

  return (
    <section className="surface-panel overflow-hidden border-ocean/20 bg-ocean/5 p-4">
      <div className="flex items-start justify-between gap-2">
        <h3 className="kicker text-ocean">SAP enterprise context</h3>
        <span className={`rounded px-2 py-0.5 font-mono text-[10px] font-semibold uppercase ${modeBadge(mode)}`}>
          {mode === "LIVE" ? "LIVE • VERIFIED" : formatLabel(mode)}
        </span>
      </div>

      <ul className="mt-3 space-y-1 text-xs">
        {domains.map((d) => {
          const slice = (bundle[d.key] as Record<string, unknown>) ?? {};
          const status = String(slice.status ?? sapContext?.[d.sliceKey] ?? "SIMULATED");
          const count = entityCounts[d.key] ?? slice.item_count ?? 0;
          const ok = status === "AVAILABLE";
          return (
            <li key={d.key} className="flex justify-between gap-2 rounded bg-surface-raised/80 px-2 py-1">
              <span className="text-muted">
                {d.label} {ok ? "✓" : ""}
              </span>
              <span className="shrink-0 font-medium text-ink">
                {formatLabel(status)}
                {typeof count === "number" && count > 0 ? ` (${count})` : ""}
              </span>
            </li>
          );
        })}
      </ul>

      {retrievedAt && (
        <p className="mt-2 text-[10px] text-muted">
          Last synchronized: {new Date(retrievedAt).toLocaleTimeString()}
        </p>
      )}

      <div className="mt-4 grid gap-3 border-t border-ocean/10 pt-3 text-xs">
        <div>
          <p className="font-semibold uppercase tracking-wide text-ocean">From SAP</p>
          <ul className="mt-1 space-y-0.5 text-muted">
            {fromSap.map((item) => (
              <li key={item}>— {item}</li>
            ))}
          </ul>
        </div>
        <div className="text-center text-muted">↓</div>
        <div>
          <p className="font-semibold uppercase tracking-wide text-ink">RE:WORK reasoning</p>
          <ul className="mt-1 space-y-0.5 text-muted">
            {reworkStages.map((item) => (
              <li key={item}>→ {item}</li>
            ))}
          </ul>
        </div>
      </div>

      <button
        type="button"
        onClick={() => setShowTrace((v) => !v)}
        className="mt-3 text-[10px] font-medium text-ocean underline-offset-2 hover:underline"
      >
        {showTrace ? "Hide SAP trace" : "SAP → RE:WORK trace"}
      </button>

      {showTrace && (
        <div className="mt-2 rounded border border-ocean/15 bg-surface-raised/60 p-2 font-mono text-[10px] text-muted">
          <p>Source: SAP OData via RE:WORK API</p>
          <p>Mode: {formatLabel(mode)}</p>
          <p className="mt-1">Browser never calls SAP directly.</p>
          {domains.map((d) => {
            const slice = (bundle[d.key] as Record<string, unknown>) ?? {};
            const prov = slice.provenance as Record<string, unknown> | undefined;
            if (!prov && !slice.retrieved_at) return null;
            return (
              <p key={d.key} className="mt-1">
                {d.label}: mapped to canonical model • {String(slice.retrieved_at ?? "")}
              </p>
            );
          })}
        </div>
      )}

      <p className="font-body mt-3 text-xs leading-relaxed text-muted">
        SAP provides enterprise context. RE:WORK provides evidence-backed reasoning.
      </p>
    </section>
  );
}
