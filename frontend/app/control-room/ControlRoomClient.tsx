"use client";

import { useState } from "react";
import { AgentOrchestratorPanel } from "../components/AgentOrchestratorPanel";
import { CaseTimelinePanel } from "../components/CaseTimelinePanel";
import { DecisionCard } from "../components/DecisionCard";
import { DifferentiatorPanel } from "../components/DifferentiatorPanel";
import { ExplainPanel } from "../components/ExplainPanel";
import { HumanDecisionPanel } from "../components/HumanDecisionPanel";
import { InterventionSimulatorPanel } from "../components/InterventionSimulator";
import { JuryStoryPanel } from "../components/JuryStoryPanel";
import { NegativeCasePanel } from "../components/NegativeCasePanel";
import { OpportunityPanel } from "../components/OpportunityPanel";
import { PathwayJourneyPanel } from "../components/PathwayJourneyPanel";
import { PipelineStrip } from "../components/PipelineStrip";
import { ProofJourneyPanel } from "../components/ProofJourneyPanel";
import { SAPContextPanel } from "../components/SAPContextPanel";
import { SAPJuryPanel } from "../components/SAPJuryPanel";
import { WhatChangedHero } from "../components/WhatChangedHero";
import { AppHeader } from "../components/AppShell";
import { resetDemoCase } from "../../lib/api";
import type { ControlRoomData, ExplainReport } from "../../lib/types";

export function ControlRoomClient({ data: initialData }: { data: ControlRoomData }) {
  const [data] = useState(initialData);
  const [explainReport, setExplainReport] = useState<ExplainReport | null>(null);
  const [resetting, setResetting] = useState(false);

  const dataAnalystViability = data.viability?.assessments?.find(
    (v) => v.opportunity_id === "opp-data-analyst",
  );
  const employer = data.employer_readiness?.find((e) => e.opportunity_id === "opp-data-analyst");
  const reports = data.explainability?.reports ?? [];
  const primaryReport = reports[0] as ExplainReport | undefined;
  const caseName = data.active_case?.candidate_name as string;
  const target = data.active_case?.target_opportunity as string;
  const narrative = data.jury_narrative ?? {};
  const negativeOptions =
    (narrative.negative_case_options as Array<{ id: string; title: string; outcome: string }>) ?? [];
  const progress = Math.round((data.system_status.pipeline_progress ?? 0) * 100);

  async function handleReset() {
    setResetting(true);
    try {
      await resetDemoCase();
      window.location.reload();
    } catch {
      setResetting(false);
    }
  }

  return (
    <>
      <AppHeader badge="Finale Demo" />

      <main className="rework-grid-bg min-h-screen">
        <div className="mx-auto max-w-7xl space-y-8 px-6 py-10">
          {/* Hero */}
          <section className="relative overflow-hidden rounded-2xl border border-slate-800 bg-slate-950 px-8 py-10 text-white shadow-2xl">
            <div className="relative z-10 max-w-3xl">
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-teal-400">RE:WORK</p>
              <h1 className="font-display mt-2 text-4xl leading-tight md:text-5xl">
                Who could succeed — if we reasoned beyond the résumé?
              </h1>
              <p className="mt-4 text-sm text-slate-300">
                {caseName} → {target} · Case {data.case_id}
              </p>
            </div>
            <div className="relative z-10 mt-6 flex flex-wrap gap-3">
              <button
                type="button"
                onClick={handleReset}
                disabled={resetting}
                className="rounded-lg bg-teal-600 px-4 py-2 text-sm font-semibold text-white hover:bg-teal-500 disabled:opacity-50"
              >
                {resetting ? "Resetting…" : "Reset & replay finale"}
              </button>
              <span className="rounded-lg border border-slate-600 px-4 py-2 text-sm text-slate-300">
                Pipeline {progress}%
              </span>
            </div>
            <dl className="relative z-10 mt-6 grid gap-4 text-sm sm:grid-cols-5">
              <div><dt className="text-slate-500">SAP</dt><dd className="font-semibold">{data.system_status.sap}</dd></div>
              <div><dt className="text-slate-500">AI engine</dt><dd>{data.system_status.ai_engine}</dd></div>
              <div><dt className="text-slate-500">Viability</dt><dd>{String(dataAnalystViability?.viability_state ?? "—")}</dd></div>
              <div><dt className="text-slate-500">Employer</dt><dd>{String(employer?.overall_state ?? "—")}</dd></div>
              <div><dt className="text-slate-500">Human</dt><dd>{data.human_decision_status ?? "PENDING"}</dd></div>
            </dl>
          </section>

          <DifferentiatorPanel diagnosis={data.diagnosis} />
          <WhatChangedHero changes={data.what_changed?.changes} />
          <JuryStoryPanel narrative={narrative as Parameters<typeof JuryStoryPanel>[0]["narrative"]} />

          {data.pipeline && <PipelineStrip stages={data.pipeline} />}

          <div className="grid gap-8 lg:grid-cols-12">
            <aside className="space-y-6 lg:col-span-3">
              <AgentOrchestratorPanel
                data={(data.agent_orchestrator ?? {}) as Parameters<typeof AgentOrchestratorPanel>[0]["data"]}
              />
              <CaseTimelinePanel timeline={data.timeline} />
              <SAPContextPanel sapContext={data.sap_context} />
            </aside>

            <div className="space-y-8 lg:col-span-6">
              <DecisionCard
                card={data.decision_card}
                viability={dataAnalystViability}
                pathway={data.pathway}
                proof={data.proof}
                onWhy={() => setExplainReport(primaryReport ?? null)}
              />
              <PathwayJourneyPanel pathway={data.pathway} />
              <ProofJourneyPanel proof={data.proof} pathway={data.pathway} />
              <OpportunityPanel assessments={data.viability?.assessments} />
              <InterventionSimulatorPanel
                interventions={data.interventions as Parameters<typeof InterventionSimulatorPanel>[0]["interventions"]}
                baselineState={(data.interventions as { baseline_viability_state?: string }).baseline_viability_state}
              />
              <NegativeCasePanel options={negativeOptions} />
            </div>

            <aside className="space-y-6 lg:col-span-3">
              <section className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
                <h3 className="text-xs font-semibold uppercase text-slate-500">Explainability</h3>
                <p className="mt-2 text-sm text-slate-600">WHAT · WHY · EVIDENCE · CONFIDENCE · HUMAN DECISION</p>
                <ul className="mt-3 space-y-2">
                  {reports.slice(0, 6).map((r) => (
                    <li key={String(r.what)}>
                      <button
                        type="button"
                        onClick={() => setExplainReport(r as ExplainReport)}
                        className="w-full rounded-lg bg-slate-50 px-3 py-2 text-left text-xs text-slate-700 hover:bg-teal-50 hover:text-teal-900"
                      >
                        {String(r.what)}
                      </button>
                    </li>
                  ))}
                </ul>
              </section>
              {data.sap_judge_panel && (
                <SAPJuryPanel panel={data.sap_judge_panel as Parameters<typeof SAPJuryPanel>[0]["panel"]} />
              )}
            </aside>
          </div>

          <HumanDecisionPanel
            runId={data.run_id}
            decisionCardId={String(data.decision_card?.id ?? "")}
            aiRecommendation={String(
              data.decision_card?.what ??
                (data.ai_recommendation as { recommendation_summary?: string })?.recommendation_summary ??
                "",
            )}
            status={data.human_decision_status ?? "PENDING"}
          />
        </div>
      </main>

      <ExplainPanel report={explainReport} onClose={() => setExplainReport(null)} />
    </>
  );
}
