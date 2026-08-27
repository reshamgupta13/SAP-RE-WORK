# Implementation Checkpoint 04

**Date:** 2026-08-28  
**Branch:** `feature/rework-p0`  
**Scope:** Learning Pathway + Proof-of-Skill + Capability Refresh + Reassessment  
**Prerequisite:** Checkpoint 03 (`12c4908`)

---

## 1. Pathway architecture

```
Diagnosed GENUINE_CAPABILITY_GAP
        ↓
PathwayEngine (minimum-effective pathway)
        ↓
SAPLearningProvider.search_learning_items()
        ↓
LearningPath with milestones + practical tasks
        ↓
ProofOfSkillEngine (structured rubric task)
        ↓
CapabilityUpdateService (evidence-backed refresh)
        ↓
DiagnosisService (reassessment — reused, not shortcut)
```

LangGraph nodes: `pathway_generation` → `proof_of_skill` → `capability_refresh` → `reassessment`

Run modes: `ANALYZE_ONLY`, `GENERATE_PATHWAY`, `EVALUATE_PROOF`, `FULL_DEMO_REPLAY`

---

## 2. Learning selection logic

PathwayEngine selects the **primary genuine capability gap** (core importance × gap magnitude) and generates:

- Targeted learning items (max 4) from SAP Learning catalog
- Milestones: foundations → dashboard practice → analytics project → proof
- Practical tasks bound to the gap capability
- Structured explanation: `why`, `what`, `how`, `success_criteria`

No unrelated course spam — Power BI gap does not produce a generic analytics bootcamp.

---

## 3. SAP Learning adapter

| Component | Status |
|---|---|
| `SAPLearningProvider` interface | ✅ |
| `SimulatedSAPLearningProvider` | ✅ `source_mode=SIMULATED` |
| `LiveSAPLearningProvider` stub | ✅ not connected |
| Expanded catalog in `fixtures/sap/simulated_context.json` | ✅ |

`SimulatedSAPProvider` write-back stubs: `update_skill_progress()`, `record_learning_completion()` — local simulated records only.

**No live SAP Learning API calls.**

---

## 4. Proof-of-Skill model

| Model | Purpose |
|---|---|
| `ProofOfSkillAssessment` | Task + rubric criteria |
| `ProofSubmission` | Candidate/demo responses |
| `ProofOfSkillResult` | Deterministic rubric scores |
| `ProofEvidence` | Assessment-backed evidence record |
| `CapabilityUpdateEvent` | Auditable proficiency change |

Power BI task: sales dataset dashboard with trends, regions, declining segment analysis.

---

## 5. Rubric

Criteria (deterministic weights):

- Data Preparation (25%)
- Dashboard Construction (25%)
- Visualization Quality (20%)
- Business Insight (20%)
- Communication (10%)

Pass threshold: 0.70. No personality or protected-attribute judgment.

---

## 6. Capability update

On **PASSED** proof:

- New `CandidateEvidence` (type `ASSESSMENT`, `VERIFIED`)
- Proficiency raised to at least role-required threshold when score ≥ 0.70
- `verification_status = VERIFIED_BY_ASSESSMENT`
- Historical evidence preserved (append, not overwrite)
- `CapabilityUpdateEvent` recorded

Failed proof does **not** improve capability.

---

## 7. Reassessment

Reuses `DiagnosisService` on updated capabilities — no special shortcut scoring.

After Ananya demo replay: Power BI moves from `GENUINE_CAPABILITY_GAP` to `MATCHED`.

---

## 8. Ananya before/after

| | Before | After (FULL_DEMO_REPLAY) |
|---|---|---|
| Power BI proficiency | ~0.22 | ≥ 0.60 (role threshold) |
| Power BI gap status | `GENUINE_CAPABILITY_GAP` | `MATCHED` |
| Verification | `SELF_REPORTED` | `VERIFIED_BY_ASSESSMENT` |
| Pathway status | — | `COMPLETED` |
| Proof | — | Demo synthetic (`is_demo=true`) |

Experience proxy and workplace constraints remain for human review — not auto-resolved by pathway.

---

## 9. Demo fallback

- `FULL_DEMO_REPLAY` uses `fixtures/proof/ananya_power_bi_demo.json`
- Explicitly labeled `source_mode=SYNTHETIC`, `is_demo=true`
- Not presented as a real candidate submission
- `engine_mode=DEMO_FALLBACK` when no LLM key

---

## 10. Tests

| Suite | Count |
|---|---|
| Checkpoint 01–03 | 70 |
| Pathway + proof | 17 |
| **Total** | **87 passed** |

Covers: pathway binding, practical tasks, proof rubric, failed proof guard, capability refresh, reassessment, API endpoints, golden CP4, SAP learning adapter.

---

## 11. Known limitations

- Proof evaluation is deterministic rubric only (no LLM free-text grading yet)
- Credential/experience proxies not resolved by pathway alone
- No opportunity matching or market intelligence
- No HR review UI
- Write-back to live SAP not implemented
- In-memory run store only

---

## 12. Next checkpoint

**Market Intelligence + Inclusive Opportunity Matching**

---

## 13. API quick reference

```bash
# Pathway only (stops after pathway_generation)
curl -X POST http://localhost:8000/api/runs/pathway \
  -H "Content-Type: application/json" \
  -d '{"candidate_id":"ananya-sharma","job_id":"data-analyst-junior"}'

# Full demo replay (pathway + synthetic proof + reassessment)
curl -X POST http://localhost:8000/api/runs/proof \
  -H "Content-Type: application/json" \
  -d '{"candidate_id":"ananya-sharma","job_id":"data-analyst-junior"}'
```

---

**No live SAP integration has been claimed or implemented.**
