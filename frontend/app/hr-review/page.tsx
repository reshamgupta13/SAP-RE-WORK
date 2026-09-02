import Link from "next/link";
import { fetchCatalogHealth, fetchControlRoom, fetchHrReviewers } from "../../lib/api";
import { AppHeader } from "../components/AppShell";
import { HrReviewClient } from "./HrReviewClient";

export default async function HrReviewPage({
  searchParams,
}: {
  searchParams: Promise<{ caseId?: string }>;
}) {
  const params = await searchParams;
  if (params.caseId) {
    try {
      const data = await fetchControlRoom(params.caseId);
      return <HrReviewClient data={data} />;
    } catch {
      /* empty */
    }
  }

  const health = await fetchCatalogHealth().catch(() => null);
  const reviewers = await fetchHrReviewers().catch(() => null);
  const items = reviewers?.items ?? [];

  return (
    <div className="rework-atmosphere min-h-screen">
      <AppHeader badge="Human Review" activePath="/hr-review" showCta={false} sapMode={health?.source_mode} liveVerified={health?.live_verified} />
      <main className="rework-content mx-auto max-w-3xl space-y-6 px-6 py-12">
        <p className="kicker">HR reviewers</p>
        <h1 className="section-heading mt-2">Human decision stays with HR</h1>
        <p className="text-sm text-muted">
          Open a case from the workspace to record APPROVE / MODIFY / REJECT / REQUEST_MORE_EVIDENCE.
        </p>
        {items.length === 0 ? (
          <p className="text-muted">{reviewers?.message || "No HR reviewers are currently available from SAP."}</p>
        ) : (
          <ul className="space-y-2">
            {items.map((hr) => (
              <li key={String(hr.hr_id)} className="surface-card p-4">
                <p className="font-medium text-ink">{String(hr.hr_name || hr.hr_id)}</p>
                <p className="text-sm text-muted">{String(hr.hr_role ?? "—")} · {String(hr.hr_status ?? "—")}</p>
              </li>
            ))}
          </ul>
        )}
        <Link href="/workspace" className="btn-primary inline-flex">Open workspace</Link>
      </main>
    </div>
  );
}
