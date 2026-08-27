# 06 — Agent Architecture

**Design rule:** Agents are specialized reasoning units, not slide labels.  
**Hackathon rule:** At least one agent must be genuinely functional. The orchestrator must still *look complete*.

We do **not** implement 10 LLM agents.

---

## 1. Compression of the proposed 10

| Original idea | Decision | Why |
|---|---|---|
| 1. Candidate Intelligence | **Keep (LLM)** | Core extraction/synthesis |
| 2. Job Decomposition | **Keep (LLM)** | Core extraction/classification |
| 3. Evidence / Skill Verification | **Merge into Candidate Intelligence + deterministic validators** | Verification is schema/validation, not a persona |
| 4. Capability Gap Agent | **Merge into Diagnosis Agent** | Gap and barrier share one comparison |
| 5. Market Intelligence | **Service + optional LLM briefing** | Mostly retrieval/ranking; LLM writes the memo |
| 6. Barrier & Bias Audit | **Barrier: inside Diagnosis. Bias audit: deterministic batch service + LLM narrative** | Continuous “bias agent” as a chatbot is theater |
| 7. Inclusive Opportunity Matching | **Deterministic scorer + LLM explanation** | Scoring must be reproducible |
| 8. Job Recomposition | **Merge into Pathway Agent** | Recomposition *is* the plan |
| 9. Learning Pathway | **Same Pathway Agent** | One plan object |
| 10. Human Review / Governance | **Deterministic state machine** | Not an LLM. LLMs do not approve jobs |

**Hackfest-named Employer Readiness:** a **view + checklist** over Job Decomposition output, not a separate agent. HR edits requirement classes.

---

## 2. Runtime map

```
                    +-------------------+
                    |  Orchestrator     |
                    |  (LangGraph)      |
                    |  deterministic    |
                    +---------+---------+
                              |
        +---------------------+---------------------+
        v                     v                     v
 Candidate Intel        Job Decomposition      Diagnosis
     (LLM)                   (LLM)            (LLM+rules)
        |                     |                     |
        +----------+----------+----------+----------+
                   v                     v
            Pathway Agent         Matching Scorer
               (LLM)               (deterministic)
                   |                     |
                   +----------+----------+
                              v
                    Explainability LLM
                    (narrative only)
                              v
                    Governance (human)
```

**Functional prototype of at least one agent:** Candidate Intelligence and Job Decomposition are both real P0 LLM nodes. Diagnosis is the third. Matching is intentionally *not* an LLM.

---

## 3. Shared conventions

### Confidence

- `0.0–1.0` on every agent artifact.
- Orchestrator stores `min` of critical dependencies for downstream `inherited_confidence`.
- UI: High ≥ 0.75, Medium 0.5–0.74, Low < 0.5. Low always escalates.

### Failure modes (all LLM nodes)

- Hallucinated employers, dates, skills
- Over-labeling proxies as “must drop”
- Under-labeling genuine capability gaps
- Inventing market statistics
- Inventing SAP records

**Mitigations:** grounded extraction (quote spans), schema validation, allowlists for skill IDs, demo fixtures, no silent defaults to “inclusive hire.”

### Audit

Every node writes `AuditEvent`: agent, graph_node, input_hash, output_json, confidence, latency_ms, model_id, prompt_version, error, fallback.

---

## 4. Agent specs

### 4.1 Orchestrator (not an LLM)

- **Responsibility:** State transitions, retries, DEMO_MODE short-circuit, human interrupt.
- **Input:** `RunRequest` `{ candidate_id, job_id, mode, actor }`
- **Output:** Final `RecommendationBundle` + `HumanDecision` slot
- **Tools:** All node invocations
- **Deterministic checks:** Required keys present; provenance enum valid; no hire state
- **Escalation:** Node error after retries → `status=failed` with reason
- **Human:** Interrupt before persist of HR decision
- **Hallucination risk:** None (must not “think”)
- **Dependencies:** All

### 4.2 Candidate Intelligence Agent

