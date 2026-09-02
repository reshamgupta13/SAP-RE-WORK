import { formatLabel } from "../../lib/format";

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
  completed: "bg-sage/15 text-sage",
  skipped: "bg-parchment text-muted",
  failed: "bg-red-100 text-red-800",
  pending: "bg-amber/15 text-amber",
};

export function AgentOrchestratorPanel({ data }: { data: AgentOrchestratorData }) {
  const nodes = data.nodes ?? [];

  return (
    <section className="surface-panel overflow-hidden p-4">
      <div className="flex items-center justify-between gap-2">
        <h3 className="kicker !tracking-[0.08em]">Agent orchestrator</h3>
        <span className="font-mono text-[10px] text-muted">{data.orchestrator ?? "LangGraph"}</span>
      </div>
      <p className="mt-1 font-mono text-[10px] text-muted">
        SAP: {formatLabel(data.sap_source_mode)} · Engine: {formatLabel(data.engine_mode)}
      </p>
      <ol className="mt-3 max-h-[28rem] space-y-2 overflow-y-auto text-sm">
        {nodes.map((node) => (
          <li
            key={node.agent}
            className="rounded-lg border border-border bg-surface px-3 py-2"
          >
            <div className="flex items-start justify-between gap-2">
              <div className="min-w-0">
                <p className="font-medium text-ink">{node.label}</p>
                <p className="font-mono text-[10px] text-muted">{formatLabel(node.stage)}</p>
              </div>
              <span
                className={`shrink-0 rounded px-2 py-0.5 text-xs font-medium ${
                  STATUS_STYLES[node.status] ?? STATUS_STYLES.pending
                }`}
              >
                {node.status}
              </span>
            </div>
            <dl className="mt-2 grid grid-cols-2 gap-x-2 gap-y-1 font-mono text-[10px] text-muted">
              {node.duration_ms != null && (
                <>
                  <dt>Duration</dt>
                  <dd className="text-ink">{node.duration_ms}ms</dd>
                </>
              )}
              {node.confidence && (
                <>
                  <dt>Confidence</dt>
                  <dd className="text-ink">{formatLabel(node.confidence)}</dd>
                </>
              )}
              {node.evidence_count != null && node.evidence_count > 0 && (
                <>
                  <dt>Evidence</dt>
                  <dd className="text-ink">{node.evidence_count}</dd>
                </>
              )}
              {node.source_mode && (
                <>
                  <dt>Source</dt>
                  <dd className="text-ink">{formatLabel(node.source_mode)}</dd>
                </>
              )}
            </dl>
            {node.output && (
              <p className="mt-1 break-words text-xs text-muted">→ {node.output}</p>
            )}
          </li>
        ))}
      </ol>
    </section>
  );
}
