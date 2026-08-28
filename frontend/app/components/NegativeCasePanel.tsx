"use client";

import { useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type NegativeOption = { id: string; title: string; outcome: string };

export function NegativeCasePanel({ options }: { options: NegativeOption[] }) {
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(false);

  async function load(scenarioId: string) {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/demo/negative-case?scenario_id=${scenarioId}`, {
        cache: "no-store",
      });
      setResult(await res.json());
    } catch {
      setResult({ error: "Failed to load negative case" });
    }
    setLoading(false);
  }

  return (
    <section className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <h3 className="text-xs font-semibold uppercase text-slate-500">
        Show me a case RE:WORK refuses to force
      </h3>
      <p className="mt-1 text-xs text-slate-500">
        Intelligence system — not a positivity generator.
      </p>
      <div className="mt-3 flex flex-wrap gap-2">
        {options.map((opt) => (
          <button
            key={opt.id}
            type="button"
            disabled={loading}
            onClick={() => load(opt.id)}
            className="rounded-md border border-slate-200 bg-slate-50 px-2 py-1 text-xs hover:bg-slate-100"
          >
            {opt.id}: {opt.title}
          </button>
        ))}
      </div>
      {result && (
        <div className="mt-3 rounded-lg bg-red-50 p-3 text-sm text-red-900">
          <p className="font-semibold">{String(result.title ?? result.scenario_id)}</p>
          <p className="mt-1">Outcome: {String(result.outcome ?? result.actual ? (result.actual as { diagnosis_state?: string }).diagnosis_state : "—")}</p>
          <p className="mt-2 text-xs">{String(result.message ?? "")}</p>
        </div>
      )}
    </section>
  );
}
