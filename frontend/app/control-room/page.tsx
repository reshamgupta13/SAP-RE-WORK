import Link from "next/link";
import { fetchCatalogHealth, fetchControlRoom } from "../../lib/api";
import { AppHeader } from "../components/AppShell";
import { ControlRoomClient } from "./ControlRoomClient";
import { ControlRoomLoaderClient } from "./ControlRoomLoaderClient";

export default async function ControlRoomPage({
  searchParams,
}: {
  searchParams: Promise<{ caseId?: string; run?: string }>;
}) {
  const params = await searchParams;
  if (!params.caseId) {
    const health = await fetchCatalogHealth().catch(() => null);
    return (
      <div className="rework-atmosphere min-h-screen">
        <AppHeader badge="Control Room" activePath="/control-room" showCta={false} sapMode={health?.source_mode} liveVerified={health?.live_verified} />
        <main className="rework-content mx-auto max-w-3xl px-6 py-12">
          <p className="kicker">Control Room</p>
          <h1 className="section-heading mt-2">Select a person to begin</h1>
          <p className="mt-3 text-sm text-muted">
            Control Room is driven by a live case. Choose a candidate and role in the workspace.
          </p>
          <Link href="/workspace" className="btn-primary mt-6 inline-flex">
            Open workspace
          </Link>
        </main>
      </div>
    );
  }

  if (params.run === "1") {
    return <ControlRoomLoaderClient caseId={params.caseId} />;
  }

  try {
    const data = await fetchControlRoom(params.caseId);
    return <ControlRoomClient data={data} />;
  } catch (e) {
    return (
      <div className="rework-atmosphere min-h-screen">
        <main className="rework-content mx-auto max-w-6xl px-6 py-12 text-center">
          <p className="text-muted">Control Room unavailable for this case.</p>
          <p className="mt-2 text-sm text-amber">{(e as Error).message}</p>
          <Link href="/workspace" className="btn-primary mt-6 inline-flex">Open workspace</Link>
        </main>
      </div>
    );
  }
}