- **Responsibility:** Build capability graph from heterogeneous evidence. Surface ability, not pedigree.
- **Input schema (conceptual):**
```json
{
  "candidate_id": "uuid",
  "documents": [{"type": "resume|project|self_report|other", "text": "...", "provenance": "USER-PROVIDED"}],
  "sap_context": {
    "growth_portfolio": null,
    "learning_history": null,
    "employee": null,
    "provenance": "SIMULATED"
  },
  "constraints": {"location": "Lucknow", "work_modes": ["hybrid", "remote"], "languages": ["en", "hi"]}
}
```
- **Output schema:**
```json
{
  "capabilities": [{
    "skill_id": "sql",
    "label": "SQL",
    "proficiency": 0.0,
    "confidence": 0.0,
    "recency": "YYYY-MM",
    "transferable": true,
    "evidence_ids": ["e1"],
    "inference_type": "explicit|inferred|transfer"
  }],
  "evidence": [{
    "id": "e1",
    "type": "work_history|artifact|self_report|sap_rating|proof",
    "summary": "...",
    "span_or_ref": "...",
    "date": "YYYY-MM",
    "provenance": "USER-PROVIDED",
    "confidence": 0.0
  }],
  "career_timeline": [{"from": "", "to": "", "kind": "employment|break|education|project", "notes": ""}],
  "confidence": 0.0,
  "unknowns": ["..."]
}
```
- **Tools:** Document parse (PDF/DOCX) — P1; P0 text paste. SAP adapter get context. Skill ID allowlist lookup.
- **Reasoning:** Extract, normalize to skill IDs, infer adjacent with lower confidence, **do not** treat caregiving break as skill loss.
- **Deterministic checks:** Skill IDs ∈ catalog; dates parseable; no protected-class fields; every inferred capability has evidence_id or is marked `unsupported` and dropped.
- **Escalation:** confidence < 0.5; conflicting dates; empty evidence
- **Human review:** Candidate/HR can strike a capability
- **Hallucination:** Invented employers/skills — require quote/ref
- **Dependencies:** Skill catalog, SAP adapter optional

### 4.3 Job Decomposition Agent

- **Responsibility:** Turn JD/requisition into typed requirements and tasks.
- **Input:** `{ "job_id", "title", "raw_text", "structured_fields": {}, "sap_job_profile": null, "provenance": "SIMULATED" }`
- **Output:** See `09_JOB_DECOMPOSITION_MODEL.md`. Minimum:
```json
{
  "outcomes": [],
  "tasks": [{"id": "t1", "text": "", "capability_ids": ["sql"]}],
  "requirements": [{
    "id": "r1",
    "text": "3 years continuous experience",
    "class": "experience_requirement",
    "review_tag": "potential_proxy|none|unknown_needs_review",
    "why_may_be_relevant": "",
    "why_may_be_proxy": "",
    "confidence": 0.0
  }],
  "workplace_conditions": [],
  "confidence": 0.0
}
```
- **Tools:** Skill catalog; optional JPB JSON
- **Reasoning:** Map tasks → capabilities; classify requirements; never output “this is biased”
- **Deterministic checks:** Every requirement has class ∈ enum; `review_tag` required if class is experience/credential/institution/location-hard-filter
- **Escalation:** Legal/license-like requirements (`unknown_needs_review` if unsure)
- **Human:** Employer-readiness edit
- **Hallucination:** Invented must-have skills not in JD — forbid unless marked `inferred_from_tasks` with lower confidence
- **Dependencies:** Skill catalog

### 4.4 Diagnosis Agent (Gap + Barrier)

- **Responsibility:** Compare person vs role. Split capability vs eligibility. Produce counterfactual notes.
- **Input:** Candidate Intelligence output + Job Decomposition output
- **Output:**
```json
{
  "gaps": [{
    "capability_id": "power_bi",
    "type": "capability|evidence|credential|experience|workplace|potential_proxy|unknown_needs_review",
    "severity": "blocking|trainable|informational",
    "notes": "",
    "confidence": 0.0
  }],
  "barriers": [{
    "requirement_id": "r1",
    "counterfactual": "If replaced by a supervised SQL work sample, capability still fails? true|false|uncertain",
    "recommendation": "keep|replace_with_evidence|rephrase|human_review",
    "confidence": 0.0
  }],
  "summary": "",
  "confidence": 0.0
}
```
- **Tools:** Deterministic overlap of capability_ids vs required_ids (primary). LLM only for typing ambiguous rows and counterfactual prose.
- **Deterministic checks:** If required skill missing from candidate AND no transfer edge → type must not be `potential_proxy`. If only years/institution/gap/location → must not be typed `capability` without explanation.
- **Escalation:** Mixed/uncertain counterfactual
- **Human:** Always for `replace_with_evidence` on a live requisition
- **Hallucination:** Declaring barriers “illegal” — forbid legal conclusions
- **Dependencies:** 4.2, 4.3

