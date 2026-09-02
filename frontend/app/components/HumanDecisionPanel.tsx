"use client";

import { useState } from "react";
import { submitCaseReview, submitReview } from "../../lib/api";
import { formatLabel } from "../../lib/format";

type HumanDecisionPanelProps = {
  caseId?: string;
  runId: string;
  decisionCardId: string;
  aiRecommendation?: string;
  status: string;
  reviewerId?: string;
  onUpdated?: (status: string) => void;
};

export function HumanDecisionPanel({
  caseId,
  runId,
  decisionCardId,
  aiRecommendation,
  status,
  reviewerId,
  onUpdated,
}: HumanDecisionPanelProps) {
  const [current, setCurrent] = useState(status);
  const [loading, setLoading] = useState(false);

  async function decide(action: string) {
    setLoading(true);
    try {
      if (caseId) {
        await submitCaseReview(caseId, {
          action,
          reviewer_id: reviewerId,
          reason: `Human decision: ${action}`,
        });
      } else {
        await submitReview({
          run_id: runId,
          decision_card_id: decisionCardId,
          action,
          reviewer_id: reviewerId,
          reason: `Human decision: ${action}`,
        });
      }
      const mapped = action === "APPROVE" ? "APPROVED" : action === "REJECT" ? "REJECTED" : action;
      setCurrent(mapped);
      onUpdated?.(mapped);
    } catch {
      setCurrent("ERROR");
    }
    setLoading(false);
  }

  return (
    <section className="surface-card overflow-hidden px-4 py-4">
      <div className="grid gap-4 sm:grid-cols-2">
        <div className="surface-panel p-3">
          <p className="kicker">AI recommendation</p>
          <p className="mt-2 text-sm text-ink">{aiRecommendation ?? "See decision card"}</p>
        </div>
        <div className="surface-panel border-2 border-accent/30 p-3">
          <p className="kicker">Human decision</p>
          <p className="mt-2 text-sm font-medium text-ink">{formatLabel(current)}</p>
          {current === "PENDING" && (
            <div className="mt-3 flex flex-wrap gap-2">
              {["APPROVE", "MODIFY", "REQUEST_MORE_EVIDENCE", "REJECT"].map((action) => (
                <button
                  key={action}
                  type="button"
                  disabled={loading}
                  onClick={() => decide(action)}
                  className={action === "APPROVE" ? "btn-primary px-3 py-1 text-xs" : "btn-secondary px-3 py-1 text-xs"}
                >
                  {formatLabel(action)}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
