import { fetchControlRoom } from "../../lib/api";
import { AppHeader } from "../components/AppShell";
import { SourceBadge } from "../components/SourceBadge";

export default async function EmployerPage() {
  let data = null;
  try {
    data = await fetchControlRoom();
  } catch {
    data = null;
  }

  const readiness = (data?.employer_readiness as Array<Record<string, unknown>>) ?? [];
  const primary = readiness.find((e) => e.opportunity_id === "opp-data-analyst") ?? readiness[0];

  return (
    <>
      <AppHeader badge="Employer Readiness" />
      <main className="mx-auto max-w-4xl space-y-6 px-6 py-8">
        <p className="text-sm text-slate-600">
          Two-sided readiness assessment. <SourceBadge mode="SIMULATED" />
        </p>

        {primary && (
          <section className="rounded-xl border border-slate-200 bg-white p-6">
            <h2 className="font-semibold text-slate-900">Overall: {primary.overall_state as string}</h2>
            <ul className="mt-4 space-y-3">
              {(primary.factors as Array<Record<string, unknown>>)?.map((f) => (
                <li key={f.id as string} className="rounded-lg border border-slate-100 p-4">
                  <div className="flex items-center justify-between">
                    <span className="font-medium capitalize">{f.factor as string}</span>
                    <StatusBadge status={f.status as string} />
                  </div>
                  {f.evidence_ref != null && f.evidence_ref !== "" && (
                    <p className="mt-2 text-xs text-slate-500">Evidence: {String(f.evidence_ref)}</p>
                  )}
                </li>
              ))}
            </ul>
          </section>
        )}
      </main>
    </>
  );
}

function StatusBadge({ status }: { status: string }) {
  const colors: Record<string, string> = {
    READY: "bg-emerald-100 text-emerald-800",
    PARTIALLY_READY: "bg-amber-100 text-amber-900",
    NOT_READY: "bg-red-100 text-red-800",
    UNKNOWN: "bg-slate-100 text-slate-600",
  };
  return (
    <span className={`rounded px-2 py-0.5 text-xs font-semibold ${colors[status] ?? colors.UNKNOWN}`}>
      {status}
    </span>
  );
}
