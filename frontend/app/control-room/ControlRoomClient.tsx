"use client";

import { useState } from "react";
import { DecisionCard } from "../components/DecisionCard";
import { ExplainPanel } from "../components/ExplainPanel";
import { InterventionSimulatorPanel } from "../components/InterventionSimulator";
import { PipelineStrip } from "../components/PipelineStrip";
import { AppHeader } from "../components/AppShell";

type ControlRoomData = {
  run_id: string;
  system_status: { sap: string; ai_engine: string; pipeline_progress: number };
  active_case: Record<string, unknown>;
  decision_card: Record<string, unknown>;
  pipeline: Array<{ stage: string; status: string }>;
  viability: { assessments?: Array<Record<string, unknown>> };
  pathway: Record<string, unknown> | null;
  proof: { result?: Record<string, unknown> | null };
  interventions: Record<string, unknown>;
  explainability: { reports?: Array<Record<string, unknown>> };
  sap_context: Record<string, unknown>;
  market: Record<string, unknown>;
  employer_readiness: Array<Record<string, unknown>>;
};

export function ControlRoomClient({ data }: { data: ControlRoomData }) {
  const [explainReport, setExplainReport] = useState<Record<string, unknown> | null>(null);

  const dataAnalystViability = data.viability.assessments?.find(
    (v) => v.opportunity_id === "opp-data-analyst",
  );

  const reports = data.explainability.reports ?? [];
  const primaryReport = reports[0];

  return (
    <>
      <AppHeader badge="CHECKPOINT 06 — Control Room" />

      <main className="mx-auto max-w-6xl space-y-6 px-6 py-8">
        <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">System status</h2>
          <dl className="mt-3 grid gap-3 text-sm sm:grid-cols-4">
            <div><dt className="text-slate-500">SAP</dt><dd className="font-medium">{data.system_status.sap}</dd></div>
            <div><dt className="text-slate-500">AI engine</dt><dd className="font-medium">{data.system_status.ai_engine}</dd></div>
            <div>
              <dt className="text-slate-500">Pipeline</dt>
              <dd className="font-medium">{Math.round(data.system_status.pipeline_progress * 100)}%</dd>
            </div>
            <div><dt className="text-slate-500">Run</dt><dd className="font-mono text-xs">{data.run_id}</dd></div>
          </dl>
        </section>

        <section className="rounded-xl border border-slate-200 bg-white p-6">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">Active case</h2>
          <p className="mt-2 text-2xl font-semibold text-slate-900">
            {data.active_case.candidate_name as string} — {data.active_case.target_opportunity as string}
          </p>
          <dl className="mt-4 grid gap-3 text-sm sm:grid-cols-3">
            <div><dt className="text-slate-500">Diagnosis</dt><dd>{data.active_case.current_diagnosis as string}</dd></div>
            <div><dt className="text-slate-500">Viability</dt><dd>{data.active_case.opportunity_viability as string}</dd></div>
            <div><dt className="text-slate-500">Employer</dt><dd>{data.active_case.employer_readiness as string}</dd></div>
          </dl>
        </section>

        <section>
          <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-500">Pipeline</h2>
          <PipelineStrip stages={data.pipeline} />
        </section>

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

        <section className="rounded-xl border border-slate-200 bg-white p-6">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">SAP ecosystem context</h2>
          <dl className="mt-3 grid gap-2 text-sm sm:grid-cols-2">
            {Object.entries(data.sap_context)
              .filter(([k]) => !["raw", "note"].includes(k))
              .map(([k, v]) => (
                <div key={k} className="flex justify-between rounded bg-slate-50 px-3 py-2">
                  <dt className="text-slate-600">{k.replace(/_/g, " ")}</dt>
                  <dd className="font-medium">{String(v)}</dd>
                </div>
              ))}
          </dl>
          <p className="mt-3 text-xs text-slate-500">{data.sap_context.note as string}</p>
        </section>
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
