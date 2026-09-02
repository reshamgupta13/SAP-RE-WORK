import type { ControlRoomData } from "./types";
import { apiUrl, getApiBaseUrl } from "./api-base";

async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(apiUrl(path), { cache: "no-store" });
  if (!res.ok) throw new Error(`Request failed (${res.status})`);
  return res.json() as Promise<T>;
}

export async function fetchControlRoom(caseId?: string): Promise<ControlRoomData> {
  if (!caseId) {
    throw new Error("A case identifier is required");
  }
  return apiGet<ControlRoomData>(`/api/cases/${caseId}/control-room`);
}

export async function fetchCatalogHealth() {
  return apiGet<{
    source_mode: string;
    live_verified: boolean;
    message?: string;
    prototype_demo?: boolean;
    write_operations?: { available?: boolean; reason?: string };
    entity_status?: Record<string, string>;
    hybrid_mode?: boolean;
    access_plan?: { entities?: Array<Record<string, unknown>> };
  }>("/api/catalog/health");
}

export async function fetchCatalogTrace() {
  return apiGet<{ traces?: Array<Record<string, unknown>>; message?: string; source_mode?: string }>(
    "/api/catalog/trace",
  );
}

export async function fetchCandidates(q?: string) {
  const qs = q ? `?q=${encodeURIComponent(q)}` : "";
  return apiGet<{ items: Array<Record<string, unknown>>; message?: string | null; source_mode: string; live_verified?: boolean; hybrid_mode?: boolean; prototype_demo?: boolean }>(
    `/api/catalog/candidates${qs}`,
  );
}

export async function fetchCandidate(userId: string) {
  return apiGet<{
    candidate: Record<string, unknown> | null;
    skills: Array<Record<string, unknown>>;
    evidence: Array<Record<string, unknown>>;
    relevant_jobs?: Array<Record<string, unknown>>;
    message?: string | null;
    source_mode: string;
  }>(`/api/catalog/candidates/${encodeURIComponent(userId)}`);
}

export async function fetchJobs(q?: string) {
  const qs = q ? `?q=${encodeURIComponent(q)}` : "";
  return apiGet<{ items: Array<Record<string, unknown>>; message?: string | null; source_mode: string; hybrid_mode?: boolean; prototype_demo?: boolean }>(
    `/api/catalog/jobs${qs}`,
  );
}

export async function fetchJob(jobId: string) {
  return apiGet<{
    job: Record<string, unknown> | null;
    requirements: Array<Record<string, unknown>>;
    organization: Record<string, unknown> | null;
    message?: string | null;
    source_mode: string;
  }>(`/api/catalog/jobs/${encodeURIComponent(jobId)}`);
}

export async function fetchOrganizations(q?: string) {
  const qs = q ? `?q=${encodeURIComponent(q)}` : "";
  return apiGet<{ items: Array<Record<string, unknown>>; message?: string | null }>(`/api/catalog/organizations${qs}`);
}

export async function fetchHrReviewers(q?: string) {
  const qs = q ? `?q=${encodeURIComponent(q)}` : "";
  return apiGet<{ items: Array<Record<string, unknown>>; message?: string | null }>(`/api/catalog/hr${qs}`);
}

export async function createProductCase(candidateId: string, jobId: string, executeUntil?: string) {
  const res = await fetch(apiUrl("/api/cases"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      candidate_id: candidateId,
      job_id: jobId,
      opportunity_id: jobId,
      ...(executeUntil ? { execute_until: executeUntil } : {}),
    }),
  });
  if (!res.ok) {
    const detail = await res.json().catch(() => ({}));
    throw new Error((detail as { detail?: string }).detail || "Failed to create case");
  }
  return res.json() as Promise<{ id: string }>;
}

