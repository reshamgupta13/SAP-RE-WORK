"use client";

import { useState } from "react";
import { submitReview } from "../../lib/api";
import { AppHeader } from "../components/AppShell";
import { SourceBadge } from "../components/SourceBadge";

type HrReviewProps = {
  data: {
    run_id: string;
    decision_card: Record<string, unknown>;
    human_review: {
      ai_recommendation?: Record<string, unknown>;
      decision_card_id?: string;
    };
  };
};

export function HrReviewClient({ data }: HrReviewProps) {
  const [result, setResult] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const rec = data.human_review.ai_recommendation ?? {};

  async function act(action: string, extra?: Record<string, unknown>) {
    setLoading(true);
    try {
      const res = await submitReview({
        run_id: data.run_id,
        decision_card_id: data.decision_card.id as string,
        action,
        reviewer_id: "hr-demo",
        ...extra,
      });
      setResult(res.message as string);
    } catch {
      setResult("Submission failed");
    }
    setLoading(false);
  }

  return (
    <>
      <AppHeader badge="Human Review" />
      <main className="mx-auto max-w-3xl space-y-6 px-6 py-8">
        <p className="text-sm text-slate-600">
          AI recommendation generated — not a hiring decision. <SourceBadge mode="USER_PROVIDED" />
        </p>

        <section className="rounded-xl border border-slate-200 bg-white p-6">
          <h2 className="text-sm font-semibold uppercase text-slate-500">AI recommendation</h2>
          <p className="mt-2 text-slate-900">{rec.recommendation_summary as string}</p>

          <dl className="mt-4 space-y-2 text-sm">
            <div><dt className="text-slate-500">Confidence</dt><dd>{rec.confidence_label as string}</dd></div>
            <div>
              <dt className="text-slate-500">Risks</dt>
              <dd>{((rec.risks as string[]) ?? []).join("; ") || "—"}</dd>
            </div>
            <div>
              <dt className="text-slate-500">Alternatives</dt>
              <dd>{((rec.alternatives as string[]) ?? []).join("; ") || "—"}</dd>
            </div>
          </dl>
        </section>

        <section className="flex flex-wrap gap-3">
          {["APPROVE", "MODIFY", "REQUEST_MORE_EVIDENCE", "REJECT"].map((action) => (
            <button
              key={action}
              type="button"
              disabled={loading}
              onClick={() =>
                act(action, action === "MODIFY" ? { modified_pathway: "pathway-hr-adjusted" } : undefined)
              }
              className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-800 hover:bg-slate-50 disabled:opacity-50"
            >
              {action.replace(/_/g, " ")}
            </button>
          ))}
        </section>

        {result && (
          <p className="rounded-lg bg-teal-50 px-4 py-3 text-sm font-medium text-teal-900" role="status">
            {result}
          </p>
        )}
      </main>
    </>
  );
}
