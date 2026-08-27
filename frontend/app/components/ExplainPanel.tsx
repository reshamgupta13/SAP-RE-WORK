type Report = {
  what: string;
  why: string;
  evidence_refs?: string[];
  confidence_label?: string;
  alternatives?: string[];
  assumptions?: string[];
  human_decision_required?: boolean;
};

export function ExplainPanel({ report, onClose }: { report: Report | null; onClose: () => void }) {
  if (!report) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="explain-title"
    >
      <div className="max-h-[90vh] w-full max-w-lg overflow-y-auto rounded-xl bg-white shadow-xl">
        <header className="flex items-center justify-between border-b border-slate-100 px-6 py-4">
          <h2 id="explain-title" className="text-lg font-semibold">Explainability</h2>
          <button
            type="button"
            onClick={onClose}
            className="rounded-md px-2 py-1 text-slate-500 hover:bg-slate-100"
            aria-label="Close"
          >
            ✕
          </button>
        </header>
        <div className="space-y-4 p-6 text-sm">
          <Section label="WHAT" text={report.what} />
          <Section label="WHY" text={report.why} />
          <Section label="EVIDENCE" text={(report.evidence_refs ?? []).join(", ") || "Structured refs in run"} />
          <Section label="CONFIDENCE" text={report.confidence_label ?? "—"} />
          <Section label="ALTERNATIVES" text={(report.alternatives ?? []).join("; ") || "—"} />
          <Section label="ASSUMPTIONS" text={(report.assumptions ?? []).join("; ")} />
          <Section
            label="HUMAN DECISION"
            text={report.human_decision_required ? "Required before action" : "Optional review"}
          />
        </div>
      </div>
    </div>
  );
}

function Section({ label, text }: { label: string; text: string }) {
  return (
    <div>
      <h3 className="text-xs font-bold uppercase tracking-wide text-slate-500">{label}</h3>
      <p className="mt-1 text-slate-800">{text}</p>
    </div>
  );
}
