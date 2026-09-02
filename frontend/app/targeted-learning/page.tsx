import { Suspense } from "react";
import { TargetedLearningClient } from "./TargetedLearningClient";

export default function TargetedLearningPage() {
  return (
    <Suspense fallback={<div className="p-10 text-center text-muted">Loading…</div>}>
      <TargetedLearningClient />
    </Suspense>
  );
}
