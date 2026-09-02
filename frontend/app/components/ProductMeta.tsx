import { formatLabel } from "../../lib/format";

export function EmptyState({ title, detail }: { title: string; detail: string }) {
  return (
    <div className="surface-panel px-4 py-6 text-center">
      <p className="font-medium text-ink">{title}</p>
      <p className="mt-1 text-sm text-muted">{detail}</p>
    </div>
  );
}

export function MutationNotice({ reason }: { reason?: string }) {
  return (
    <p className="rounded-lg border border-dashed border-border px-3 py-2 text-xs text-muted">
      {reason ?? "Create and update require a verified SAP OData service. Demo evidence is fixture-backed."}
    </p>
  );
}

export function HrIdentityCard({ reviewer }: { reviewer?: Record<string, unknown> | null }) {
  if (!reviewer) return null;
  return (
    <section className="surface-panel p-4">
      <p className="kicker">Reviewer</p>
      <p className="mt-2 font-medium text-ink">{String(reviewer.hr_name)}</p>
      <p className="text-sm text-muted">
        {formatLabel(reviewer.hr_role)} · {formatLabel(reviewer.hr_access_level)}
      </p>
      <p className="mt-1 text-xs text-muted">{String(reviewer.hr_location)}</p>
    </section>
  );
}
