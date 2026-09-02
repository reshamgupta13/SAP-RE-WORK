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
  enterprise_context?: EnterpriseContext;
};

export type EnterpriseEvidence = {
  id?: string;
  title?: string;
  type?: string;
  verification_status?: string;
  description?: string;
  occurred_on?: string;
  source_mode?: string;
  confidence?: number;
};

export type PersonSkill = {
  user_id?: string;
  skill_id: string;
  skill_name?: string;
  proficiency?: number;
  confidence?: number;
  verification_status?: string;
  inference_status?: string;
  valid_from?: string;
  valid_to?: string | null;
  recency_status?: string;
  gap_status?: string;
  evidence?: EnterpriseEvidence[];
  source_mode?: string;
};

export type EnterpriseJob = {
  job_id: string;
  job_name?: string;
  job_description?: string | null;
  org_unit_id?: string;
  location?: string;
  family?: string;
  work_modes?: string[];
  is_target?: boolean;
  source_mode?: string;
  required_skill_count?: number;
  mandatory_skill_count?: number;
  opportunity_id?: string;
};

export type JobSkill = {
  job_id: string;
  skill_id: string;
  skill_name?: string;
  required_proficiency?: number;
  is_mandatory?: boolean;
  evidence_expectation?: string | null;
};

export type FitSkillRow = {
  skill_id?: string;
  skill_name?: string;
  candidate_proficiency?: number;
  required_proficiency?: number;
  gap_status?: string;
  rationale?: string;
  evidence_refs?: string[];
  kind?: string;
};

export type FitRequirementRow = {
  requirement_text?: string;
  diagnosis_type?: string;
  review_tag?: string;
  rationale?: string;
  kind?: string;
};

export type SapTraceRow = {
  sap_table: string;
  product_label: string;
  odata_entity: string;
  odata_method: string;
  rework_model: string;
  agent: string;
  record_count: number;
  source_mode?: string;
  service?: string | null;
};

export type EnterpriseContext = {
  source_mode: string;
  odata_status: {
    label: string;
    source_mode: string;
    live_verified: boolean;
    service?: string | null;
    metadata_accessible?: boolean;
    entity_mappings?: string;
  };
  write_operations?: { available: boolean; reason?: string };
  domains: {
    candidate: Record<string, unknown>;
    skills: Array<Record<string, unknown>>;
    person_skills: PersonSkill[];
    jobs: EnterpriseJob[];
    job_skills: JobSkill[];
    organizations: Array<Record<string, unknown>>;
    hr_reviewer: Record<string, unknown>;
  };
  capability_fit?: { skills: FitSkillRow[]; requirements: FitRequirementRow[] };
  proof_delta?: {
    skill_id?: string;
    result?: string;
    total?: number;
    is_demo?: boolean;
    source_mode?: string;
    message?: string | null;
  } | null;
  sap_trace?: SapTraceRow[];
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