### 4.5 Pathway Agent (Recomposition + Learning)

- **Responsibility:** Bounded plan to reach the bar. Or `no_viable_path`.
- **Input:** Diagnosis + policy `{ max_weeks, allow_proof, allow_work_mode_proposal }` + market hints
- **Output:** `LearningPath` (see `13_LEARNING_PATHWAY.md`) + `RecompositionPlan`
- **Tools:** Learning catalog mapper (SAP IDs if present); duration heuristics (deterministic table)
- **Reasoning:** LLM sequences items; **hours/weeks from table**, not from the model
- **Deterministic checks:** Every item maps to a gap capability_id; proof task exists for each blocking trainable gap; no item without `why_it_matters`
- **Escalation:** Path > policy max_weeks → `no_viable_path` or stretch-with-warning
- **Human:** HR accepts work-mode proposals; candidate accepts time commitment
- **Hallucination:** Fake SAP course IDs — catalog join required
- **Dependencies:** Diagnosis, learning catalog, market service optional

### 4.6 Inclusive Matching Scorer (deterministic)

- **Responsibility:** Rank opportunities with readiness states and constraints.
- **Input:** Capabilities, opportunities, constraints, diagnosis, pathway duration
- **Output:** `MatchRecommendation[]` with subscores and explanations *data* (not prose)
- **Tools:** None LLM. Formula in `14_INCLUSIVE_MATCHING.md`
- **Deterministic checks:** No protected-class features in the vector; constraint violations cannot be overridden by high skill score
- **Escalation:** Empty set
- **Human:** Selects among recommendations
- **Hallucination risk:** None if formula is the source of rank
- **Dependencies:** Opportunities store, diagnosis

### 4.7 Explainability Narrator (LLM, non-deciding)

- **Responsibility:** Turn structured artifacts into WHAT/WHY/EVIDENCE prose
- **Must not** add new facts. Groundedness check: every claim maps to an artifact id
- **Failure:** If ungrounded sentence detected (heuristic), show structured view only

### 4.8 Market Intelligence Service

- **Not a free-roaming agent in P0**
- Retrieval from `MarketSignal` table **[SYNTHETIC]** unless a licensed feed exists
- Optional LLM: 1-paragraph briefing that may only cite row ids
- See `12_MARKET_INTELLIGENCE.md`

### 4.9 Bias / fairness snapshot (governance service)

- **Input:** Current run + optional batch of N demo runs
- **Output:** Counts of knockout-by-requirement-class; concentration by *opportunity location field* (not by inferred demographics); flags if institution/gap length dominated rejects
- **LLM:** Narrative of the **numbers only**
- **Must not:** Estimate gender from names

### 4.10 Proof-of-Skill evaluator

- **P0:** Rubric service; LLM assist for open text with bounded rubric
- See `11_PROOF_OF_SKILL.md`
- Human can override

---

## 5. What actually needs an LLM vs not

| Task | LLM? | Why |
|---|---|---|
| PDF/resume interpretation | Yes | Unstructured |
| JD → tasks/classes | Yes | Unstructured |
| Skill ID normalization | LLM + allowlist | Hybrid |
| Overlap scoring | No | Reproducible |
| Confidence blend | No | Formula |
| Counterfactual typing | Yes + rules | Ambiguous language |
| Course sequencing | Yes | Light planning |
| Duration estimates | No | Table |
| Match rank | No | Safety |
| HR approval | No | Governance |
| Explanation prose | Yes | UX |
| Audit persist | No | |

---

## 6. Human-review matrix

| Artifact | Who | When |
|---|---|---|
| Inferred capabilities | Candidate / HR | Before using in a live decision (P1; P0 at review screen) |
| Requirement class edits | HR | Before matching if they want “reviewed JD” path |
| Barrier replace/keep | HR | Always for employment-affecting recs |
| Pathway time/cost | Candidate + HR | Before assigning learning |
| Proof score | HR / hiring manager | Before readiness → ready_now |
| Final recommendation | HR | Always. No auto-advance to hired |

---

## 7. Minimum viable “complete orchestrator”

Even with compressed agents, the **demo control room** still shows tiles named as the brief expects:

- Skills Discovery → Candidate Intelligence
- Market Intelligence → service
- Learning Pathways → Pathway Agent
- Inclusive Matching → scorer
- Bias Audit → snapshot service
- Employer Readiness → decomposition view
- Human-in-the-loop → governance

Naming in the UI may follow the brief. Implementation must follow this file.
