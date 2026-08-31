"use client";

export function SAPContextPanel({ sapContext }: { sapContext?: Record<string, unknown> }) {
  const mode = String(sapContext?.source_mode ?? sapContext?.success_factors ?? "SIMULATED");
  const bundle = (sapContext?.bundle as Record<string, unknown>) ?? {};

  const domains = [
    { key: "workforce_context", label: "Workforce" },
    { key: "skills_context", label: "Skills" },
    { key: "role_context", label: "Role" },
    { key: "learning_context", label: "Learning" },
    { key: "opportunity_context", label: "Opportunity" },
  ];

  return (
    <section className="rounded-xl border border-indigo-200 bg-gradient-to-b from-indigo-50/50 to-white p-4 shadow-sm">
      <h3 className="text-xs font-bold uppercase tracking-widest text-indigo-900">SAP enterprise context</h3>
      <p className="mt-2 text-sm font-semibold text-slate-800">
        Source mode: <span className="rounded bg-indigo-100 px-2 py-0.5 text-indigo-900">{mode}</span>
      </p>
      <ul className="mt-3 space-y-1 text-xs text-slate-600">
        {domains.map((d) => {
          const slice = (bundle[d.key] as Record<string, unknown>) ?? {};
          const status = String(slice.status ?? sapContext?.[d.label.toLowerCase()] ?? "SIMULATED");
          return (
            <li key={d.key} className="flex justify-between rounded bg-white/80 px-2 py-1">
              <span>{d.label}</span>
              <span className="font-medium">{status}</span>
            </li>
          );
        })}
      </ul>
      <p className="mt-3 text-xs leading-relaxed text-slate-600">
        SAP provides enterprise context. RE:WORK provides evidence-backed reasoning. Live adapter replaces simulated only.
      </p>
    </section>
  );
}
