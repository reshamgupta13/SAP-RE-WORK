import Link from "next/link";
import { SourceBadge } from "../components/SourceBadge";

export function AppNav() {
  const links = [
    { href: "/control-room", label: "Control Room" },
    { href: "/candidate", label: "Candidate" },
    { href: "/employer", label: "Employer" },
    { href: "/hr-review", label: "HR Review" },
  ];
  return (
    <nav className="flex flex-wrap items-center gap-4 text-sm" aria-label="Main">
      {links.map((l) => (
        <Link key={l.href} href={l.href} className="text-slate-600 hover:text-teal-700 hover:underline">
          {l.label}
        </Link>
      ))}
    </nav>
  );
}

export function AppHeader({ badge }: { badge?: string }) {
  return (
    <header className="border-b border-slate-200 bg-white">
      <div className="mx-auto flex max-w-6xl flex-col gap-3 px-6 py-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-xl font-semibold tracking-tight text-slate-900">RE:WORK</h1>
          <p className="text-sm text-slate-500">Inclusive Workforce Intelligence</p>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <AppNav />
          {badge && (
            <span className="rounded-md bg-slate-900 px-3 py-1 text-xs font-medium text-white">{badge}</span>
          )}
          <SourceBadge mode="SIMULATED" />
        </div>
      </div>
    </header>
  );
}
