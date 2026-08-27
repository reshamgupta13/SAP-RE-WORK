# Implementation Checkpoint 02

**Date:** 2026-08-28  
**Branch:** `feature/rework-p0`  
**Scope:** Candidate Intelligence + Job Decomposition + LangGraph skeleton + LLM abstraction  
**Prerequisite:** Checkpoint 01 (`818126e`)

---

## 1. What was implemented

| Component | Status |
|---|---|
| LangGraph state (`ReworkGraphState`) | ✅ |
| Graph: load_candidate → candidate_intelligence → load_job → job_decomposition | ✅ |
| `LLMProvider` abstraction | ✅ |
| `ConfiguredLLMProvider` (Gemini REST, env key) | ✅ |
| `DeterministicFallbackProvider` | ✅ |
| `CandidateIntelligenceAgent` | ✅ |
| `JobDecompositionAgent` | ✅ |
| Confidence derivation (`system_confidence`) | ✅ |
| Audit events per node | ✅ |
| In-memory `RunStore` | ✅ |
| API: `POST /api/runs`, `GET /api/runs/{id}`, partial agent endpoints | ✅ |
| Golden snapshot `fixtures/golden/checkpoint_02_ananya.json` | ✅ |
| Tests (49 total, all passing) | ✅ |

**Not implemented (by design):** diagnosis, counterfactual, pathway, proof, matching, market intelligence, human review UI, frontend orchestration.

---

## 2. Architecture changes

```
POST /api/runs
    → OrchestrationService
    → LangGraph (4 nodes)
        → CandidateIntelligenceAgent (LLMProvider)
        → JobDecompositionAgent (LLMProvider)
    → RunStore (in-memory)
```

SAP data enters only via `SAPProvider` in `load_candidate` — agents do not call SAP directly.

---

## 3. Agent contracts

### CandidateIntelligenceAgent

| | |
|---|---|
| **Input** | `CandidateProfile`, `list[CandidateEvidence]`, optional `SAPContext` |
| **Output** | `list[CandidateCapability]`, rationale string |
| **Engine** | `LLM` if `LLM_API_KEY` set; else `DEMO_FALLBACK` |

### JobDecompositionAgent

| | |
|---|---|
| **Input** | `JobProfile` |
| **Output** | `RoleOutcome[]`, `JobTask[]`, `JobCapability[]`, `JobRequirement[]` (as requirement analyses), rationale |
| **Engine** | Same as above |

Neither agent produces hiring recommendations.

---

## 4. LangGraph state

`ReworkGraphState` fields:

- `run_id`, `status`, `engine_mode`, `candidate_id`, `job_id`
- `candidate`, `job`, `sap_context` (JSON dicts)
- `candidate_evidence`, `candidate_capabilities`
- `job_tasks`, `job_capabilities`, `role_outcomes`, `requirement_analyses`
- `audit_events` (append reducer), `errors` (append reducer)

Serializable via `model_dump(mode="json")` at boundaries.

---

## 5. LLM provider design

```python
LLMProvider.generate_structured(prompt, schema, context) -> Pydantic model
```

- **ConfiguredLLMProvider:** Gemini `generateContent` with `responseMimeType=application/json`, validated against Pydantic schema.
- **DeterministicFallbackProvider:** Requires `context["fallback_payload"]` — no fake NLP.
- **Factory:** `get_llm_provider()` uses `LLM_API_KEY` from env; otherwise fallback.

Env vars: `LLM_PROVIDER`, `LLM_API_KEY`, `LLM_MODEL`, `LLM_TIMEOUT` (via settings).

---

## 6. Fallback behavior

- Ananya: fixture-backed capabilities + inferred `data_analysis` / `reporting` when MIS/reporting evidence supports.
- Data Analyst job: uses structured fixture tasks/capabilities/requirements.
- `engine_mode = DEMO_FALLBACK` when no API key.
- LLM failures inside agents catch and re-run deterministic fallback payload.
- Demo runs are stable (no random business scores).

---

## 7. SAP interaction

- `load_candidate` loads `SAPContext` via `SimulatedSAPProvider`.
- `source_mode=SIMULATED` preserved in state.
- External candidate (Ananya): empty SAP employee skills — correct.
- Agents use neutral phrasing in prompts; no “According to SAP” unless context is SAP-sourced.

**No live SAP integration has been claimed or implemented.**

---

## 8. Tests

| Suite | Count |
|---|---|
| Checkpoint 01 tests | 21 |
| Candidate intelligence | 9 |
| Job decomposition | 7 |
| Orchestration + golden | 7 |
| Runs API | 5 |
| **Total** | **49 passed** |

---

## 9. Known limitations

- Runs stored in memory only (lost on restart).
- No diagnosis / matching / pathways.
- LLM path requires network + valid key; demo uses fallback.
- `ConfiguredLLMProvider` only implements Gemini REST today.
- Job decomposition fallback requires pre-structured fixture (not free-text JD parsing for arbitrary jobs).

---

## 10. Example Ananya output (DEMO_FALLBACK)

**Capabilities (skill_ids):** `sql`, `excel`, `communication`, `power_bi`, `data_analysis`, `reporting`

**Power BI:** low proficiency, `verification_status=SELF_REPORTED`, evidence `ev-ananya-self-powerbi`

**Job tasks:** `task-da-sql`, `task-da-dashboard`, `task-da-communicate`

**Experience requirement:** `EXPERIENCE_REQUIREMENT` — “3 years continuous recent professional experience”

**No hiring recommendation produced.**

---

## 11. Next checkpoint

**Diagnosis + Capability Gap + Counterfactual Engine** (Checkpoint 3 per master plan).

---

## 12. API quick reference

```bash
# Full integrated run
curl -X POST http://localhost:8000/api/runs -H "Content-Type: application/json" -d "{}"

# Partial
curl -X POST http://localhost:8000/api/runs/candidate-intelligence -d '{"candidate_id":"ananya-sharma"}'
curl -X POST http://localhost:8000/api/runs/job-decomposition -d '{"job_id":"data-analyst-junior"}'
```

---

**No live SAP integration has been claimed or implemented.**
