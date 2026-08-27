# 05 — End-to-End Workforce Loop

RE:WORK is a **closed loop**, not a recommend-and-forget matcher.

```
DISCOVER -> DECOMPOSE -> DIAGNOSE -> RECOMPOSE -> DEVELOP
    -> PROVE -> MATCH -> REVIEW -> LEARN ----+
         ^                                   |
         +-----------------------------------+
```

Each stage writes to shared state (see `07_SHARED_STATE_AND_ORCHESTRATION.md`). Stages can skip only when inputs already exist and are still valid (idempotent re-entry).

---

## Stage contracts

### 1. DISCOVER — What can this person actually do?

| | |
|---|---|
| **Owner** | Candidate Intelligence Agent + deterministic validators |
| **Inputs** | Resume/CV, projects, self-report, optional SAP Growth Portfolio / EC / learning history, user-provided constraints (location, work mode, language, accessibility *if volunteered*) |
| **Outputs** | `CandidateProfile`, `EvidenceSet`, `CapabilityAssessment` (graph of capabilities with proficiency, confidence, recency, source) |
| **Must not** | Infer protected characteristics; invent employers; treat gap as negative skill |
| **Human** | Candidate confirms/corrects high-impact inferences before HR sees them (P1; P0 may use confirm-on-review) |
| **Provenance** | Each evidence node labeled LIVE / SIMULATED / SYNTHETIC / MOCKED / USER-PROVIDED |

### 2. DECOMPOSE — What does the job actually require?

| | |
|---|---|
| **Owner** | Job Decomposition Agent |
| **Inputs** | Requisition text + structured fields; optional SAP Job Profile |
| **Outputs** | `JobProfile` structured: outcomes, responsibilities, tasks, capabilities, evidence expectations, conditions, credential/experience clauses, each with `requirement_class` |
| **Must not** | Label clauses as “biased” automatically |
| **Human** | HR can edit classes before matching (employer-readiness) |
| **Confidence** | Lower if only unstructured JD; higher if JPB-like structure present |

### 3. DIAGNOSE — Genuine gaps vs possible proxies

| | |
|---|---|
| **Owner** | Diagnosis Agent (gap + barrier in one node) |
| **Inputs** | `CapabilityAssessment` + `JobProfile` |
| **Outputs** | `CapabilityGap[]`, `BarrierAssessment[]`, overall `DiagnosisSummary` |
| **Questions** | What is missing as capability? What is missing as evidence? What may be a proxy? How sure are we? |
| **Must not** | Auto-remove requirements; auto-fail the candidate |
| **Escalation** | Any `unknown_needs_review` or confidence < threshold |

### 4. RECOMPOSE — Realistic pathway from person to opportunity

| | |
|---|---|
| **Owner** | Pathway Agent (recomposition) |
| **Inputs** | Diagnosis + market signals (optional) + policy bounds (max weeks, cost, proof allowed) |
| **Outputs** | `RecompositionPlan`: target role stay/adjust, requirement-substitution *proposals*, pathway skeleton, or `no_viable_path` |
| **Must not** | Promise a job; change SAP requisition automatically |
| **Human** | HR must accept proposed requirement substitutions |

### 5. DEVELOP — Learning, practice, mentorship, accommodation

| | |
|---|---|
| **Owner** | Pathway Agent + Learning item mapper |
| **Inputs** | Gaps classified as trainable; SAP Learning catalog if available |
| **Outputs** | `LearningPath` with items mapped to capabilities, duration, completion criteria |
| **Must not** | Dump unrelated popular courses |
| **SAP** | Map to SuccessFactors Learning / Learning Hub titles when verified |

### 6. PROVE — Demonstrate the missing capability

| | |
|---|---|
| **Owner** | Proof-of-Skill service (deterministic rubric + optional LLM assist for open-ended work) |
| **Inputs** | Target capability, task brief, submission |
| **Outputs** | `ProofOfSkillResult` → new evidence → updated capability confidence |
| **Must not** | Discriminatory or medically sensitive tests; puzzles unrelated to the role |
| **Human** | Manager/HR can accept, request redo, or override score |

### 7. MATCH — Current + future fit

| | |
|---|---|
| **Owner** | Inclusive Matching (deterministic scoring) + LLM for narrative only |
| **Inputs** | Updated capabilities, opportunities, constraints, diagnosis, pathway |
| **Outputs** | `OpportunitySet` + `MatchRecommendation[]` with `readiness_state` |
| **Readiness** | `ready_now` \| `ready_with_proof` \| `ready_with_bounded_pathway` \| `not_ready` |
| **Must not** | Rank by protected class; hide scores |

### 8. REVIEW — Human judgment

| | |
|---|---|
| **Owner** | Governance layer (deterministic state machine) |
| **Inputs** | Recommendation + explainability pack |
| **Outputs** | `HumanDecision`: approve / modify / reject / defer; comments; field-level overrides |
| **Must not** | Proceed to “hired” or “rejected from company” as an autonomous state |
| **Actors** | Candidate (pathway consent) and HR (employment-affecting actions) |

### 9. LEARN — Improve from outcomes

| | |
|---|---|
| **Owner** | Outcome logging + offline eval (not a live self-training loop in P0) |
| **Inputs** | Decisions, later hire/success flags if provided |
| **Outputs** | `Outcome` records; eval metrics; optional prompt/rule patches by engineers |
| **Must not** | Automatically retrain a model on demographic outcomes |
| **P0** | Store outcomes; do not claim online learning |

---

## Control flow (prototype)

P0 is a **single LangGraph graph**, not nine microservices:

1. `load_context` (SAP adapter + user uploads)
2. `discover`
3. `decompose`
4. `diagnose`
5. `recompose_and_develop` (pathway)
6. `match`
7. `bias_audit_snapshot` (deterministic aggregates + LLM narrative)
8. `await_human_review`
9. `record_decision`

`prove` is a **side loop**: can run after pathway generation or after HR says “request proof.” P0 demo uses a **pre-seeded proof result** for speed, with UI that still shows the mechanism.

Market intelligence runs **inside** `recompose` and `match` as a tool, not a separate chatbot.

---

## Failure and skip rules

| Condition | Behavior |
|---|---|
| Missing JD | Stop. Ask HR for a role. |
| Missing candidate evidence | Discover with low confidence; escalate. |
| SAP adapter down | Continue with USER-PROVIDED + SIMULATED flags; show degraded banner. |
| LLM timeout | Use cached demo fixtures in `DEMO_MODE`; else fail the node with retry ≤2. |
| `no_viable_path` | Still show diagnosis and human review; do not invent a match. |
| Human reject | Persist; do not delete evidence; allow re-run after JD edit. |

---

## Loop on the flagship persona (preview)

Ananya, Lucknow, 3-year break, prior BA/MIS work:

- DISCOVER: SQL, stakeholder communication, requirements, Excel — evidenced; dashboarding weak; gap is not “no skills.”
- DECOMPOSE: Junior Data Analyst — SQL + analysis tasks real; “3 years continuous,” “Bangalore,” “premier institute” classified as potential proxies / workplace conditions.
- DIAGNOSE: one trainable capability gap (BI dashboarding); several eligibility gaps.
- RECOMPOSE: keep performance bar; propose evidence-of-SQL + 4-week Power BI path + hybrid work review.
- DEVELOP/PROVE: Learning Hub-mapped items + SQL/BI work sample.
- MATCH: `ready_with_bounded_pathway` on two roles; `not_ready` on senior DE.
- REVIEW: HR accepts pathway match, rejects location rewrite without policy change.
- LEARN: store decision (P0).
