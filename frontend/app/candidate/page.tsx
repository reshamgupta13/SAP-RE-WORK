import { fetchControlRoom } from "../../lib/api";
import { AppHeader } from "../components/AppShell";
import { SourceBadge } from "../components/SourceBadge";

export default async function CandidatePage() {
  let data = null;
  try {
    data = await fetchControlRoom();
  } catch {
    data = null;
  }

  const gaps = (data?.diagnosis?.capability_gaps as Array<Record<string, unknown>>) ?? [];
  const genuineGaps = gaps.filter((g) => g.gap_status === "GENUINE_CAPABILITY_GAP");
  const pathway = data?.pathway as Record<string, unknown> | null;
  const proof = data?.proof?.result as Record<string, unknown> | null;
  const opportunities = (data?.viability?.assessments as Array<Record<string, unknown>>) ?? [];
  const candidate = data?.candidate as Record<string, unknown> | null;

  return (
    <>
      <AppHeader badge="Candidate View" />
      <main className="mx-auto max-w-4xl space-y-6 px-6 py-8">
        <p className="text-sm text-slate-600">
          Candidate-facing view — HR-only governance details are not shown. <SourceBadge mode="SYNTHETIC" />
        </p>

        <section className="rounded-xl border border-slate-200 bg-white p-6">
          <h2 className="font-semibold text-slate-900">My capability</h2>
          <p className="mt-2 text-sm text-slate-700">
            {candidate?.name as string} — strengths in SQL, Excel, and analytics foundations.
          </p>
        </section>

        <section className="rounded-xl border border-slate-200 bg-white p-6">
          <h2 className="font-semibold text-slate-900">My target</h2>
          <p className="mt-2 text-lg">{data?.active_case?.target_opportunity as string ?? "Data Analyst"}</p>
        </section>

        <section className="rounded-xl border border-slate-200 bg-white p-6">
          <h2 className="font-semibold text-slate-900">My gaps</h2>
          <ul className="mt-2 text-sm text-slate-700">
            {genuineGaps.map((g) => (
              <li key={g.skill_id as string}>{g.skill_id as string}</li>
            ))}
            {!genuineGaps.length && <li>No critical gaps after reassessment</li>}
          </ul>
        </section>

        <section className="rounded-xl border border-slate-200 bg-white p-6">
          <h2 className="font-semibold text-slate-900">My pathway</h2>
          <p className="mt-2 text-sm">{pathway?.why as string ?? "Pathway will appear when generated."}</p>
        </section>

        <section className="rounded-xl border border-slate-200 bg-white p-6">
          <h2 className="font-semibold text-slate-900">My proof</h2>
          <p className="mt-2 text-sm">
            {proof ? `Status: ${proof.result as string}` : "Proof assessment available when pathway is active."}
          </p>
        </section>

        <section className="rounded-xl border border-slate-200 bg-white p-6">
          <h2 className="font-semibold text-slate-900">My opportunities</h2>
          <ul className="mt-2 space-y-2 text-sm">
            {opportunities.map((o) => (
              <li key={o.opportunity_id as string} className="rounded bg-slate-50 px-3 py-2">
                {o.opportunity_id as string}: {o.viability_state as string}
              </li>
            ))}
          </ul>
        </section>

        <section className="rounded-xl border border-teal-200 bg-teal-50 p-6">
          <h2 className="font-semibold text-teal-900">My next best action</h2>
          <p className="mt-2 text-sm text-teal-800">
            Continue pathway milestones and submit proof-of-skill when ready.
          </p>
        </section>
      </main>
    </>
  );
}
