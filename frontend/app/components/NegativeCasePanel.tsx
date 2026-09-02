"use client";

import { useState } from "react";
import { apiUrl } from "../../lib/api-base";
import { formatLabel } from "../../lib/format";

type NegativeOption = { id: string; title: string; outcome: string };

export function NegativeCasePanel({ options }: { options: NegativeOption[] }) {
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(false);

  async function load(scenarioId: string) {
    setLoading(true);
    try {
      const res = await fetch(apiUrl(`/api/demo/negative-case?scenario_id=${scenarioId}`), {
        cache: "no-store",
      });
      setResult(await res.json());
    } catch {
      setResult({ error: "Failed to load negative case" });
    }
    setLoading(false);
  }

  return (
    <section className="surface-card overflow-hidden p-4">
      <h3 className="kicker">Trust signal</h3>
      <p className="mt-1 font-display text-lg font-semibold text-ink">
        Show me a case RE:WORK refuses to force
      </p>
      <p className="mt-1 text-xs text-muted">
        Intelligence system — not a positivity generator.
      </p>
      <div className="mt-3 flex flex-wrap gap-2">
        {options.map((opt) => (
          <button
            key={opt.id}
            type="button"
            disabled={loading}
            onClick={() => load(opt.id)}
            className="rounded-md border border-border bg-surface px-3 py-1.5 text-xs font-medium text-ink transition-colors hover:border-accent hover:bg-accent/5 disabled:opacity-50"
          >
            {opt.id}: {opt.title}
          </button>
        ))}
      </div>
      {result && (
        <div className="mt-3 rounded-lg border border-amber/30 bg-amber/10 p-3 text-sm text-ink">
          <p className="font-semibold">{String(result.title ?? result.scenario_id)}</p>
          <p className="mt-1">
            Outcome:{" "}
            {formatLabel(
              result.outcome ??
                (result.actual as { diagnosis_state?: string } | undefined)?.diagnosis_state,
            )}
          </p>
          <p className="mt-2 text-xs text-muted">{String(result.message ?? "")}</p>
        </div>
      )}
    </section>
  );
}
