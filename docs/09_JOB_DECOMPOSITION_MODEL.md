# 09 — Job Decomposition Model

The Job Agent transforms a **job description / requisition** into a structured role model.

```
ROLE
  -> OUTCOMES
  -> RESPONSIBILITIES
  -> TASKS
  -> CAPABILITIES
  -> EVIDENCE EXPECTATIONS
  -> CONDITIONS / CONSTRAINTS
  -> EXPERIENCE / CREDENTIAL REQUIREMENTS
```

Unstructured JD is allowed. Confidence must drop. Structured SAP Job Profile (when present) raises confidence.

---

## 1. Requirement classes

Every extracted clause gets exactly one class:

| Code | Meaning |
|---|---|
| `A_direct_capability` | Needed to perform tasks (e.g. write SQL for weekly ops reports) |
| `B_evidence` | How capability should be shown (portfolio, assessment, references) |
| `C_credential` | Degree, certificate, license |
| `D_experience` | Years, titles, “continuous employment,” industry years |
| `E_workplace_condition` | Location, hours, travel, on-site, shift, equipment, language of workplace |
| `F_potential_proxy_or_barrier` | **Tag**, not a class. Applied *in addition* when A–E may be standing in for something else |
| `G_unknown_needs_review` | Parser cannot classify; human required |

Implementation: store `class` in `{A,B,C,D,E,G}` and optional `review_tag` in `{none, potential_exclusionary_factor, potential_proxy, requires_review}`.

**Never** auto-label `biased`.

---

## 2. Output schema

```json
{
  "role": {
    "title": "Junior Data Analyst",
    "level": "junior",
    "family": "analytics",
    "sap_job_role_code": null,
    "sap_requisition_id": null
  },
  "outcomes": [
    {"id": "o1", "text": "Weekly operational insights for city ops leadership"}
  ],
  "responsibilities": [
    {"id": "p1", "text": "Build and maintain recurring reports"}
  ],
  "tasks": [
    {
      "id": "t1",
      "text": "Write SQL to extract and join operational tables",
      "outcome_ids": ["o1"],
      "capability_ids": ["sql"],
      "on_site_likelihood": "low"
    }
  ],
  "capabilities_required": [
    {
      "skill_id": "sql",
      "min_proficiency": 0.6,
      "importance": "core",
      "evidence_expectation": "work sample or equivalent project"
    }
  ],
  "evidence_expectations": [
    {"capability_id": "sql", "acceptable": ["proof_of_skill", "artifact", "supervised_probation"]}
  ],
  "workplace_conditions": [
    {
      "id": "w1",
      "text": "Bangalore office 5 days/week",
      "class": "E_workplace_condition",
      "review_tag": "potential_proxy",
      "task_justification": "unknown"
    }
  ],
  "requirements": [
    {
      "id": "r1",
      "text": "3 years continuous professional experience",
      "class": "D_experience",
      "review_tag": "potential_proxy",
      "why_may_be_relevant": "May proxy for practice volume and reliability.",
      "why_may_be_proxy": "Continuous tenure is not a task; breaks do not erase SQL.",
      "linked_task_ids": [],
      "confidence": 0.7
    },
    {
      "id": "r2",
      "text": "Premier engineering institute preferred",
      "class": "C_credential",
      "review_tag": "potential_exclusionary_factor",
      "why_may_be_relevant": "May proxy for screening volume.",
      "why_may_be_proxy": "Institute brand is not a capability.",
      "confidence": 0.8
    }
  ],
  "confidence": 0.66,
  "provenance": "SYNTHETIC"
}
```

---

## 3. Extraction rules

1. Prefer quoting original clause text (traceability).
2. Skills not in the JD may be added **only** as `inferred_from_tasks` with lower confidence (e.g. “produce dashboards” → visualization skill).
3. Statutory licenses (if ever present) → `C_credential` + `review_tag=requires_review` + **do not** suggest removal.
4. “Preferred” vs “required”: store `strength: required|preferred|unstated`. Preferred must not become knockout in matching.

---

## 4. Employer-readiness view (brief’s Employer Readiness Agent)

This is a **projection** of the same object:

- Count of `potential_proxy` / `potential_exclusionary_factor`
- Missing workplace accessibility fields
- Language that screens for recency, pedigree, unpaid overtime, “cultural fit,” age-coded phrases

HR actions: `keep` | `rephrase` | `replace_with_evidence` | `drop_preferred`.  
Actions write a new `requirement_analysis` version; they do not silently mutate SAP.

---

## 5. Quality bar

A decomposition is **demo-ready** if a hiring manager can say: “Those are the actual tasks,” and a returner can see which bullets were tenure theater.

A decomposition is **failed** if it only lists buzzwords without tasks, or if it marks every requirement as a proxy.