export async function executeProductCase(caseId: string) {
  const res = await fetch(apiUrl(`/api/cases/${encodeURIComponent(caseId)}/execute`), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ execute_until: "FINALE" }),
  });
  if (!res.ok) {
    const detail = await res.json().catch(() => ({}));
    throw new Error((detail as { detail?: string }).detail || "Case execution failed");
  }
  return res.json() as Promise<{ id: string }>;
}

export async function mutateCatalog(path: string, method: "POST" | "PUT", payload: Record<string, unknown>) {
  const res = await fetch(apiUrl(path), {
    method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ payload }),
  });
  const body = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error((body as { detail?: string }).detail || "SAP mutation failed");
  }
  return body;
}

type StudentSkillResult = {
  ok: boolean;
  log?: string[];
  detail?: string;
  item?: { records?: Array<{ SkillId: string; SkillName: string; Description: string }> } & Record<string, unknown>;
};

async function studentPost(endpoint: string, payload: Record<string, unknown> = {}): Promise<StudentSkillResult> {
  const res = await fetch(apiUrl(`/api/student/${endpoint}`), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ payload }),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error((body as { detail?: string }).detail || `Request failed (${res.status})`);
  }
  return res.json() as Promise<StudentSkillResult>;
}

export function studentGetAllSkills() {
  return studentPost("get-skills");
}

export function studentGetSkill(skillId: string) {
  return studentPost("get-skill", { SkillId: skillId });
}

export function studentCreateSkill(payload: Record<string, unknown>) {
  return studentPost("create-skill", payload);
}

export function studentUpdateSkill(payload: Record<string, unknown>) {
  return studentPost("update-skill", payload);
}

export function studentDeleteSkill(skillId: string) {
  return studentPost("delete-skill", { SkillId: skillId });
}

export async function fetchScenarios() {
  const res = await fetch(apiUrl("/api/demo/scenarios"), { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to load scenarios");
  return res.json();
}

export async function submitReview(payload: {
  run_id: string;
  decision_card_id: string;
  action: string;
  reviewer_id?: string;
  reason?: string;
  modified_interventions?: string[];
  modified_pathway?: string;
  comments?: string;
}) {
  const res = await fetch(apiUrl("/api/reviews"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Review submission failed");
  return res.json();
}

export async function resetDemoCase() {
  const res = await fetch(apiUrl("/api/demo/reset"), { method: "POST" });
  if (!res.ok) throw new Error("Failed to reset demo case");
  return res.json();
}

export async function fetchSapDiagnostics() {
  const res = await fetch(apiUrl("/api/sap/diagnostics"), { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to load SAP diagnostics");
  return res.json();
}

export async function fetchSapTrace() {
  const res = await fetch(apiUrl("/api/sap/trace"), { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to load SAP trace");
  return res.json();
}

export async function submitCaseReview(caseId: string, payload: {
  action: string;
  reviewer_id?: string;
  reason?: string;
  reviewed_case_version?: number;
}) {
  const res = await fetch(apiUrl(`/api/cases/${caseId}/review`), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Case review submission failed");
  return res.json();
}

export const API_URL = getApiBaseUrl();

export async function generateLearningPlan(candidateId: string, roleId: string) {
  const res = await fetch(apiUrl("/api/learning-plans/generate"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ candidate_id: candidateId, role_id: roleId }),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error((body as { detail?: string }).detail || "Failed to generate learning plan");
  }
  return res.json() as Promise<Record<string, unknown>>;
}

export async function simulateLearningIntervention(planId: string, gapId?: string) {
  const res = await fetch(apiUrl(`/api/learning-plans/plan/${planId}/simulate`), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ gap_id: gapId ?? null }),
  });
  if (!res.ok) throw new Error("Simulation failed");
  return res.json() as Promise<Record<string, unknown>>;
}

export async function fetchLearningResources() {
  return apiGet<{
    catalog_label: string;
    source_type: string;
    count: number;
    resources: Array<Record<string, unknown>>;
  }>("/api/learning-plans/catalog/resources");
}
