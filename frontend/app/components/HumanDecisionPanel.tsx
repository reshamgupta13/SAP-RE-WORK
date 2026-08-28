"use client";

import { useState } from "react";
import { submitReview } from "../../lib/api";

type HumanDecisionPanelProps = {
  caseId?: string;
  runId: string;
  decisionCardId: string;
  aiRecommendation?: string;
  status: string;
  onUpdated?: (status: string) => void;
};

export function HumanDecisionPanel({
  runId,
  decisionCardId,
  aiRecommendation,
  status,
  onUpdated,
}: HumanDecisionPanelProps) {
  const [current, setCurrent] = useState(status);
  const [loading, setLoading] = useState(false);

  async function decide(action: string) {
    setLoading(true);
    try {
      await submitReview({
        run_id: runId,
        decision_card_id: decisionCardId,
        action,
        reviewer_id: "jury-demo-hr",
        reason: `Jury demo: ${action}`,
      });
      const mapped = action === "APPROVE" ? "APPROVED" : action === "REJECT" ? "REJECTED" : action;
      setCurrent(mapped);
      onUpdated?.(mapped);
    } catch {
      setCurrent("ERROR");
    }
    setLoading(false);
  }

  return (
    <section className="rounded-lg border border-slate-200 bg-white px-4 py-4">
      <div className="grid gap-4 sm:grid-cols-2">
        <div className="rounded-lg bg-slate-50 p-3">
          <p className="text-xs font-semibold uppercase text-slate-500">AI recommendation</p>
          <p className="mt-1 text-sm text-slate-800">{aiRecommendation ?? "See decision card"}</p>
        </div>
        <div className="rounded-lg border-2 border-slate-300 p-3">
          <p className="text-xs font-semibold uppercase text-slate-700">Human decision</p>
          <p className="mt-1 text-sm font-medium text-slate-900">{current}</p>
          {current === "PENDING" && (
            <div className="mt-3 flex flex-wrap gap-2">
              {["APPROVE", "MODIFY", "REQUEST_MORE_EVIDENCE", "REJECT"].map((action) => (
                <button
                  key={action}
                  type="button"
                  disabled={loading}
                  onClick={() => decide(action)}
                  className="rounded bg-slate-800 px-2 py-1 text-xs text-white hover:bg-slate-700 disabled:opacity-50"
                >
                  {action.replace(/_/g, " ")}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
