import Link from "next/link";
import { fetchCatalogHealth, fetchJob, fetchJobs } from "../../lib/api";
import { AppHeader } from "../components/AppShell";
import { SourceBadge } from "../components/SourceBadge";

export default async function OpportunitiesPage({
  searchParams,
}: {
  searchParams: Promise<{ jobId?: string; q?: string }>;
}) {
  const params = await searchParams;
  const health = await fetchCatalogHealth().catch(() => null);
  const sapMode = health?.source_mode ?? "NOT_CONNECTED";

  if (params.jobId) {
    const payload = await fetchJob(params.jobId).catch(() => null);
    const job = payload?.job;
    const requirements = payload?.requirements ?? [];
    const org = payload?.organization;
    return (
      <div className="rework-atmosphere min-h-screen">
        <AppHeader badge="Opportunities" activePath="/opportunities" showCta={false} sapMode={payload?.source_mode ?? sapMode} liveVerified={health?.live_verified} />
        <main className="rework-content mx-auto max-w-4xl space-y-6 px-6 py-8">
          <Link href="/opportunities" className="text-sm text-accent">← All roles</Link>
          {!job ? (
            <p className="text-muted">{payload?.message || "No job found in SAP."}</p>
          ) : (
            <>
              <section className="surface-card p-6">
                <p className="kicker">From SAP</p>
                <h1 className="section-heading mt-2">{String(job.job_name)}</h1>
                <p className="mt-2 text-sm text-muted">{String(job.location ?? job.org_unit_id ?? "—")}</p>
                {job.job_description ? <p className="mt-4 text-sm text-ink">{String(job.job_description)}</p> : null}
              </section>
              {org && (
                <section className="surface-card p-6">
                  <p className="kicker">Organization</p>
                  <h2 className="section-heading mt-2">{String(org.org_unit_name ?? org.org_unit_id)}</h2>
                  {org.parent_org_unit ? <p className="mt-2 text-sm text-muted">Parent: {String(org.parent_org_unit)}</p> : null}
                </section>
              )}
              <section className="surface-card p-6">
                <p className="kicker">From SAP</p>
                <h2 className="section-heading mt-2">Why this role?</h2>
                {requirements.length === 0 ? (
                  <p className="mt-3 text-sm text-muted">{payload?.message || "This role has no recorded skill requirements in SAP."}</p>
                ) : (
                  <ul className="mt-4 space-y-3">
                    {requirements.map((r) => (
                      <li key={`${r.job_id}-${r.skill_id}`} className="surface-panel p-4">
                        <p className="font-medium text-ink">{String(r.skill_name || r.skill_id)}</p>
                        <p className="text-sm text-muted">
                          Required proficiency: {r.required_proficiency == null ? "not recorded" : String(r.required_proficiency)}
                          {" · "}
                          {r.is_mandatory ? "Mandatory" : "Optional"}
                        </p>
                      </li>
                    ))}
                  </ul>
                )}
              </section>
            </>
          )}
        </main>
      </div>
    );
  }

  const list = await fetchJobs(params.q).catch(() => null);
  const jobs = list?.items ?? [];

  return (
    <div className="rework-atmosphere min-h-screen">
      <AppHeader badge="Opportunities" activePath="/opportunities" showCta={false} sapMode={sapMode} liveVerified={health?.live_verified} />
      <main className="rework-content mx-auto max-w-5xl space-y-6 px-6 py-8">
        <div>
          <p className="kicker">Job explorer</p>
          <h1 className="section-heading mt-2">What does this job actually require?</h1>
          <p className="mt-2 text-sm text-muted">
            Roles from SAP. <SourceBadge mode={sapMode} liveVerified={health?.live_verified} />
          </p>
        </div>
        {jobs.length === 0 ? (
          <section className="surface-card p-6">
            <p className="text-muted">{list?.message || "No jobs are currently available from SAP."}</p>
            <Link href="/workspace" className="btn-primary mt-4 inline-flex">Open workspace</Link>
          </section>
        ) : (
          <ul className="grid gap-3 sm:grid-cols-2">
            {jobs.map((job) => {
              const id = String(job.job_id ?? "");
              return (
                <li key={id}>
                  <Link href={`/opportunities?jobId=${encodeURIComponent(id)}`} className="interactive-card block">
                    <h2 className="font-display text-lg font-semibold">{String(job.job_name || id)}</h2>
                    <p className="mt-1 text-sm text-muted">{String(job.location ?? job.org_unit_id ?? "—")}</p>
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
