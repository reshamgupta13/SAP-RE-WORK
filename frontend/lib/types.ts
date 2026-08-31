/** Control Room API contract — backend is source of truth. */

export type ControlRoomData = {
  case_id?: string;
  run_id: string;
  human_decision_status?: string;
  human_review?: {
    ai_recommendation?: Record<string, unknown>;
    decision_card_id?: string;
  };
  ai_recommendation?: Record<string, unknown>;
  system_status: {
    sap: string;
    ai_engine: string;
    pipeline_progress: number;
    sap_health?: Record<string, unknown>;
  };
  active_case: Record<string, unknown>;
  candidate?: Record<string, unknown>;
  decision_card: Record<string, unknown>;
  diagnosis?: {
    summary?: Record<string, unknown>;
    capability_gaps?: Array<Record<string, unknown>>;
    requirement_diagnoses?: Array<Record<string, unknown>>;
    counterfactuals?: Array<Record<string, unknown>>;
  };
  what_changed?: { changes?: Array<Record<string, unknown>> };
  viability: { assessments?: Array<Record<string, unknown>>; comparison?: Record<string, unknown> };
  pathway: Record<string, unknown> | null;
  proof: {
    result?: Record<string, unknown> | null;
    assessment?: Record<string, unknown> | null;
    evidence?: Record<string, unknown> | null;
  };
  interventions: Record<string, unknown>;
  explainability: { reports?: Array<Record<string, unknown>> };
  sap_context?: Record<string, unknown>;
  sap_judge_panel?: Record<string, unknown>;
  agent_orchestrator?: Record<string, unknown>;
  jury_narrative?: Record<string, unknown>;
  employer_readiness?: Array<Record<string, unknown>>;
  timeline?: Array<Record<string, unknown>>;
  pipeline?: Array<{ stage: string; agent: string; status: string }>;
  market?: { signals?: Array<Record<string, unknown>> };
  operator_guide?: Array<{ step: string; action: string; explain: string }>;
};

export type ExplainReport = {
  what: string;
  why: string;
  evidence_refs?: string[];
  confidence_label?: string;
  alternatives?: string[];
  assumptions?: string[];
  human_decision_required?: boolean;
};
