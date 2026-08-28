const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function fetchControlRoom(caseId?: string) {
  const path = caseId
    ? `${API_BASE}/api/cases/${caseId}/control-room`
    : `${API_BASE}/api/demo/control-room`;
  const res = await fetch(path, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to load control room");
  return res.json();
}

export async function fetchScenarios() {
  const res = await fetch(`${API_BASE}/api/demo/scenarios`, { cache: "no-store" });
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
  const res = await fetch(`${API_BASE}/api/reviews`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Review submission failed");
  return res.json();
}

export async function resetDemoCase() {
  const res = await fetch(`${API_BASE}/api/demo/reset`, { method: "POST" });
  if (!res.ok) throw new Error("Failed to reset demo case");
  return res.json();
}

export async function submitCaseReview(caseId: string, payload: {
  action: string;
  reviewer_id?: string;
  reason?: string;
  reviewed_case_version?: number;
}) {
  const res = await fetch(`${API_BASE}/api/cases/${caseId}/review`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Case review submission failed");
  return res.json();
}

export const API_URL = API_BASE;
