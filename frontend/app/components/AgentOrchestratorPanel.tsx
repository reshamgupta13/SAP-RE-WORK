type AgentNode = {
  agent: string;
  label: string;
  stage: string;
  kind: string;
  status: string;
  duration_ms?: number | null;
  engine_mode?: string;
  confidence?: string;
  evidence_count?: number;
  source_mode?: string;
  input_sources?: string[];
  output?: string;
  rationale?: string;
  error?: string;
};

type AgentOrchestratorData = {
  orchestrator?: string;
  engine_mode?: string;
  sap_source_mode?: string;
  progress?: number;
  nodes?: AgentNode[];
  sap_agent_flows?: Array<Record<string, unknown>>;
  human_governance?: Record<string, unknown>;
};

const STATUS_STYLES: Record<string, string> = {
  completed: "bg-emerald-100 text-emerald-800",
  skipped: "bg-slate-100 text-slate-600",
  failed: "bg-red-100 text-red-800",
  pending: "bg-amber-50 text-amber-800",
};

export function AgentOrchestratorPanel({ data }: { data: AgentOrchestratorData }) {
  const nodes = data.nodes ?? [];

  return (
    <section className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <div className="flex items-center justify-between">
        <h3 className="text-xs font-semibold uppercase text-slate-500">Agent orchestrator</h3>
        <span className="text-xs text-slate-500">{data.orchestrator ?? "LangGraph"}</span>
      </div>
      <p className="mt-1 text-xs text-slate-500">
        SAP: {data.sap_source_mode ?? "—"} · Engine: {data.engine_mode ?? "—"}
      </p>
      <ol className="mt-3 max-h-[28rem] space-y-2 overflow-y-auto text-sm">
        {nodes.map((node) => (
          <li
            key={node.agent}
            className="rounded-lg border border-slate-100 bg-slate-50 px-3 py-2"
          >
            <div className="flex items-start justify-between gap-2">
              <div>
                <p className="font-medium text-slate-900">{node.label}</p>
                <p className="text-xs text-slate-500">{node.stage}</p>
              </div>
              <span
                className={`shrink-0 rounded px-2 py-0.5 text-xs font-medium ${
                  STATUS_STYLES[node.status] ?? STATUS_STYLES.pending
                }`}
              >
                {node.status}
              </span>
            </div>
            <dl className="mt-2 grid grid-cols-2 gap-x-2 gap-y-1 text-xs text-slate-600">
              {node.duration_ms != null && (
                <>
                  <dt>Duration</dt>
                  <dd>{node.duration_ms}ms</dd>
                </>
              )}
              {node.confidence && (
                <>
                  <dt>Confidence</dt>
                  <dd>{node.confidence}</dd>
                </>
              )}
              {node.evidence_count != null && node.evidence_count > 0 && (
                <>
                  <dt>Evidence</dt>
                  <dd>{node.evidence_count}</dd>
                </>
              )}
              {node.source_mode && (
                <>
                  <dt>Source</dt>
                  <dd>{node.source_mode}</dd>
                </>
              )}
            </dl>
            {node.output && (
              <p className="mt-1 text-xs text-slate-600">→ {node.output}</p>
            )}
          </li>
        ))}
      </ol>
    </section>
  );
}
