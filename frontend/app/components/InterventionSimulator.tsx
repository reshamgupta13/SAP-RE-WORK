"use client";

import { useState } from "react";

type Scenario = {
  id: string;
  label: string;
  before_viability_state?: string;
  after_viability_state?: string;
  effect?: {
    before_state?: Record<string, unknown>;
    after_state?: Record<string, unknown>;
    assumptions?: string[];
    is_simulated_projection?: boolean;
  };
  total_effort_weeks?: number;
};

type Bundle = {
  id: string;
  label: string;
  total_effort_weeks?: number;
  after_viability_state?: string;
  is_minimum_effective?: boolean;
};

export function InterventionSimulatorPanel({
  interventions,
  baselineState,
}: {
  interventions: {
    scenarios?: Scenario[];
    bundles?: Bundle[];
    minimum_effective_intervention?: Scenario | null;
    label?: string;
  };
  baselineState?: string;
}) {
  const scenarios = interventions.scenarios ?? [];
  const bundles = interventions.bundles ?? [];
  const [selected, setSelected] = useState<string[]>([]);

  const toggle = (id: string) => {
    setSelected((prev) => (prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]));
  };

  const compare = scenarios.filter((s) => selected.includes(s.id));

  return (
    <section className="rounded-xl border border-slate-200 bg-white shadow-sm" aria-labelledby="sim-title">
      <header className="border-b border-slate-100 px-6 py-4">
        <h2 id="sim-title" className="text-lg font-semibold text-slate-900">What if we change something?</h2>
        <p className="mt-1 text-sm text-slate-600">
          Current: <strong>{baselineState ?? "—"}</strong>
        </p>
        <p className="mt-2 inline-block rounded bg-amber-100 px-2 py-0.5 text-xs font-semibold uppercase text-amber-900">
          {interventions.label ?? "SIMULATED PROJECTION"}
        </p>
      </header>

      <div className="flex flex-wrap gap-2 p-4">
        {scenarios
          .filter((s) => s.label !== "Current state")
          .slice(0, 6)
          .map((s) => (
            <button
              key={s.id}
              type="button"
              onClick={() => toggle(s.id)}
              className={`rounded-lg border px-3 py-2 text-sm transition ${
                selected.includes(s.id)
                  ? "border-teal-600 bg-teal-50 text-teal-900"
                  : "border-slate-200 bg-white text-slate-700 hover:border-slate-300"
              }`}
            >
              + {s.label}
            </button>
          ))}
      </div>

      <div className="grid gap-4 p-4 md:grid-cols-2">
        {compare.map((s) => (
          <ScenarioCard key={s.id} scenario={s} />
        ))}
      </div>

      {bundles.length > 0 && (
        <div className="border-t border-slate-100 p-4">
          <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-500">Bundle comparison</h3>
          <div className="mt-2 grid gap-2 sm:grid-cols-2 lg:grid-cols-4">
            {bundles.map((b) => (
              <div
                key={b.id}
                className={`rounded-lg border p-3 text-sm ${
                  b.is_minimum_effective ? "border-teal-500 bg-teal-50" : "border-slate-200"
                }`}
              >
                <p className="font-medium text-slate-900">{b.label}</p>
                <p className="text-slate-600">Effort: {b.total_effort_weeks ?? "—"} wk</p>
                <p className="text-slate-600">→ {b.after_viability_state}</p>
                {b.is_minimum_effective && (
                  <p className="mt-1 text-xs font-semibold text-teal-700">Minimum effective</p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </section>
  );
}

function ScenarioCard({ scenario }: { scenario: Scenario }) {
  const effect = scenario.effect;
  return (
    <div className="rounded-lg border border-slate-200 p-4">
      <h4 className="font-medium text-slate-900">{scenario.label}</h4>
      <div className="mt-3 grid grid-cols-2 gap-2 text-sm">
        <div>
          <p className="text-xs text-slate-500">Before</p>
          <p>{scenario.before_viability_state}</p>
        </div>
        <div>
          <p className="text-xs text-slate-500">Simulated after</p>
          <p className="font-semibold text-teal-700">{scenario.after_viability_state}</p>
        </div>
      </div>
      {effect?.before_state && effect?.after_state && (
        <dl className="mt-3 space-y-1 text-xs text-slate-600">
          {Object.keys(effect.after_state).map((k) => (
            <div key={k} className="flex justify-between gap-2">
              <dt>{k}</dt>
              <dd>
                {String(effect.before_state?.[k])} → {String(effect.after_state?.[k])}
              </dd>
            </div>
          ))}
        </dl>
      )}
      {effect?.assumptions && (
        <ul className="mt-3 list-disc pl-4 text-xs text-slate-500">
          {effect.assumptions.slice(0, 3).map((a) => (
            <li key={a}>{a}</li>
          ))}
        </ul>
      )}
    </div>
  );
}
