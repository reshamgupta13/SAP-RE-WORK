type SAPJuryPanelData = {
  title?: string;
  what_sap_provides?: string[];
  what_rework_adds?: string[];
  connected_by?: string;
  source_mode?: string;
  configured?: boolean;
  healthy?: boolean;
};

export function SAPJuryPanel({ panel }: { panel: SAPJuryPanelData }) {
  return (
    <section className="rounded-xl border border-indigo-200 bg-indigo-50/40 p-4 shadow-sm">
      <h3 className="text-xs font-semibold uppercase text-indigo-900">
        {panel.title ?? "WHY SAP + RE:WORK?"}
      </h3>
      <p className="mt-2 text-center text-xs font-medium text-indigo-700">
        Connected by {panel.connected_by ?? "agentic orchestration"}
      </p>
      <div className="mt-3 grid gap-3 text-xs">
        <div className="rounded-lg bg-white p-3">
          <p className="font-semibold text-slate-800">SAP</p>
          <ul className="mt-2 space-y-1 text-slate-600">
            {(panel.what_sap_provides ?? []).map((item) => (
              <li key={item}>✓ {item}</li>
            ))}
          </ul>
        </div>
        <div className="rounded-lg bg-white p-3">
          <p className="font-semibold text-teal-800">RE:WORK</p>
          <ul className="mt-2 space-y-1 text-slate-600">
            {(panel.what_rework_adds ?? []).map((item) => (
              <li key={item}>✓ {item}</li>
            ))}
          </ul>
        </div>
      </div>
      <p className="mt-3 text-center text-xs font-medium text-slate-700">
        Mode: {panel.source_mode ?? "SIMULATED"}
      </p>
    </section>
  );
}
