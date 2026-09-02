import Link from "next/link";
import { fetchCatalogHealth, fetchControlRoom, fetchOrganizations } from "../../lib/api";
import { formatLabel } from "../../lib/format";
import { AppHeader } from "../components/AppShell";
import { OrgContextCard } from "../components/OrgContextCard";
import { SourceBadge } from "../components/SourceBadge";

export default async function EmployerPage({
  searchParams,
}: {
  searchParams: Promise<{ caseId?: string }>;
}) {
  const params = await searchParams;
  const health = await fetchCatalogHealth().catch(() => null);
  const sapMode = health?.source_mode ?? "NOT_CONNECTED";

  if (params.caseId) {
    try {
      const data = await fetchControlRoom(params.caseId);
      const readiness = (data.employer_readiness as Array<Record<string, unknown>>) ?? [];
      const primary = readiness[0];
      const orgs = data.enterprise_context?.domains.organizations ?? [];
      const targetJob = data.enterprise_context?.domains.jobs.find((j) => j.is_target);
      return (
        <div className="rework-atmosphere min-h-screen">
          <AppHeader badge="Employer" activePath="/employer" showCta={false} sapMode={String(data.system_status?.sap ?? sapMode)} liveVerified={data.enterprise_context?.odata_status?.live_verified} />
          <main className="rework-content mx-auto max-w-4xl space-y-6 px-6 py-8">
            <p className="text-sm text-muted">
              What the organization needs to know. <SourceBadge mode={String(data.system_status?.sap)} liveVerified={data.enterprise_context?.odata_status?.live_verified} />
            </p>
            <OrgContextCard organizations={orgs} />
            {targetJob && (
              <section className="surface-card p-6">
                <p className="kicker">From SAP</p>
                <h2 className="section-heading mt-2">{targetJob.job_name}</h2>
                <p className="mt-2 text-sm text-muted">{targetJob.location}</p>
              </section>
            )}
            {primary && (
              <section className="surface-card p-6">
                <p className="kicker">RE:WORK</p>
                <h2 className="section-heading mt-2">Overall: {formatLabel(primary.overall_state)}</h2>
              </section>
            )}
          </main>
        </div>
      );
    } catch {
      /* catalog fallback */
    }
  }

  const orgs = await fetchOrganizations().catch(() => null);
  const items = orgs?.items ?? [];

  return (
    <div className="rework-atmosphere min-h-screen">
      <AppHeader badge="Employer" activePath="/employer" showCta={false} sapMode={sapMode} liveVerified={health?.live_verified} />
      <main className="rework-content mx-auto max-w-4xl space-y-6 px-6 py-8">
        <p className="text-sm text-muted">
          Organizations from SAP. <SourceBadge mode={sapMode} liveVerified={health?.live_verified} />
        </p>
        {items.length === 0 ? (
          <section className="surface-card p-6">
            <p className="text-muted">{orgs?.message || "No organizations are currently available from SAP."}</p>
            <Link href="/workspace" className="btn-primary mt-4 inline-flex">Select a candidate and role</Link>
          </section>
        ) : (
          <OrgContextCard
            organizations={items.map((o) => ({
              org_unit_id: String(o.org_unit_id ?? ""),
              org_unit_name: o.org_unit_name ? String(o.org_unit_name) : undefined,
              parent_org_unit: o.parent_org_unit ? String(o.parent_org_unit) : undefined,
            }))}
          />
        )}
      </main>
    </div>
  );
}
