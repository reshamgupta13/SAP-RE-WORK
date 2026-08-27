const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "";

async function getHealth() {
  try {
    const res = await fetch(`${API_BASE}/api/health`, { cache: "no-store" });
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

export default async function HomePage() {
  const health = await getHealth();

  return (
    <main className="min-h-screen">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
          <div>
            <h1 className="text-xl font-semibold tracking-tight text-rework-slate">RE:WORK</h1>
            <p className="text-sm text-slate-500">Inclusive Workforce Recomposition Engine</p>
          </div>
          <span className="rounded-md bg-amber-100 px-3 py-1 text-xs font-medium text-amber-900">
            CHECKPOINT 01 — Foundation
          </span>
        </div>
      </header>

      <div className="mx-auto max-w-5xl px-6 py-10">
        <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-medium text-slate-800">System status</h2>
          {health ? (
            <dl className="mt-4 grid gap-3 text-sm sm:grid-cols-2">
              <div>
                <dt className="text-slate-500">API</dt>
                <dd className="font-medium">{health.status}</dd>
              </div>
              <div>
                <dt className="text-slate-500">Demo mode</dt>
                <dd className="font-medium">{String(health.demo_mode)}</dd>
              </div>
              <div>
                <dt className="text-slate-500">SAP connection</dt>
                <dd className="font-medium">{health.sap_connection}</dd>
              </div>
              <div>
                <dt className="text-slate-500">Engine</dt>
                <dd className="font-medium">{health.engine_mode}</dd>
              </div>
            </dl>
          ) : (
            <p className="mt-4 text-sm text-slate-600">
              Backend not reachable. Start API:{" "}
              <code className="rounded bg-slate-100 px-1">uvicorn app.main:app --reload</code>
            </p>
          )}
        </section>

        <section className="mt-6 rounded-lg border border-slate-200 bg-white p-6">
          <h2 className="text-lg font-medium text-slate-800">Planned surfaces</h2>
          <ul className="mt-3 grid gap-2 text-sm text-slate-600 sm:grid-cols-2">
            <li>Candidate Profile</li>
            <li>Job Analysis</li>
            <li>Career Orchestrator</li>
            <li>Decision Card / Explainability</li>
            <li>Learning Pathway</li>
            <li>Proof of Skill</li>
            <li>Opportunity Matching</li>
            <li>HR Review</li>
            <li>SAP Context</li>
          </ul>
        </section>
      </div>
    </main>
  );
}
