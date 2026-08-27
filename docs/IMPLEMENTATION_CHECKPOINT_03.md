# Implementation Checkpoint 03

**Date:** 2026-08-28  
**Branch:** `feature/rework-p0`  
**Scope:** Capability Gap + Requirement Diagnosis + Counterfactual Engine  
**Prerequisite:** Checkpoint 02 (`b47fac9`)

---

## 1. What was implemented

| Component | Status |
|---|---|
| `CapabilityGapEngine` — deterministic capability comparison | ✅ |
| `DiagnosisEngine` — requirement-level diagnosis | ✅ |
| `CounterfactualEngine` — structured counterfactual analysis | ✅ |
| `DiagnosisService` — orchestrates gap + diagnosis + counterfactual | ✅ |
| `DiagnosisSummary` with multi-dimensional fit (not single score) | ✅ |
| `RequirementDiagnosis` with barrier classification | ✅ |
| LangGraph nodes: `diagnosis`, `counterfactual_analysis` | ✅ |
| API: `POST /api/runs/diagnose` | ✅ |
| Golden snapshot `fixtures/golden/checkpoint_03_ananya.json` | ✅ |
| Tests (70 total, all passing) | ✅ |

**Not implemented (by design):** pathway generation, proof-of-skill, market intelligence, inclusive matching, HR review UI, frontend dashboard, live SAP.

---

## 2. Diagnosis architecture

```
Candidate capabilities + Job capabilities
        ↓
CapabilityGapEngine (deterministic)
        ↓
RequirementDiagnosis (deterministic, requirement-class aware)
        ↓
CounterfactualEngine (deterministic)
        ↓
DiagnosisSummary
```

LLM is **not** used in diagnosis classification. Checkpoint 2 LLM/fallback agents feed structured inputs; all diagnosis logic is rule-driven.

---

## 3. Capability gap logic

For each `JobCapability`:

| Condition | `GapStatus` |
|---|---|
| Candidate meets/exceeds required proficiency with sufficient evidence | `MATCHED` |
| Candidate below threshold with evidenced proficiency | `GENUINE_CAPABILITY_GAP` |
| No capability or insufficient evidence | `INSUFFICIENT_EVIDENCE` |

**Principle:** absence of evidence ≠ evidence of absence.

`evidence_strength` is a heuristic (verification tier, evidence type, recency, count) — not a calibrated probability.

---

## 4. Requirement classification handling

| `RequirementClass` | Typical `diagnosis_type` |
|---|---|
| `DIRECT_CAPABILITY` | From capability assessment |
| `EXPERIENCE_REQUIREMENT` | `ELIGIBILITY_PROXY` |
| `WORKPLACE_CONDITION` | `WORKPLACE_CONSTRAINT` |
| `CREDENTIAL_REQUIREMENT` | `UNKNOWN_REQUIRES_HUMAN_REVIEW` |
| `EVIDENCE_REQUIREMENT` | `MATCHED` or `INSUFFICIENT_EVIDENCE` |
| `UNKNOWN` | `UNKNOWN_REQUIRES_HUMAN_REVIEW` |

Statutory keywords (visa, citizenship, clearance, license) force human review with no automatic substitution.

---

## 5. Counterfactual engine

Question: *If this requirement were replaced by direct capability evidence, would readiness still fail?*

`CounterfactualConclusion` values:

- `REQUIREMENT_APPEARS_JOB_RELEVANT`
- `POTENTIAL_PROXY`
- `INSUFFICIENT_EVIDENCE`
- `REQUIRES_HUMAN_REVIEW`

**Never:** discrimination verdicts, hire/reject, or requirement deletion.

---

## 6. Ananya result (DEMO_FALLBACK)

| Capability | Diagnosis |
|---|---|
| SQL | `MATCHED` |
| Excel | `MATCHED` |
| Communication | `MATCHED` |
| Power BI | `GENUINE_CAPABILITY_GAP` |

| Requirement | Diagnosis |
|---|---|
| 3 years continuous experience | `ELIGIBILITY_PROXY` → counterfactual `POTENTIAL_PROXY` |
| Bangalore office 5 days/week | `WORKPLACE_CONSTRAINT` |
| Premier institute preferred | `UNKNOWN_REQUIRES_HUMAN_REVIEW` |

**Career gap:** profile context only — not classified as a skill or capability failure.

**Overall:** `MATCH_WITH_GAPS` / `POTENTIALLY_VIABLE` with human review flags on proxy and constraint items.

**No hiring recommendation produced.**

---

## 7. LLM vs deterministic responsibilities

| Layer | Responsibility |
|---|---|
| Candidate Intelligence (CP2) | Evidence-aware capability extraction |
| Job Decomposition (CP2) | Task/capability/requirement structure |
| Diagnosis (CP3) | **Deterministic** gap comparison and classification |
| Counterfactual (CP3) | **Deterministic** proxy/constraint reasoning |

LLM may assist extraction in CP2; it has no unilateral authority over diagnosis outcomes.

---

## 8. SAP interaction

Diagnosis consumes structured state from CP2. SAP context remains `source_mode=SIMULATED` via adapter. No SAP-specific logic in diagnosis engines.

**No live SAP integration has been claimed or implemented.**

---

## 9. Tests

| Suite | Focus |
|---|---|
| Checkpoint 01–02 (49) | Regression |
| Diagnosis scenarios (19) | Matched, gap, missing evidence, proxy, constraint, credential, negative guards |
| Orchestration updates | 6-node graph, diagnosis fields |
| API | `POST /api/runs/diagnose` |
| Golden CP3 | Ananya structural expectations |

**Total: 70 passed**

Negative tests verify: no discrimination verdicts, no hiring decision, career gap not a skill, no single match score.

---

## 10. Known limitations

- Diagnosis is heuristic and demo-fixture oriented for fallback path.
- Credential-to-capability substitution uses evidenced capabilities broadly; semantic task mapping is limited.
- `capability_fit` / `evidence_strength` / `diagnosis_confidence` are not calibrated probabilities.
- In-memory run store only.
- No pathway or proof-of-skill refresh of aging evidence yet.

---

## 11. Next checkpoint

**Pathway + Proof-of-Skill Engine** — bounded upskilling recommendations and evidence refresh for aging capabilities.

---

## 12. API quick reference

```bash
# Full diagnosis run (intelligence + diagnosis + counterfactual)
curl -X POST http://localhost:8000/api/runs/diagnose \
  -H "Content-Type: application/json" \
  -d '{"candidate_id":"ananya-sharma","job_id":"data-analyst-junior"}'
```

---

**No live SAP integration has been claimed or implemented.**
