export function OrgContextCard({
  organizations,
}: {
  organizations: Array<Record<string, unknown>>;
}) {
  if (!organizations.length) {
    return <p className="text-sm text-muted">No organization context available.</p>;
  }
  const root = organizations.find((o) => !o.parent_org_unit) ?? organizations[0];
  const child = organizations.find((o) => o.parent_org_unit === root.org_unit_id);

  return (
    <section className="surface-card p-6">
      <p className="kicker">Organization</p>
      <h2 className="section-heading mt-2">Where this opportunity sits</h2>
      <ol className="mt-4 space-y-2 text-sm">
        <li className="font-medium text-ink">{String(root.org_unit_name)}</li>
        {child && (
          <li className="border-l border-border pl-4 text-muted">
            {String(child.org_unit_name)}
            {child.location ? ` · ${String(child.location)}` : ""}
          </li>
        )}
      </ol>
    </section>
  );
}
