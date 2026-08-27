"use client";

import { useState } from "react";
import { DecisionCard } from "../components/DecisionCard";
import { ExplainPanel } from "../components/ExplainPanel";
import { InterventionSimulatorPanel } from "../components/InterventionSimulator";
import { PipelineStrip } from "../components/PipelineStrip";
import { AppHeader } from "../components/AppShell";

type ControlRoomData = {
  case_id?: string;
  run_id: string;
  human_decision_status?: string;
  system_status: {
    sap: string;
    ai_engine: string;
    pipeline_progress: number;
    sap_health?: Record<string, unknown>;
  };
  active_case: Record<string, unknown>;
  case?: Record<string, unknown>;
  decision_card: Record<string, unknown>;
  pipeline: Array<{ stage: string; status: string }>;
  timeline?: Array<Record<string, unknown>>;
  what_changed?: { changes?: Array<Record<string, unknown>> };
  viability: { assessments?: Array<Record<string, unknown>> };
  pathway: Record<string, unknown> | null;
  proof: { result?: Record<string, unknown> | null };
  interventions: Record<string, unknown>;
  explainability: { reports?: Array<Record<string, unknown>> };
  sap_context: Record<string, unknown>;
  sap_judge_panel?: Record<string, unknown>;
  market: Record<string, unknown>;
  employer_readiness: Array<Record<string, unknown>>;
};

export function ControlRoomClient({ data }: { data: ControlRoomData }) {
  const [explainReport, setExplainReport] = useState<Record<string, unknown> | null>(null);

  const dataAnalystViability = data.viability?.assessments?.find(
    (v) => v.opportunity_id === "opp-data-analyst",
  );

  const reports = data.explainability?.reports ?? [];
  const primaryReport = reports[0];
  const caseName = data.active_case?.candidate_name as string;
  const target = data.active_case?.target_opportunity as string;

  return (
    <>
      <AppHeader badge="CHECKPOINT 07 — Case Control Room" />

      <main className="mx-auto max-w-7xl space-y-6 px-6 py-8">
        <section className="rounded-xl border border-slate-800 bg-slate-900 p-6 text-white shadow-lg">
          <p className="text-xs font-semibold uppercase tracking-widest text-slate-400">RE:WORK Case</p>
          <h2 className="mt-1 text-2xl font-semibold">{caseName} → {target}</h2>
          <dl className="mt-4 grid gap-3 text-sm sm:grid-cols-4">
            <div><dt className="text-slate-400">SAP</dt><dd className="font-medium">{data.system_status.sap}</dd></div>
            <div><dt className="text-slate-400">Engine</dt><dd>{data.system_status.ai_engine}</dd></div>
            <div><dt className="text-slate-400">Case</dt><dd className="font-mono text-xs">{data.case_id}</dd></div>
            <div><dt className="text-slate-400">Human decision</dt><dd>{data.human_decision_status ?? "PENDING"}</dd></div>
          </dl>
        </section>

        <div className="grid gap-6 lg:grid-cols-12">
          <aside className="lg:col-span-3 space-y-4">
            <section className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
              <h3 className="text-xs font-semibold uppercase text-slate-500">Case timeline</h3>
              <ol className="mt-3 space-y-2 text-sm">
                {(data.timeline ?? []).map((e) => (
                  <li key={e.index as number} className="rounded bg-slate-50 px-2 py-1">
                    <span className="text-slate-500">T{e.index}</span> {e.label as string}
                  </li>
                ))}
              </ol>
            </section>
            {data.what_changed?.changes && data.what_changed.changes.length > 0 && (
              <section className="rounded-xl border border-teal-200 bg-teal-50 p-4">
                <h3 className="text-xs font-semibold uppercase text-teal-800">What changed?</h3>
                <ul className="mt-2 space-y-1 text-sm text-teal-900">
                  {data.what_changed.changes.map((c) => (
                    <li key={c.dimension as string}>
                      {c.dimension as string}: {c.before as string} → {c.after as string}
                    </li>
                  ))}
                </ul>
              </section>
            )}
          </aside>

          <div className="lg:col-span-6 space-y-6">
            <PipelineStrip stages={data.pipeline} />
            <DecisionCard
              card={data.decision_card}
              viability={dataAnalystViability}
              pathway={data.pathway}
              proof={data.proof}
              onWhy={() => setExplainReport(primaryReport ?? null)}
            />
            <InterventionSimulatorPanel
              interventions={data.interventions as ControlRoomData["interventions"]}
              baselineState={(data.interventions as { baseline_viability_state?: string }).baseline_viability_state}
            />
          </div>

          <aside className="lg:col-span-3 space-y-4">
            <section className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
              <h3 className="text-xs font-semibold uppercase text-slate-500">Evidence + explainability</h3>
              <p className="mt-2 text-sm text-slate-600">
                Structured factors — not LLM prose. Click WHY? on the decision card.
              </p>
              <ul className="mt-3 space-y-1 text-xs text-slate-600">
                {reports.slice(0, 4).map((r) => (
                  <li key={r.what as string}>{r.what as string}</li>
                ))}
              </ul>
            </section>
            {data.sap_judge_panel && (
              <section className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
                <h3 className="text-xs font-semibold uppercase text-slate-500">SAP vs RE:WORK</h3>
                <p className="mt-2 text-xs text-slate-600">SAP provides workforce context. RE:WORK adds reasoning.</p>
                <p className="mt-2 text-xs font-medium">Mode: {data.sap_judge_panel.source_mode as string}</p>
              </section>
            )}
          </aside>
        </div>

        <footer className="rounded-lg border border-slate-200 bg-white px-4 py-3 text-center text-sm text-slate-600">
          Human decision: {data.human_decision_status ?? "PENDING"} — AI recommendation is not a hiring decision.
        </footer>
      </main>

      <ExplainPanel
        report={explainReport as ExplainPanelReport | null}
        onClose={() => setExplainReport(null)}
      />
    </>
  );
}

type ExplainPanelReport = {
  what: string;
  why: string;
  evidence_refs?: string[];
  confidence_label?: string;
  alternatives?: string[];
  assumptions?: string[];
  human_decision_required?: boolean;
};
