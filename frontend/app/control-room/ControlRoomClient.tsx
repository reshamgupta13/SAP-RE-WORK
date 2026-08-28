"use client";

import { useState } from "react";
import { AgentOrchestratorPanel } from "../components/AgentOrchestratorPanel";
import { DecisionCard } from "../components/DecisionCard";
import { ExplainPanel } from "../components/ExplainPanel";
import { InterventionSimulatorPanel } from "../components/InterventionSimulator";
import { SAPJuryPanel } from "../components/SAPJuryPanel";
import { AppHeader } from "../components/AppShell";

type ControlRoomData = {
  case_id?: string;
  run_id: string;
  human_decision_status?: string;
  ai_recommendation?: Record<string, unknown>;
  system_status: {
    sap: string;
    ai_engine: string;
    pipeline_progress: number;
    sap_health?: Record<string, unknown>;
  };
  active_case: Record<string, unknown>;
  decision_card: Record<string, unknown>;
  timeline?: Array<Record<string, unknown>>;
  what_changed?: { changes?: Array<Record<string, unknown>> };
  viability: { assessments?: Array<Record<string, unknown>> };
  pathway: Record<string, unknown> | null;
  proof: { result?: Record<string, unknown> | null };
  interventions: Record<string, unknown>;
  explainability: { reports?: Array<Record<string, unknown>> };
  sap_context: Record<string, unknown>;
  sap_judge_panel?: Record<string, unknown>;
  agent_orchestrator?: Record<string, unknown>;
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
      <AppHeader badge="Inclusive Workforce Intelligence" />

      <main className="mx-auto max-w-7xl space-y-6 px-6 py-8">
        <section className="rounded-xl border border-slate-800 bg-slate-900 p-6 text-white shadow-lg">
          <p className="text-xs font-semibold uppercase tracking-widest text-slate-400">RE:WORK</p>
          <h2 className="mt-1 text-2xl font-semibold">
            {caseName} → {target}
          </h2>
          <dl className="mt-4 grid gap-3 text-sm sm:grid-cols-4">
            <div>
              <dt className="text-slate-400">SAP</dt>
              <dd className="font-medium">{data.system_status.sap}</dd>
            </div>
            <div>
              <dt className="text-slate-400">AI</dt>
              <dd>{data.system_status.ai_engine}</dd>
            </div>
            <div>
              <dt className="text-slate-400">Case</dt>
              <dd className="font-mono text-xs">{data.case_id}</dd>
            </div>
            <div>
              <dt className="text-slate-400">Human decision</dt>
              <dd>{data.human_decision_status ?? "PENDING"}</dd>
            </div>
          </dl>
        </section>

        <section className="rounded-xl border-2 border-teal-600 bg-white p-6 shadow-md">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-teal-800">
            Current opportunity viability
          </h2>
          <p className="mt-2 text-2xl font-semibold text-slate-900">
            {(dataAnalystViability?.viability_state as string) ?? "—"}
          </p>
          <p className="mt-2 text-sm text-slate-600">
            Minimum effective intervention: learning + proof pathway (see WHAT IF below)
          </p>
        </section>

        <div className="grid gap-6 lg:grid-cols-12">
          <aside className="lg:col-span-3 space-y-4">
            <AgentOrchestratorPanel
              data={(data.agent_orchestrator ?? {}) as Parameters<typeof AgentOrchestratorPanel>[0]["data"]}
            />
            {data.what_changed?.changes && data.what_changed.changes.length > 0 && (
              <section className="rounded-xl border border-teal-200 bg-teal-50 p-4">
                <h3 className="text-xs font-semibold uppercase text-teal-800">What changed?</h3>
                <ul className="mt-2 space-y-1 text-sm text-teal-900">
                  {data.what_changed.changes.map((c) => (
                    <li key={String(c.dimension)}>
                      {String(c.dimension)}: {String(c.before)} → {String(c.after)}
                    </li>
                  ))}
                </ul>
              </section>
            )}
          </aside>

          <div className="lg:col-span-6 space-y-6">
            <DecisionCard
              card={data.decision_card}
              viability={dataAnalystViability}
              pathway={data.pathway}
              proof={data.proof}
              onWhy={() => setExplainReport(primaryReport ?? null)}
            />
            <InterventionSimulatorPanel
              interventions={data.interventions}
              baselineState={
                (data.interventions as { baseline_viability_state?: string }).baseline_viability_state
              }
            />
          </div>

          <aside className="lg:col-span-3 space-y-4">
            <section className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
              <h3 className="text-xs font-semibold uppercase text-slate-500">WHY?</h3>
              <p className="mt-2 text-sm text-slate-600">
                Structured evidence chain — click WHY? on the decision card.
              </p>
              <ul className="mt-3 space-y-1 text-xs text-slate-600">
                {reports.slice(0, 5).map((r) => (
                  <li key={String(r.what)}>{String(r.what)}</li>
                ))}
              </ul>
            </section>
            {data.sap_judge_panel && (
              <SAPJuryPanel panel={data.sap_judge_panel as Parameters<typeof SAPJuryPanel>[0]["panel"]} />
            )}
          </aside>
        </div>

        <footer className="rounded-lg border border-slate-200 bg-white px-4 py-4">
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="rounded-lg bg-slate-50 p-3">
              <p className="text-xs font-semibold uppercase text-slate-500">AI recommendation</p>
              <p className="mt-1 text-sm text-slate-800">
                {(data.decision_card?.what as string) ?? "See decision card"}
              </p>
            </div>
            <div className="rounded-lg border-2 border-slate-300 bg-white p-3">
              <p className="text-xs font-semibold uppercase text-slate-700">Human decision</p>
              <p className="mt-1 text-sm font-medium text-slate-900">
                {data.human_decision_status ?? "PENDING"}
              </p>
              <p className="mt-1 text-xs text-slate-500">
                AI recommendation is not a hiring decision.
              </p>
            </div>
          </div>
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
