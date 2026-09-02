export function SAPEnterpriseFlow({ sourceMode }: { sourceMode?: string }) {
  return (
    <section className="surface-card overflow-hidden p-6">
      <p className="kicker">SAP enterprise data</p>
      <h2 className="section-heading mt-2">How enterprise context becomes a decision</h2>
      <ol className="sap-flow mt-6">
        {[
          { title: "SAP data", detail: "Candidate · skills · job · organization · HR" },
          { title: "OData", detail: "Transports the seven-domain contract" },
          { title: "RE:WORK intelligence", detail: "Diagnosis · pathway · proof · opportunity" },
          { title: "Human decision", detail: "HR approves, modifies, or requests evidence" },
        ].map((step, i) => (
          <li key={step.title} className="sap-flow-step">
            <span className="sap-flow-index">{i + 1}</span>
            <div>
              <p className="font-medium text-ink">{step.title}</p>
              <p className="text-xs text-muted">{step.detail}</p>
            </div>
          </li>
        ))}
      </ol>
      <p className="mt-4 text-xs text-muted">Current source: {sourceMode ?? "SIMULATED"} — LIVE only after verified OData access.</p>
    </section>
  );
}
