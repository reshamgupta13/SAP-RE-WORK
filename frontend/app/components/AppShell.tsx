"use client";

import Link from "next/link";
import { ThemeToggle } from "./ThemeProvider";
import { SourceBadge } from "./SourceBadge";

const NAV_LINKS = [
  { href: "/workspace", label: "Workspace" },
  { href: "/targeted-learning", label: "Targeted Learning" },
  { href: "/student", label: "Student" },
  { href: "/candidate", label: "Candidate" },
  { href: "/opportunities", label: "Opportunities" },
  { href: "/employer", label: "Employer" },
  { href: "/hr-review", label: "HR Review" },
  { href: "/control-room", label: "Control Room" },
];

export function AppNav({ activePath }: { activePath?: string }) {
  return (
    <nav className="hidden flex-wrap items-center gap-1 md:flex" aria-label="Main">
      {NAV_LINKS.map((l) => (
        <Link
          key={l.href}
          href={l.href}
          className={`nav-link ${activePath === l.href ? "nav-link-active" : ""}`}
        >
          {l.label}
        </Link>
      ))}
    </nav>
  );
}

export function MobileNav({ activePath }: { activePath?: string }) {
  return (
    <nav className="flex gap-2 overflow-x-auto pb-1 md:hidden" aria-label="Mobile">
      {NAV_LINKS.map((l) => (
        <Link
          key={l.href}
          href={l.href}
          className={`shrink-0 rounded-md px-3 py-1.5 text-xs font-medium ${
            activePath === l.href ? "bg-accent/10 text-accent" : "text-muted"
          }`}
        >
          {l.label}
        </Link>
      ))}
    </nav>
  );
}

export function AppHeader({
  badge,
  activePath,
  showCta = true,
  sapMode = "NOT_CONNECTED",
  liveVerified = false,
}: {
  badge?: string;
  activePath?: string;
  showCta?: boolean;
  sapMode?: string;
  liveVerified?: boolean;
}) {
  return (
    <header className="sticky top-0 z-50 border-b border-border bg-surface/95 backdrop-blur-md">
      <div className="rework-content mx-auto max-w-6xl px-4 py-4 sm:px-6">
        <div className="flex flex-col gap-3">
          <div className="flex items-center justify-between gap-3">
            <Link href="/" className="group flex min-w-0 shrink items-center gap-3">
              <span
                className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg text-sm font-bold"
                style={{ backgroundColor: "var(--color-brand)", color: "var(--color-brand-text)" }}
              >
                R
              </span>
              <div className="min-w-0">
                <p className="font-display truncate text-lg font-semibold leading-none text-ink">RE:WORK</p>
                <p className="truncate text-xs text-muted">SAP Workforce Intelligence</p>
              </div>
            </Link>

            <div className="flex shrink-0 items-center gap-2">
              <ThemeToggle />
              {badge && (
                <span className="hidden rounded-md bg-parchment px-2.5 py-1 font-mono text-[10px] font-medium uppercase tracking-wider text-muted sm:inline">
                  {badge}
                </span>
              )}
              <SourceBadge mode={sapMode} liveVerified={liveVerified} />
              {showCta && (
                <Link
                  href="/workspace"
                  className="btn-primary hidden whitespace-nowrap px-3 py-2 text-xs sm:inline-flex lg:px-4"
                >
                  Open workspace
                </Link>
              )}
            </div>
          </div>
          <AppNav activePath={activePath} />
          <MobileNav activePath={activePath} />
        </div>
      </div>
    </header>
  );
}
