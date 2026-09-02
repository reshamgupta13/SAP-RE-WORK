import Link from "next/link";
import { AppHeader } from "./AppShell";
import { HeroArtwork } from "./HeroArtwork";
import { HeroReveal } from "./HeroReveal";
import { ScrollReveal } from "./ScrollReveal";

const VALUE_ITEMS = [
  { title: "Evidence-first", desc: "Reason from what candidates can demonstrate." },
  { title: "Targeted pathways", desc: "Minimum-effective routes to readiness." },
  { title: "Human oversight", desc: "AI recommends — HR decides." },
  { title: "Outcome focused", desc: "Viability without lowering the standard." },
];

const JOURNEY_CARDS = [
  {
    href: "/workspace",
    label: "Workforce workspace",
    desc: "Select a person and a role from SAP, then let RE:WORK diagnose the pairing.",
    meta: "Start here",
  },
  {
    href: "/skills",
    label: "Skills workspace",
    desc: "SAP skill CRUD — create, read, update, and delete ZREWORK_SKILL records.",
    meta: "SAP OData lab",
  },
  {
    href: "/candidate",
    label: "Candidate",
    desc: "Profile, recorded skills, and evidence from SAP.",
    meta: "Candidate view",
  },
  {
    href: "/employer",
    label: "Employer",
    desc: "Organization context for the selected role.",
    meta: "Employer view",
  },
  {
    href: "/hr-review",
    label: "Human review",
    desc: "Approve, modify, reject, or request more evidence.",
    meta: "Governance",
  },
];

export function HomePageClient() {
  return (
    <div className="rework-atmosphere rework-route-texture">
      <AppHeader badge="Product" activePath="/" showCta />

      <main className="rework-content">
        {/* Hero */}
        <section className="hero-section mx-auto max-w-7xl px-6 py-16 md:py-24">
          <div className="hero-section-copy min-w-0">
            <p className="kicker">Inclusive workforce intelligence</p>
            <HeroReveal
              className="mt-4"
              lines={[
                { text: "Reason beyond" },
                { text: "the résumé." },
                { text: "Build pathways", accent: true },
                { text: "that prove readiness." },
              ]}
            />
            <p className="font-body mt-6 max-w-lg text-lg leading-relaxed text-muted">
              RE:WORK helps employers discover who could succeed in a role — what they can already
              demonstrate, what is genuinely missing, and the smallest evidence-backed path forward.
            </p>
            <div className="mt-8 flex flex-wrap gap-4">
              <Link href="/workspace" className="btn-primary">
                Open workspace
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden>
                  <path d="M5 12h14M12 5l7 7-7 7" />
                </svg>
              </Link>
              <Link href="/candidate" className="btn-secondary">
                Browse candidates
              </Link>
            </div>
            <p className="font-mono-data mt-6 text-muted">
              Select any person in the workforce, select any role, and RE:WORK reasons over the SAP context.
            </p>
          </div>
          <div className="hero-artwork-col">
            <HeroArtwork />
          </div>
        </section>

        {/* Value strip */}
        <section className="border-y border-border bg-surface/60">
          <div className="mx-auto grid max-w-6xl sm:grid-cols-2 lg:grid-cols-4">
            {VALUE_ITEMS.map((item) => (
              <div key={item.title} className="value-strip-item">
                <p className="font-mono text-[10px] font-semibold uppercase tracking-[0.16em] text-sage">
                  {item.title}
                </p>
                <p className="font-body text-sm leading-relaxed text-muted">{item.desc}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Learning experience */}
        <section className="mx-auto max-w-6xl px-6 py-20">
          <ScrollReveal>
            <p className="kicker">The experience</p>
            <h2 className="section-heading mt-3">A journey, not a dashboard</h2>
            <p className="font-body mt-4 max-w-2xl text-lg text-muted">
              Every screen connects to the currently selected SAP candidate and role — from evidence
              through diagnosis, pathway, proof, and a human HR decision.
            </p>
          </ScrollReveal>

          <div className="mt-10 grid gap-4 sm:grid-cols-2">
            {JOURNEY_CARDS.map((card) => (
              <ScrollReveal key={card.href}>
                <Link href={card.href} className="interactive-card group">
                  <p className="font-mono text-[10px] font-medium uppercase tracking-wider text-sage">
                    {card.meta}
                  </p>
                  <h3 className="mt-2 font-display text-xl font-semibold text-ink group-hover:text-accent">
                    {card.label}
                  </h3>
                  <p className="mt-2 text-sm leading-relaxed text-muted">{card.desc}</p>
                  <span className="mt-4 inline-flex items-center gap-1 text-sm font-medium text-accent">
                    Open
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden>
                      <path d="M5 12h14M12 5l7 7-7 7" />
                    </svg>
                  </span>
                </Link>
              </ScrollReveal>
            ))}
          </div>
        </section>

        {/* AI positioning */}
        <section className="mx-auto max-w-6xl px-6 pb-12">
          <ScrollReveal>
            <div className="surface-panel p-8 md:p-10">
              <p className="kicker">Your reasoning assistant</p>
              <h2 className="section-heading mt-3">Intelligence that supports the decision</h2>
              <p className="font-body mt-4 max-w-2xl text-muted">
                AI decomposes roles, diagnoses capability gaps, and explains recommendations with
                evidence. It never autonomously hires or rejects — human HR retains final authority.
              </p>
            </div>
          </ScrollReveal>
        </section>

        {/* Final CTA */}
        <section className="border-t border-border bg-parchment/50 px-6 py-16">
          <div className="mx-auto max-w-2xl text-center">
            <h2 className="font-display text-3xl font-semibold text-ink">
              Start with real workforce records
            </h2>
            <p className="font-body mt-4 text-muted">
              Select a candidate and a role from SAP. RE:WORK diagnoses gaps. Human HR decides.
            </p>
            <Link href="/workspace" className="btn-primary mt-8">
              Open workspace
            </Link>
            <p className="font-mono-data mt-8 text-muted">
              SAP status is reported honestly — LIVE only after verified retrieval.
            </p>
          </div>
        </section>
      </main>
    </div>
  );
}
