import Link from "next/link";
import { AppHeader } from "./components/AppShell";

export default function HomePage() {
  return (
    <>
      <AppHeader badge="CHECKPOINT 06" />
      <main className="mx-auto max-w-4xl px-6 py-12">
        <section className="rounded-xl border border-slate-200 bg-white p-8 shadow-sm">
          <h2 className="text-2xl font-semibold text-slate-900">Enterprise Control Room</h2>
          <p className="mt-2 text-slate-600">
            Decision support, evidence synthesis, intervention simulation, and human governance —
            sitting above SAP as a reasoning layer.
          </p>
          <Link
            href="/control-room"
            className="mt-6 inline-flex rounded-lg bg-teal-700 px-5 py-2.5 text-sm font-medium text-white hover:bg-teal-600"
          >
            Open Control Room
          </Link>
        </section>

        <ul className="mt-6 grid gap-3 sm:grid-cols-2">
          {[
            { href: "/candidate", label: "Candidate view" },
            { href: "/employer", label: "Employer readiness" },
            { href: "/hr-review", label: "HR review" },
          ].map((item) => (
            <li key={item.href}>
              <Link
                href={item.href}
                className="block rounded-lg border border-slate-200 bg-white px-4 py-3 text-sm font-medium text-slate-800 hover:border-teal-300"
              >
                {item.label}
              </Link>
            </li>
          ))}
        </ul>

        <p className="mt-8 text-xs text-slate-500">
          SAP: SIMULATED ONLY. No live SAP integration has been claimed or implemented.
        </p>
      </main>
    </>
  );
}
