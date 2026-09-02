"use client";

import { useState } from "react";
import { submitCaseReview, submitReview } from "../../lib/api";
import { formatLabel } from "../../lib/format";
import type { ControlRoomData } from "../../lib/types";
import { AppHeader } from "../components/AppShell";
import { HrIdentityCard } from "../components/ProductMeta";
import { SourceBadge } from "../components/SourceBadge";

export function HrReviewClient({ data }: { data: ControlRoomData }) {
  const [result, setResult] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const rec = data.human_review?.ai_recommendation ?? data.ai_recommendation ?? {};
  const sapMode = String(data.system_status?.sap ?? "SIMULATED");
  const reviewer = data.enterprise_context?.domains.hr_reviewer;
  const card = data.decision_card ?? {};

  async function act(action: string, extra?: Record<string, unknown>) {
    setLoading(true);
    try {
      const reviewerId = reviewer?.hr_id ? String(reviewer.hr_id) : undefined;
      if (data.case_id) {
        const res = await submitCaseReview(data.case_id, {
          action,
          reviewer_id: reviewerId,
          reason: action === "MODIFY" ? "HR modified the recommendation" : undefined,
        });
        setResult(String((res as { message?: string }).message ?? "Decision recorded."));
      } else {
        const res = await submitReview({
          run_id: data.run_id,
          decision_card_id: data.decision_card.id as string,
          action,
          reviewer_id: reviewerId,
          ...extra,
        });
        setResult(res.message as string);
      }
    } catch {
      setResult("Submission failed");
    }
    setLoading(false);
  }

  return (
    <div className="rework-atmosphere min-h-screen">
      <AppHeader badge="Human Review" activePath="/hr-review" showCta={false} sapMode={sapMode} />
      <main className="rework-content mx-auto max-w-3xl space-y-6 px-6 py-8">
        <p className="text-sm text-muted">
          What should a human review before deciding. <SourceBadge mode={sapMode} />
        </p>

        <HrIdentityCard reviewer={reviewer} />

        <section className="surface-card p-6">
          <p className="kicker">RE:WORK recommendation</p>
          <p className="font-body mt-3 text-lg text-ink">
            {String(card.what ?? rec.recommendation_summary ?? "See decision card")}
          </p>
          <p className="font-body mt-2 text-sm text-muted">{String(card.why ?? rec.rationale ?? "")}</p>
          <dl className="mt-6 grid gap-4 text-sm sm:grid-cols-2">
            <div>
              <dt className="font-mono text-[10px] uppercase tracking-wider text-muted">Confidence</dt>
              <dd className="mt-1 text-ink">{formatLabel(card.confidence ?? rec.confidence_label)}</dd>
            </div>
            <div>
              <dt className="font-mono text-[10px] uppercase tracking-wider text-muted">Human required</dt>
              <dd className="mt-1 text-ink">{card.human_decision_required ? "Yes" : "Yes"}</dd>
            </div>
          </dl>
        </section>

        <section className="surface-card border-2 border-accent/30 p-6">
          <p className="kicker">Human HR decision</p>
          <p className="mt-2 text-sm text-muted">AI recommendation is preserved separately and is not overwritten.</p>
          <div className="mt-4 flex flex-wrap gap-3">
            {["APPROVE", "MODIFY", "REQUEST_MORE_EVIDENCE", "REJECT"].map((action) => (
              <button
                key={action}
                type="button"
                disabled={loading}
                onClick={() =>
                  act(action, action === "MODIFY" ? { modified_pathway: "pathway-hr-adjusted" } : undefined)
                }
                className={action === "APPROVE" ? "btn-primary" : "btn-secondary"}
              >
                {formatLabel(action)}
              </button>
            ))}
          </div>
        </section>

        {result && (
          <p className="surface-panel border-sage/30 bg-sage/5 px-4 py-3 text-sm font-medium text-ink" role="status">
            {result}
          </p>
        )}
      </main>
    </div>
  );
}
