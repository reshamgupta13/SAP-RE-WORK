import Link from "next/link";
import { AppHeader } from "./components/AppShell";

export default function HomePage() {
  return (
    <>
      <AppHeader badge="Finale Prototype" />
      <main className="rework-grid-bg min-h-screen">
        <div className="mx-auto max-w-4xl px-6 py-16">
          <section className="rounded-2xl border border-slate-200 bg-white p-10 shadow-lg">
            <p className="text-xs font-bold uppercase tracking-widest text-teal-700">RE:WORK</p>
            <h1 className="font-display mt-3 text-4xl text-slate-900">
              Inclusive Workforce Intelligence
            </h1>
            <p className="mt-4 text-lg text-slate-600">
              Who could succeed in this role — if we reasoned beyond the résumé?
            </p>
            <p className="mt-2 text-sm text-slate-500">
              Canonical demo: Ananya Sharma → Data Analyst · SAP SIMULATED · DEMO_FALLBACK
            </p>
            <Link
              href="/control-room"
              className="mt-8 inline-flex rounded-lg bg-slate-900 px-6 py-3 text-sm font-semibold text-white hover:bg-slate-800"
            >
              Open Control Room — Start Demo
            </Link>
          </section>

          <ul className="mt-8 grid gap-3 sm:grid-cols-3">
            {[
              { href: "/candidate", label: "Candidate view", desc: "Capability-focused journey" },
              { href: "/employer", label: "Employer readiness", desc: "Two-sided viability" },
              { href: "/hr-review", label: "Human review", desc: "AI ≠ final decision" },
            ].map((item) => (
              <li key={item.href}>
                <Link
                  href={item.href}
                  className="block h-full rounded-xl border border-slate-200 bg-white p-4 hover:border-teal-400 hover:shadow-md"
                >
                  <span className="font-medium text-slate-900">{item.label}</span>
                  <p className="mt-1 text-xs text-slate-500">{item.desc}</p>
                </Link>
              </li>
            ))}
          </ul>

          <p className="mt-10 text-center text-xs text-slate-500">
            SAP: SIMULATED ONLY — live SuccessFactors integration is the remaining external dependency.
          </p>
        </div>
      </main>
    </>
  );
}
