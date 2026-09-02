import Link from "next/link";
import { fetchCandidate, fetchCandidates, fetchCatalogHealth, fetchControlRoom } from "../../lib/api";
import { formatLabel } from "../../lib/format";
import { AppHeader } from "../components/AppShell";
import { MutationNotice } from "../components/ProductMeta";
import { RequirementFitPanel } from "../components/RequirementFitPanel";
import { SkillCapabilityList } from "../components/SkillCapabilityList";
import { SourceBadge } from "../components/SourceBadge";
import type { PersonSkill } from "../../lib/types";

export default async function CandidatePage({
  searchParams,
}: {
  searchParams: Promise<{ userId?: string; caseId?: string }>;
}) {
  const params = await searchParams;
  const health = await fetchCatalogHealth().catch(() => null);
  const sapMode = health?.source_mode ?? "NOT_CONNECTED";

  if (params.caseId) {
    try {
      const data = await fetchControlRoom(params.caseId);
      const enterprise = data.enterprise_context;
      const candidate = enterprise?.domains.candidate ?? {};
      const skills = (enterprise?.domains.person_skills ?? []) as PersonSkill[];
      return (
        <CandidateView
          sapMode={String(data.system_status?.sap ?? sapMode)}
          liveVerified={Boolean(enterprise?.odata_status?.live_verified)}
          candidate={candidate}
          skills={skills}
          writeReason={enterprise?.write_operations?.reason}
          fitSkills={enterprise?.capability_fit?.skills}
          fitReqs={enterprise?.capability_fit?.requirements}
        />
      );
    } catch {
      /* fall through to catalog */
    }
  }

  if (params.userId) {
    const payload = await fetchCandidate(params.userId).catch(() => null);
    const candidate = payload?.candidate ?? {};
    const skills = ((payload?.skills ?? []) as Array<Record<string, unknown>>).map((s) => ({
      ...s,
      evidence: s.evidence_text
        ? [{ title: "Recorded evidence", description: String(s.evidence_text) }]
        : [],
    })) as PersonSkill[];
    return (
      <CandidateView
        sapMode={payload?.source_mode ?? sapMode}
        liveVerified={Boolean(health?.live_verified)}
        candidate={candidate}
        skills={skills}
        writeReason={health?.write_operations?.reason}
        emptyMessage={payload?.message}
      />
    );
  }

  const list = await fetchCandidates().catch(() => null);
  const items = list?.items ?? [];

  return (
    <div className="rework-atmosphere min-h-screen">
      <AppHeader badge="Candidate" activePath="/candidate" showCta={false} sapMode={sapMode} liveVerified={health?.live_verified} />
      <main className="rework-content mx-auto max-w-4xl space-y-6 px-6 py-8">
        <p className="kicker">Select a person</p>
        <h1 className="section-heading mt-2">Candidates from SAP</h1>
        <p className="text-sm text-muted">
          {list?.message || "Choose a candidate to inspect skills and evidence."}{" "}
          <SourceBadge mode={sapMode} liveVerified={health?.live_verified} />
        </p>
        {items.length === 0 ? (
          <section className="surface-card p-6">
            <p className="text-sm text-muted">No candidates are currently available from SAP.</p>
            <Link href="/workspace" className="btn-primary mt-4 inline-flex">
              Open workspace
            </Link>
          </section>
        ) : (
          <ul className="space-y-2">
            {items.map((c) => {
              const id = String(c.user_id ?? "");
              return (
                <li key={id}>
                  <Link href={`/candidate?userId=${encodeURIComponent(id)}`} className="interactive-card block">
                    <p className="font-medium text-ink">{String(c.display_name || id)}</p>
                    <p className="text-sm text-muted">{String(c.current_role ?? "—")}</p>
                  </Link>
                </li>
              );
            })}
          </ul>
        )}
      </main>
    </div>
  );
}

function CandidateView({
  sapMode,
  liveVerified,
  candidate,
  skills,
  writeReason,
  fitSkills,
  fitReqs,
  emptyMessage,
}: {
  sapMode: string;
  liveVerified?: boolean;
  candidate: Record<string, unknown>;
  skills: PersonSkill[];
  writeReason?: string;
  fitSkills?: Parameters<typeof RequirementFitPanel>[0]["skills"];
  fitReqs?: Parameters<typeof RequirementFitPanel>[0]["requirements"];
  emptyMessage?: string | null;
}) {
  const name = `${candidate.first_name ?? ""} ${candidate.last_name ?? ""}`.trim() || String(candidate.display_name ?? "");
  return (
    <div className="rework-atmosphere min-h-screen">
      <AppHeader badge="Candidate" activePath="/candidate" showCta={false} sapMode={sapMode} liveVerified={liveVerified} />
      <main className="rework-content mx-auto max-w-4xl space-y-6 px-6 py-8">
        <p className="text-sm text-muted">
          What RE:WORK understands about this person. <SourceBadge mode={sapMode} liveVerified={liveVerified} />
        </p>
        {!candidate.user_id && !name ? (
          <section className="surface-card p-6">
            <p className="text-sm text-muted">{emptyMessage || "No candidates are currently available from SAP."}</p>
            <Link href="/workspace" className="btn-primary mt-4 inline-flex">Open workspace</Link>
          </section>
        ) : (
          <>
            <section className="surface-card p-6">
              <p className="kicker">From SAP</p>
              <h1 className="section-heading mt-2">{name || "Selected candidate"}</h1>
              <dl className="mt-5 grid gap-4 text-sm sm:grid-cols-2">
                <div>
                  <dt className="text-xs uppercase tracking-wide text-muted">Current role</dt>
                  <dd className="mt-1 text-ink">{String(candidate.current_role ?? "—")}</dd>
                </div>
                <div>
                  <dt className="text-xs uppercase tracking-wide text-muted">Target career</dt>
                  <dd className="mt-1 text-ink">{String(candidate.target_career ?? "—")}</dd>
                </div>
                <div>
                  <dt className="text-xs uppercase tracking-wide text-muted">Location</dt>
                  <dd className="mt-1 text-ink">{String(candidate.location ?? "—")}</dd>
                </div>
                <div>
                  <dt className="text-xs uppercase tracking-wide text-muted">Profile</dt>
                  <dd className="mt-1 text-ink">{formatLabel(candidate.profile_status)}</dd>
                </div>
              </dl>
            </section>
            <section className="surface-card p-6">
              <p className="kicker">From SAP</p>
              <h2 className="section-heading mt-2">Skills and evidence</h2>
              {skills.length === 0 ? (
                <p className="mt-3 text-sm text-muted">Insufficient evidence. No recorded skills for this person in SAP.</p>
              ) : (
                <div className="mt-4">
                  <SkillCapabilityList skills={skills} />
                </div>
              )}
              <div className="mt-4">
                <MutationNotice reason={writeReason} />
              </div>
            </section>
            {fitSkills && <RequirementFitPanel skills={fitSkills} requirements={fitReqs} />}
          </>
        )}
      </main>
    </div>
  );
}
