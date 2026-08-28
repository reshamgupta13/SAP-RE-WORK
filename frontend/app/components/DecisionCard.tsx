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

  return (
    <section
      className="rounded-xl border border-slate-200 bg-white shadow-sm ring-1 ring-slate-900/5"
      aria-labelledby="decision-card-title"
    >
      <header className="border-b border-slate-100 bg-gradient-to-r from-slate-900 to-slate-800 px-6 py-4 text-white">
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="text-xs font-medium uppercase tracking-widest text-slate-300">Decision Card</p>
            <h2 id="decision-card-title" className="mt-1 text-xl font-semibold">
              {card.candidate_name as string} → {card.target_role_title as string}
            </h2>
          </div>
          {onWhy && (
            <button
              type="button"
              onClick={onWhy}
              className="rounded-md bg-teal-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-teal-500 focus:outline-none focus:ring-2 focus:ring-teal-400"
            >
              WHY?
            </button>
          )}
        </div>
      </header>

      <div className="grid gap-4 p-6 md:grid-cols-2">
        <Metric label="Capability fit" value={viability?.dimensions ? (viability.dimensions as { capability_fit?: number }).capability_fit : "—"} />
        <Metric label="Evidence strength" value={viability?.dimensions ? (viability.dimensions as { evidence_strength?: number }).evidence_strength : "—"} />
        <Metric label="Viability" value={(viability?.viability_state as string) ?? "—"} highlight />
        <Metric label="Confidence" value={confidence?.toFixed(2)} />
      </div>

      <div className="grid gap-4 border-t border-slate-100 p-6 md:grid-cols-2">
        <Block title="Genuine gaps" items={gaps} empty="None identified" />
        <Block title="Potential barriers" items={proxies} empty="None flagged" />
        <Block title="Workplace constraints" items={(card.workplace_constraints as string[]) ?? []} empty="None flagged" />
        <Block title="Pathway" items={pathway ? [pathway.title as string ?? pathway.id as string] : []} empty="Not generated" />
        <Block
          title="Proof status"
          items={proof?.result ? [`${proof.result.result as string} (${proof.result.total as number})`] : []}
          empty="Not evaluated"
        />
        <Block title="Evidence refs" items={(card.evidence_refs as string[])?.slice(0, 4) ?? []} empty="None cited" />
      </div>

      {(card.what != null || card.why != null) && (
        <div className="border-t border-slate-100 px-6 py-4 text-sm text-slate-700">
          {card.what != null && <p><span className="font-medium">What:</span> {String(card.what)}</p>}
          {card.why != null && <p className="mt-1"><span className="font-medium">Why:</span> {String(card.why)}</p>}
        </div>
      )}

      <footer className="border-t border-slate-100 bg-slate-50 px-6 py-3 text-sm text-slate-600">
        AI recommendation generated — human decision required. <SourceBadge mode={card.source_mode as string} />
      </footer>
    </section>
  );
}

function Metric({ label, value, highlight }: { label: string; value: unknown; highlight?: boolean }) {
  return (
    <div className="rounded-lg bg-slate-50 p-3">
      <dt className="text-xs font-medium uppercase tracking-wide text-slate-500">{label}</dt>
      <dd className={`mt-1 text-lg font-semibold ${highlight ? "text-teal-700" : "text-slate-900"}`}>
        {String(value)}
      </dd>
    </div>
  );
}

function Block({ title, items, empty }: { title: string; items: string[]; empty: string }) {
  return (
    <div>
      <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-500">{title}</h3>
      {items.length ? (
        <ul className="mt-2 space-y-1 text-sm text-slate-800">
          {items.map((item) => (
            <li key={item} className="rounded bg-white px-2 py-1 ring-1 ring-slate-200">{item}</li>
          ))}
        </ul>
      ) : (
        <p className="mt-2 text-sm text-slate-500">{empty}</p>
      )}
    </div>
  );
}
