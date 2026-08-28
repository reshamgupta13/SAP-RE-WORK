"use client";

import { useState } from "react";

type JuryNarrative = {
  rejection_story?: {
    title?: string;
    traditional_filters?: string[];
    rework_discovery?: string[];
  };
  what_can_change?: { title?: string; note?: string };
  what_proves_it?: { title?: string; proof_status?: string; source_mode?: string };
  who_decides?: { title?: string; ai_recommendation?: string };
  evidence_chain_example?: Array<{ step: string; value: string }>;
};

export function JuryStoryPanel({ narrative }: { narrative: JuryNarrative }) {
  const [open, setOpen] = useState(false);
  const story = narrative.rejection_story;

  if (!story) return null;

  return (
    <section className="rounded-xl border-2 border-amber-300 bg-amber-50 p-4 shadow-sm">
      <button
        type="button"
        onClick={() => setOpen(!open)}
        className="w-full text-left"
      >
        <h3 className="text-sm font-bold uppercase tracking-wide text-amber-900">
          {story.title ?? "Why was she rejected?"}
        </h3>
        <p className="mt-1 text-xs text-amber-800">Click to compare traditional filters vs RE:WORK discovery</p>
      </button>

      {open && (
        <div className="mt-4 grid gap-4 md:grid-cols-2">
          <div className="rounded-lg bg-white p-3 ring-1 ring-red-100">
            <h4 className="text-xs font-semibold uppercase text-red-700">Traditional filter</h4>
            <ul className="mt-2 space-y-1 text-sm text-slate-700">
              {(story.traditional_filters ?? []).map((item) => (
                <li key={item}>✗ {item}</li>
              ))}
            </ul>
          </div>
          <div className="rounded-lg bg-white p-3 ring-1 ring-teal-100">
            <h4 className="text-xs font-semibold uppercase text-teal-700">What RE:WORK discovered</h4>
            <ul className="mt-2 space-y-1 text-sm text-slate-700">
              {(story.rework_discovery ?? []).map((item) => (
                <li key={item}>✓ {item}</li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {open && narrative.evidence_chain_example && (
        <div className="mt-4 rounded-lg bg-white p-3">
          <h4 className="text-xs font-semibold uppercase text-slate-500">Evidence chain (Power BI gap)</h4>
          <ol className="mt-2 space-y-1 text-xs text-slate-600">
            {narrative.evidence_chain_example.map((node) => (
              <li key={node.step}>
                <span className="font-medium">{node.step}:</span> {node.value}
              </li>
            ))}
          </ol>
        </div>
      )}
    </section>
  );
}
