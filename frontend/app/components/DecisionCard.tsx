import { formatLabel, formatPathwayId } from "../../lib/format";
import { SourceBadge } from "./SourceBadge";

type DecisionCardProps = {
  card: Record<string, unknown>;
  viability?: Record<string, unknown>;
  pathway?: Record<string, unknown> | null;
  proof?: { result?: Record<string, unknown> | null };
  onWhy?: () => void;
};

export function DecisionCard({ card, viability, pathway, proof, onWhy }: DecisionCardProps) {
  const gaps = (card.genuine_gaps as string[]) ?? [];
  const proxies = (card.potential_proxies as string[]) ?? [];
  const confidence = card.confidence as number;
  const pathwayLabel = pathway
    ? String(pathway.title ?? formatPathwayId(String(pathway.id ?? "")))
    : null;

  return (
    <section className="surface-card overflow-hidden" aria-labelledby="decision-card-title">
      <header
        className="border-b border-border px-6 py-4"
        style={{ backgroundColor: "var(--color-brand)", color: "var(--color-brand-text)" }}
      >
        <div className="flex items-start justify-between gap-4">
          <div className="min-w-0">
            <p className="font-mono text-[10px] uppercase tracking-wider opacity-70">Decision card</p>
            <h2 id="decision-card-title" className="font-display mt-1 text-xl font-semibold">
              {card.candidate_name as string} → {card.target_role_title as string}
            </h2>
          </div>
          {onWhy && (
            <button
              type="button"
              onClick={onWhy}
              className="shrink-0 rounded-md border border-white/30 bg-white/10 px-3 py-1.5 text-xs font-semibold transition-all duration-interaction hover:bg-white/20"
            >
              WHY?
            </button>
          )}
        </div>
      </header>

      <div className="grid gap-4 p-6 md:grid-cols-2">
        <Metric label="Capability fit" value={viability?.dimensions ? (viability.dimensions as { capability_fit?: number }).capability_fit : "—"} />
        <Metric label="Evidence strength" value={viability?.dimensions ? (viability.dimensions as { evidence_strength?: number }).evidence_strength : "—"} />
        <Metric label="Viability" value={formatLabel(viability?.viability_state)} highlight />
        <Metric label="Confidence" value={confidence != null ? `${Math.round(confidence * 100)}%` : "—"} />
      </div>

      <div className="grid gap-4 border-t border-border p-6 md:grid-cols-2">
        <Block title="Genuine gaps" items={gaps} empty="None identified" />
        <Block title="Potential barriers" items={proxies} empty="None flagged" />
        <Block title="Workplace constraints" items={(card.workplace_constraints as string[]) ?? []} empty="None flagged" />
        <Block title="Pathway" items={pathwayLabel ? [pathwayLabel] : []} empty="Not generated" />
        <Block
          title="Proof status"
          items={proof?.result ? [`${formatLabel(proof.result.result)} (${proof.result.total as number})`] : []}
          empty="Not evaluated"
        />
        <Block title="Evidence refs" items={(card.evidence_refs as string[])?.slice(0, 4) ?? []} empty="None cited" />
      </div>

      {(card.what != null || card.why != null) && (
        <div className="border-t border-border px-6 py-4 text-sm text-muted">
          {card.what != null && <p><span className="font-medium text-ink">What:</span> {String(card.what)}</p>}
          {card.why != null && <p className="mt-1"><span className="font-medium text-ink">Why:</span> {String(card.why)}</p>}
        </div>
      )}

      <footer className="border-t border-border bg-parchment/40 px-6 py-3 text-sm text-muted">
        AI recommendation generated — human decision required. <SourceBadge mode={card.source_mode as string} />
      </footer>
    </section>
  );
}

function Metric({ label, value, highlight }: { label: string; value: unknown; highlight?: boolean }) {
  return (
    <div className="surface-panel p-3">
      <dt className="font-mono text-[10px] uppercase tracking-wide text-muted">{label}</dt>
      <dd className={`mt-1 text-lg font-semibold ${highlight ? "text-accent" : "text-ink"}`}>
        {String(value)}
      </dd>
    </div>
  );
}

function Block({ title, items, empty }: { title: string; items: string[]; empty: string }) {
  return (
    <div className="min-w-0">
      <h3 className="font-mono text-[10px] uppercase tracking-wide text-muted">{title}</h3>
      {items.length ? (
        <ul className="mt-2 space-y-1 text-sm text-ink">
          {items.map((item, i) => (
            <li key={`${title}-${item}-${i}`} className="break-words surface-panel px-2 py-1">{item}</li>
          ))}
        </ul>
      ) : (
        <p className="mt-2 text-sm text-muted">{empty}</p>
      )}
    </div>
  );
}
