"use client";

import { useState } from "react";
import { formatLabel } from "../../lib/format";

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
    <section className="surface-card overflow-hidden" aria-labelledby="sim-title">
      <header className="border-b border-border px-6 py-4">
        <p className="kicker">What-if analysis</p>
        <h2 id="sim-title" className="section-heading mt-1">What if we change something?</h2>
        <p className="mt-1 text-sm text-muted">
          Current: <strong className="text-ink">{formatLabel(baselineState)}</strong>
        </p>
        <span className="mt-2 inline-block rounded bg-amber/15 px-2 py-0.5 text-xs font-semibold text-amber">
          {formatLabel(interventions.label ?? "SIMULATED PROJECTION")}
        </span>
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
              className={`rounded-lg border px-3 py-2 text-sm transition-all duration-interaction ${
                selected.includes(s.id)
                  ? "border-accent bg-accent/10 text-accent"
                  : "border-border bg-surface-raised text-ink hover:border-accent/50"
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
        <div className="border-t border-border p-4">
          <h3 className="font-mono text-[10px] font-semibold uppercase tracking-wider text-muted">Bundle comparison</h3>
          <div className="mt-3 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
            {bundles.map((b) => (
              <div
                key={b.id}
                className={`min-w-0 rounded-lg border p-3 text-sm ${
                  b.is_minimum_effective ? "border-sage bg-sage/10" : "border-border bg-surface"
                }`}
              >
                <p className="font-medium text-ink">{b.label}</p>
                <p className="mt-1 text-muted">Effort: {b.total_effort_weeks ?? "—"} wk</p>
                <p className="mt-1 break-words font-medium text-accent">
                  → {formatLabel(b.after_viability_state)}
                </p>
                {b.is_minimum_effective && (
                  <p className="mt-2 text-xs font-semibold text-sage">Minimum effective</p>
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
    <div className="min-w-0 rounded-lg border border-border bg-surface p-4">
      <h4 className="font-medium text-ink">{scenario.label}</h4>
      <div className="mt-3 grid grid-cols-2 gap-2 text-sm">
        <div>
          <p className="font-mono text-[10px] uppercase text-muted">Before</p>
          <p className="break-words text-ink">{formatLabel(scenario.before_viability_state)}</p>
        </div>
        <div>
          <p className="font-mono text-[10px] uppercase text-muted">Simulated after</p>
          <p className="break-words font-semibold text-accent">{formatLabel(scenario.after_viability_state)}</p>
        </div>
      </div>
      {effect?.before_state && effect?.after_state && (
        <dl className="mt-3 space-y-1 text-xs text-muted">
          {Object.keys(effect.after_state).map((k) => (
            <div key={k} className="flex justify-between gap-2">
              <dt className="shrink-0">{formatLabel(k)}</dt>
              <dd className="break-words text-right text-ink">
                {String(effect.before_state?.[k])} → {String(effect.after_state?.[k])}
              </dd>
            </div>
          ))}
        </dl>
      )}
      {effect?.assumptions && (
        <ul className="mt-3 list-disc pl-4 text-xs text-muted">
          {effect.assumptions.slice(0, 3).map((a) => (
            <li key={a}>{a}</li>
          ))}
        </ul>
      )}
    </div>
  );
}
