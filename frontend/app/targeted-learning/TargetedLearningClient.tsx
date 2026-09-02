"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import {
  fetchCandidates,
  fetchCatalogHealth,
  fetchJobs,
  generateLearningPlan,
  simulateLearningIntervention,
} from "../../lib/api";
import { AppHeader } from "../components/AppShell";

type Plan = Record<string, unknown>;
type Step = Record<string, unknown>;
type TraceLink = { stage: string; label: string; detail: string };

export function TargetedLearningClient() {
  const params = useSearchParams();
  const [candidates, setCandidates] = useState<Array<Record<string, unknown>>>([]);
  const [jobs, setJobs] = useState<Array<Record<string, unknown>>>([]);
  const [candidateId, setCandidateId] = useState(params.get("candidate") ?? "USER002");
  const [roleId, setRoleId] = useState(params.get("role") ?? "JOB002");
  const [plan, setPlan] = useState<Plan | null>(null);
  const [simulation, setSimulation] = useState<Record<string, unknown> | null>(null);
  const [health, setHealth] = useState<Awaited<ReturnType<typeof fetchCatalogHealth>> | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [traceOpen, setTraceOpen] = useState<string | null>(null);
  const [whyOpen, setWhyOpen] = useState(true);

  useEffect(() => {
    void Promise.all([fetchCandidates(), fetchJobs(), fetchCatalogHealth()]).then(([c, j, h]) => {
      setCandidates(c.items ?? []);
      setJobs(j.items ?? []);
      setHealth(h);
    });
  }, []);

  const candidate = useMemo(
    () => candidates.find((c) => String(c.user_id) === candidateId),
    [candidates, candidateId],
  );
  const role = useMemo(() => jobs.find((j) => String(j.job_id) === roleId), [jobs, roleId]);

  async function handleGenerate() {
    setBusy(true);
    setError(null);
    setSimulation(null);
    try {
      const result = await generateLearningPlan(candidateId, roleId);
      setPlan(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to generate learning plan.");
      setPlan(null);
    }
    setBusy(false);
  }

  async function handleSimulate() {
    if (!plan?.learning_plan_id) return;
    setBusy(true);
    try {
      const result = await simulateLearningIntervention(String(plan.learning_plan_id));
      setSimulation(result.simulation as Record<string, unknown>);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Simulation failed.");
    }
    setBusy(false);
  }

  const steps = (plan?.steps as Step[]) ?? [];
  const proofs = (plan?.proof_requirements as Array<Record<string, unknown>>) ?? [];
  const agents = plan?.agents as Record<string, string> | undefined;
  const validation = plan?.validation as Record<string, unknown> | undefined;
  const trace = (plan?.trace as TraceLink[]) ?? [];
  const gapsSufficient = (plan?.gaps_sufficient as string[]) ?? [];
  const gapsAddressed = (plan?.gaps_addressed as string[]) ?? [];
  const noIntervention = plan?.status === "no_intervention_required";
  const sapMode = health?.source_mode ?? "SIMULATED";

  const demoHint =
    candidateId === "USER002" && roleId === "JOB002"
      ? "Best demo pairing: Mahi already has SAP fundamentals — only OData needs focused learning."
      : candidateId === "USER001" && roleId === "JOB001"
        ? "Shivansh meets Java and SQL — HANA is the gap for AI Engineer."
        : candidateId === "USER003" && roleId === "JOB003"
          ? "Resham is strong in Java/SQL — OData is the gap for Full Stack Developer."
          : "Tip: Select Mahi Chauhan + SAP Consultant to see gap-driven OData reskilling.";

  return (
    <div className="rework-atmosphere min-h-screen">
      <AppHeader
        badge="Targeted Learning"
        activePath="/targeted-learning"
        showCta={false}
        sapMode={sapMode}
        liveVerified={health?.live_verified}
      />

      <main className="rework-content mx-auto max-w-5xl space-y-8 px-6 py-10">
        {/* What problem this solves */}
        <section className="surface-card border-sage/20 p-8">
          <p className="kicker">SAP Hackfest · Learning &amp; Development</p>
          <h1 className="font-display mt-2 text-3xl font-semibold text-ink">Targeted Learning</h1>
          <p className="mt-3 max-w-3xl text-base leading-relaxed text-ink">
            <strong>Gap-driven reskilling</strong> — not a generic course catalog. RE:WORK reads SAP workforce
            data (who the person is, what the role needs), finds the <em>actual</em> skill gaps, and recommends
            only the smallest learning path to close them.
          </p>

          <div className="mt-6 grid gap-4 md:grid-cols-2">
            <div className="rounded-lg border border-border bg-surface-elevated p-4">
              <p className="text-xs font-semibold uppercase tracking-wide text-muted">The old way</p>
              <ul className="mt-2 space-y-1.5 text-sm text-muted">
                <li>· Everyone gets the same Java, Python, or SAP courses</li>
                <li>· Learning is not tied to a specific role</li>
                <li>· No proof the person actually learned the skill</li>
                <li>· HR cannot explain why a course was assigned</li>
              </ul>
            </div>
            <div className="rounded-lg border border-sage/30 bg-sage/5 p-4">
              <p className="text-xs font-semibold uppercase tracking-wide text-sage">What RE:WORK resolves</p>
              <ul className="mt-2 space-y-1.5 text-sm text-ink">
                <li>· Compares <strong>person skills</strong> vs <strong>SAP role requirements</strong></li>
                <li>· Recommends learning <strong>only for real gaps</strong> — skips skills already met</li>
                <li>· Uses the <strong>smallest effective</strong> path, not a full retraining program</li>
                <li>· Links every step to <strong>proof-of-skill</strong> so HR can verify readiness</li>
                <li>· AI agents explain <strong>why</strong> each step exists; humans still decide</li>
              </ul>
            </div>
          </div>

          <p className="mt-4 text-xs text-muted">
            Powered by SAP ZREWORK OData (USER, JOB, SKILL) + RE:WORK AI agents (Groq LLM). Learning resources
            come from the RE:WORK prototype catalog — architecture-ready for SAP Learning Hub.
          </p>
        </section>

        <section className="surface-card p-8">
          <p className="kicker">Generate a plan</p>
          <h2 className="section-heading mt-1">Pick a person and a target role</h2>
          <p className="mt-2 text-sm text-muted">{demoHint}</p>

          <div className="mt-6 grid gap-4 sm:grid-cols-2">
            <label className="flex flex-col gap-1 text-sm">
              <span className="font-medium text-ink">Candidate</span>
              <select
                className="rounded-md border border-border bg-surface px-3 py-2"
                value={candidateId}
                onChange={(e) => setCandidateId(e.target.value)}
              >
                {candidates.map((c) => (
                  <option key={String(c.user_id)} value={String(c.user_id)}>
                    {String(c.display_name ?? c.user_id)}
                  </option>
                ))}
              </select>
            </label>
            <label className="flex flex-col gap-1 text-sm">
              <span className="font-medium text-ink">Target role</span>
              <select
                className="rounded-md border border-border bg-surface px-3 py-2"
                value={roleId}
                onChange={(e) => setRoleId(e.target.value)}
              >
                {jobs.map((j) => (
                  <option key={String(j.job_id)} value={String(j.job_id)}>
                    {String(j.job_name ?? j.job_id)}
                  </option>
                ))}
              </select>
            </label>
          </div>

          <div className="mt-6 flex flex-wrap gap-3">
            <button type="button" className="btn-primary" disabled={busy} onClick={handleGenerate}>
              {busy ? "Generating…" : "Generate Targeted Learning Plan"}
            </button>
            {plan && (
              <button type="button" className="btn-secondary" disabled={busy} onClick={handleSimulate}>
                Simulate Intervention
              </button>
            )}
            <Link href="/workspace" className="btn-secondary">
              Open workspace
            </Link>
          </div>
          {error && <p className="mt-4 text-sm text-red-600">{error}</p>}
        </section>

        {plan && (
          <>
            <section className="surface-card p-8">
              <div className="flex flex-wrap items-start justify-between gap-4">
                <div>
                  <p className="kicker">Context</p>
                  <h2 className="section-heading mt-1">
                    {String(plan.candidate_name ?? candidate?.display_name)} →{" "}
                    {String(plan.target_role_title ?? role?.job_name)}
                  </h2>
                  <p className="mt-1 text-sm text-muted">
                    {noIntervention
                      ? "This person already meets the role's SAP skill requirements — no extra courses needed."
                      : "One or more capability gaps were found — a focused learning path is recommended below."}
                  </p>
                </div>
                <span className="rounded-full bg-sage/10 px-3 py-1 text-xs font-medium text-sage">
                  SAP-aligned catalog
                </span>
              </div>

              {noIntervention && (
                <div className="mt-4 rounded-lg border border-sage/30 bg-sage/5 p-4 text-sm text-ink">
                  <p className="font-medium text-sage">No reskilling needed — and that is a good outcome.</p>
                  <p className="mt-1 text-muted">
                    RE:WORK did not assign random training. It checked each required SAP skill against the
                    candidate&apos;s evidence and found no meaningful gap. That is exactly what gap-first learning
                    means: <strong>do not teach what someone already knows.</strong>
                  </p>
                </div>
              )}
            </section>

            <section className="surface-card p-8">
              <button type="button" className="w-full text-left" onClick={() => setWhyOpen(!whyOpen)}>
                <p className="kicker">Why this path?</p>
                <h2 className="section-heading mt-1">
                  {noIntervention ? "Skills already match the role" : "Smallest effective intervention"}
                </h2>
                <p className="mt-1 text-xs text-muted">{whyOpen ? "Click to collapse" : "Click to expand"}</p>
              </button>
              {whyOpen && (
                <div className="mt-4 space-y-4 text-sm leading-relaxed text-muted">
                  <p className="text-ink">{String(plan.why_this_path ?? "")}</p>
                  {gapsSufficient.length > 0 && (
                    <div className="rounded-md bg-surface-elevated p-3">
                      <p className="font-medium text-ink">Skills already sufficient (no learning assigned)</p>
                      <p className="mt-1">{gapsSufficient.join(", ")}</p>
                      <p className="mt-2 text-xs">
                        These capabilities meet or exceed the SAP role requirement based on available evidence.
                      </p>
                    </div>
                  )}
                  {gapsAddressed.length > 0 && (
                    <div className="rounded-md border border-accent/20 bg-accent/5 p-3">
                      <p className="font-medium text-ink">Gaps that need targeted learning</p>
                      <p className="mt-1">{gapsAddressed.join(", ")}</p>
                      <p className="mt-2 text-xs">
                        Each learning step below maps directly to one of these diagnosed gaps.
                      </p>
                    </div>
                  )}
                  {!noIntervention && (
                    <p className="text-xs">
                      Chain: SAP role requirement → person capability → diagnosed gap → learning step →
                      proof-of-skill → reassessment. Every link is inspectable.
                    </p>
                  )}
                </div>
              )}
            </section>

            {steps.length > 0 && (
              <section className="surface-card p-8">
                <p className="kicker">Your learning plan</p>
                <h2 className="section-heading mt-1">Focused steps — only what the gap requires</h2>
                <p className="mt-2 text-sm text-muted">
                  Each step was chosen by AI because it closes a specific SAP capability gap for this role.
                  Steps for skills the person already has were intentionally left out.
                </p>
                <ol className="mt-6 space-y-6">
                  {steps.map((step, idx) => (
                    <li key={String(step.id)} className="border-l-2 border-sage/40 pl-6">
                      <p className="text-xs font-mono uppercase text-muted">Step {idx + 1}</p>
                      <h3 className="mt-1 text-lg font-medium text-ink">{String(step.title)}</h3>
                      <p className="mt-1 text-sm text-muted">Why: {String(step.rationale)}</p>
                      <p className="mt-1 text-xs text-muted">
                        Type: {String(step.step_type)} · ~{String(step.estimated_minutes)} min
                      </p>
                      <button
                        type="button"
                        className="mt-2 text-xs font-medium text-accent"
                        onClick={() => setTraceOpen(traceOpen === String(step.id) ? null : String(step.id))}
                      >
                        Why this?
                      </button>
                      {traceOpen === String(step.id) && (
                        <div className="mt-3 rounded-md bg-surface-elevated p-4 text-sm">
                          {trace.map((t) => (
                            <div key={t.stage} className="py-1">
                              <span className="font-mono text-[10px] uppercase text-muted">{t.stage.replace(/_/g, " ")}</span>
                              <p className="font-medium text-ink">{t.label}</p>
                              <p className="text-muted">{t.detail}</p>
                            </div>
                          ))}
                        </div>
                      )}
                    </li>
                  ))}
                </ol>
              </section>
            )}

            {proofs.length > 0 && (
              <section className="surface-card p-8">
                <p className="kicker">Proof of skill</p>
                <h2 className="section-heading mt-1">{String(proofs[0].proof_title)}</h2>
                <p className="mt-2 text-sm text-muted">
                  Finishing a course is not enough. This task proves the person can actually do the work the role
                  requires. HR reviews the evidence before treating the gap as closed.
                </p>
                <p className="mt-2 text-sm text-muted">{String(proofs[0].proof_description)}</p>
                <ul className="mt-4 space-y-2 text-sm">
                  {((proofs[0].acceptance_criteria as string[]) ?? []).map((c) => (
                    <li key={c} className="flex gap-2">
                      <span className="text-sage">✓</span>
                      <span>{c}</span>
                    </li>
                  ))}
                </ul>
              </section>
            )}

            {agents && (
              <section className="surface-card p-8">
                <p className="kicker">How the AI built this plan</p>
                <h2 className="section-heading mt-1">Four agents, one traceable outcome</h2>
                <p className="mt-2 text-sm text-muted">
                  These agents work together — they do not guess skills or invent courses. Facts come from SAP
                  workforce data; agents recommend and explain.
                </p>
                <ul className="mt-4 space-y-3 text-sm">
                  {[
                    [
                      "Learning Strategist",
                      agents.learning_strategist,
                      "Reads the gap diagnosis and designs the smallest learning path for each missing skill.",
                    ],
                    [
                      "Resource Curator",
                      agents.resource_curator,
                      "Picks learning activities from the SAP-aligned catalog that match each gap.",
                    ],
                    [
                      "Proof Alignment",
                      agents.proof_alignment,
                      "Defines what evidence would convince HR that the skill is truly acquired.",
                    ],
                    [
                      "Deterministic Validator",
                      agents.validator,
                      "Checks that every step maps to a real gap — no unnecessary training, no fake claims.",
                    ],
                  ].map(([name, status, desc]) => (
                    <li key={String(name)} className="flex gap-3">
                      <span
                        className={`mt-0.5 ${status === "completed" || status === "passed" ? "text-sage" : "text-muted"}`}
                      >
                        {status === "completed" || status === "passed" ? "✓" : "○"}
                      </span>
                      <div>
                        <span className="font-medium text-ink">{name}</span>
                        <span className="text-muted"> — {status}</span>
                        <p className="mt-0.5 text-xs text-muted">{desc}</p>
                      </div>
                    </li>
                  ))}
                </ul>
                <p className="mt-3 font-mono text-xs text-muted">Engine: {String(agents.engine_mode ?? "DEMO_FALLBACK")}</p>
                {validation && (
                  <p className="mt-2 text-xs text-muted">
                    Validation: {String(validation.status)} ({((validation.checks as Array<{ name: string }>) ?? []).length} checks)
                  </p>
                )}
              </section>
            )}

            {simulation && (
              <section className="surface-card border-dashed p-8">
                <p className="kicker">What-if intervention</p>
                <h2 className="section-heading mt-1">Simulated projection</h2>
                <dl className="mt-4 grid gap-3 text-sm sm:grid-cols-2">
                  <div>
                    <dt className="text-muted">Gap</dt>
                    <dd className="font-medium">{String(simulation.gap_capability)}</dd>
                  </div>
                  <div>
                    <dt className="text-muted">Intervention</dt>
                    <dd className="font-medium">{String(simulation.intervention_label)}</dd>
                  </div>
                  <div>
                    <dt className="text-muted">Before</dt>
                    <dd>{String(simulation.before_state)}</dd>
                  </div>
                  <div>
                    <dt className="text-muted">After</dt>
                    <dd className="text-sage">{String(simulation.after_state)}</dd>
                  </div>
                </dl>
                <p className="mt-3 text-xs text-muted">{String(simulation.readiness_note ?? "")}</p>
                <p className="mt-2 font-mono text-[10px] uppercase text-muted">SIMULATED PROJECTION — not a guaranteed outcome</p>
              </section>
            )}
          </>
        )}
      </main>
    </div>
  );
}
