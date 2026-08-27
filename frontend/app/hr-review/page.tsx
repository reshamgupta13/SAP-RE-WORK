import { fetchControlRoom } from "../../lib/api";
import { HrReviewClient } from "./HrReviewClient";

export default async function HrReviewPage() {
  try {
    const data = await fetchControlRoom();
    return <HrReviewClient data={data} />;
  } catch {
    return (
      <main className="mx-auto max-w-3xl px-6 py-12 text-center text-slate-600">
        HR Review unavailable — start the API server.
      </main>
    );
  }
}
