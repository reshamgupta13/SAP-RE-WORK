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
import { OrgContextCard } from "../components/OrgContextCard";
import { RequirementFitPanel } from "../components/RequirementFitPanel";
import { SAPContextPanel } from "../components/SAPContextPanel";
import { SAPEnterpriseFlow } from "../components/SAPEnterpriseFlow";
import { SAPJuryPanel } from "../components/SAPJuryPanel";
import { SAPTechnicalTrace } from "../components/SAPTechnicalTrace";
import { SkillCapabilityList } from "../components/SkillCapabilityList";
import { WhatChangedHero } from "../components/WhatChangedHero";
import { AppHeader } from "../components/AppShell";
import { resetDemoCase } from "../../lib/api";
import { formatLabel } from "../../lib/format";
import type { ControlRoomData, ExplainReport } from "../../lib/types";

export function ControlRoomClient({ data: initialData }: { data: ControlRoomData }) {
  const [data] = useState(initialData);
  const [explainReport, setExplainReport] = useState<ExplainReport | null>(null);
  const [resetting, setResetting] = useState(false);
  const isFinale = data.case_id === "case-ananya-finale";

  const dataAnalystViability = data.viability?.assessments?.[0];
  const employer = data.employer_readiness?.[0];
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
    <div className="rework-atmosphere rework-route-texture min-h-screen">
      <AppHeader badge="Control Room" activePath="/control-room" showCta={false} sapMode={String(data.system_status.sap)} liveVerified={data.enterprise_context?.odata_status?.live_verified} />

      <main className="rework-content">
        <div className="mx-auto max-w-7xl space-y-8 px-6 py-10">
          {/* Command center hero */}
          <section className="surface-card overflow-hidden p-8 md:p-10">
            <div className="flex flex-col gap-8 lg:flex-row lg:items-start lg:justify-between">
              <div className="max-w-2xl">
                <p className="kicker">Learning command center</p>
                <h1 className="font-display mt-3 text-3xl font-semibold leading-tight text-ink md:text-4xl">
                  Who could succeed — if we reasoned beyond the résumé?
                </h1>
                <p className="font-body mt-4 text-muted">
                  {caseName} → {target} · Case {data.case_id}
                </p>
              </div>
              <div className="flex flex-col gap-3 sm:flex-row lg:flex-col">
              {isFinale && (
                <button
                  type="button"
                  onClick={handleReset}
                  disabled={resetting}
                  className="btn-primary"
                >
                  {resetting ? "Resetting…" : "Reset regression case"}
                </button>
              )}
                <div className="surface-panel px-4 py-3">
                  <p className="font-mono text-[10px] uppercase tracking-wider text-muted">Pipeline</p>
                  <div className="mt-2 flex items-center gap-3">
                    <div className="progress-track flex-1">
                      <div className="progress-fill" style={{ width: `${progress}%` }} />
                    </div>
                    <span className="font-mono text-sm font-medium text-ink">{progress}%</span>
                  </div>
                </div>
              </div>
            </div>
            <dl className="mt-8 grid gap-4 border-t border-border pt-6 text-sm sm:grid-cols-5">
              {[
                { label: "SAP", value: formatLabel(data.system_status.sap) },
                { label: "AI engine", value: formatLabel(data.system_status.ai_engine) },
                { label: "Viability", value: formatLabel(dataAnalystViability?.viability_state) },
                { label: "Employer", value: formatLabel(employer?.overall_state) },
                { label: "Human", value: formatLabel(data.human_decision_status ?? "PENDING") },
              ].map((item) => (
                <div key={item.label}>
                  <dt className="font-mono text-[10px] uppercase tracking-wider text-muted">{item.label}</dt>
                  <dd className="mt-1 font-medium text-ink">{item.value}</dd>
                </div>
              ))}
            </dl>
          </section>

          <SAPEnterpriseFlow sourceMode={String(data.system_status.sap)} />
          <DifferentiatorPanel diagnosis={data.diagnosis} />
          <WhatChangedHero changes={data.what_changed?.changes} />
          {isFinale && <JuryStoryPanel narrative={narrative as Parameters<typeof JuryStoryPanel>[0]["narrative"]} />}

          {data.pipeline && <PipelineStrip stages={data.pipeline} />}

          <div className="grid min-w-0 gap-8 lg:grid-cols-12">
            <aside className="min-w-0 space-y-6 lg:col-span-3">
              <AgentOrchestratorPanel
                data={(data.agent_orchestrator ?? {}) as Parameters<typeof AgentOrchestratorPanel>[0]["data"]}
              />
              <CaseTimelinePanel timeline={data.timeline} />
              <SAPContextPanel sapContext={data.sap_context} />
              <OrgContextCard organizations={data.enterprise_context?.domains.organizations ?? []} />
              <SAPTechnicalTrace
                rows={data.enterprise_context?.sap_trace}
                writeAvailable={data.enterprise_context?.write_operations?.available}
                writeReason={data.enterprise_context?.write_operations?.reason}
              />
            </aside>

            <div className="min-w-0 space-y-8 lg:col-span-6">
              <DecisionCard
                card={data.decision_card}
                viability={dataAnalystViability}
                pathway={data.pathway}
                proof={data.proof}
                onWhy={() => setExplainReport(primaryReport ?? null)}
              />
              {data.enterprise_context?.domains.person_skills && (
                <section className="surface-card p-6">
                  <p className="kicker">Capability and evidence</p>
                  <h2 className="section-heading mt-2">What can this person demonstrate?</h2>
                  <div className="mt-4">
                    <SkillCapabilityList skills={data.enterprise_context.domains.person_skills} />
                  </div>
                </section>
              )}
              <RequirementFitPanel
                skills={data.enterprise_context?.capability_fit?.skills}
                requirements={data.enterprise_context?.capability_fit?.requirements}
              />
              {data.enterprise_context?.proof_delta?.message && (
                <section className="surface-panel border-sage/30 bg-sage/5 p-4">
                  <p className="text-sm font-medium text-ink">{data.enterprise_context.proof_delta.message}</p>
                </section>
              )}
              <PathwayJourneyPanel pathway={data.pathway} />
              <ProofJourneyPanel proof={data.proof} pathway={data.pathway} />
              <OpportunityPanel assessments={data.viability?.assessments} />
              <InterventionSimulatorPanel
                interventions={data.interventions as Parameters<typeof InterventionSimulatorPanel>[0]["interventions"]}
                baselineState={(data.interventions as { baseline_viability_state?: string }).baseline_viability_state}
              />
              {isFinale && <NegativeCasePanel options={negativeOptions} />}
            </div>

            <aside className="min-w-0 space-y-6 lg:col-span-3">
              <section className="surface-panel overflow-hidden p-4">
                <h3 className="kicker !tracking-[0.08em]">Explainability</h3>
                <p className="mt-2 text-sm text-muted">WHAT · WHY · EVIDENCE · CONFIDENCE · HUMAN DECISION</p>
                <ul className="mt-3 space-y-2">
                  {reports.slice(0, 6).map((r) => (
                    <li key={String(r.what)}>
                      <button
                        type="button"
                        onClick={() => setExplainReport(r as ExplainReport)}
                        className="w-full rounded-lg bg-parchment/50 px-3 py-2 text-left text-xs text-ink transition-colors duration-interaction hover:bg-accent/10 hover:text-accent"
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
            caseId={data.case_id}
            runId={data.run_id}
            decisionCardId={String(data.decision_card?.id ?? "")}
            reviewerId={data.enterprise_context?.domains.hr_reviewer?.hr_id ? String(data.enterprise_context.domains.hr_reviewer.hr_id) : undefined}
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
    </div>
  );
}
