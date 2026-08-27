# 08 — Capability Model

**Central abstraction:** not resume ↔ job description.

```
PERSON -> CAPABILITY -> EVIDENCE -> TASK -> ROLE -> OPPORTUNITY
```

A skill is never a boolean.

---

## 1. Objects

### Person

Identity in RE:WORK: `candidate_id`. May map to SAP `userId` / `personIdExternal` when live. Holds preferences and volunteered constraints only.

### Capability (instance)

A **person’s** instantiation of a catalog skill (or a task-bound ability).

| Field | Meaning |
|---|---|
| `skill_id` | Catalog key, e.g. `sql` |
| `label` | Display |
| `kind` | `explicit` \| `inferred` \| `transferable` \| `adjacent` |
| `proficiency` | 0–1 (see scale) |
| `confidence` | 0–1 belief in this instance |
| `recency` | Date of strongest evidence |
| `context` | Domain/environment (e.g. “finance MIS, Lucknow shared services”) |
| `evidence_ids` | Required for explicit/inferred |
| `sap_attribute_id` | Optional TIH alignment |
| `task_ids_supported` | Optional links once matched to a job |
| `business_outcome_relevance` | Optional 0–1 vs current target role |

### Evidence

| Field | Meaning |
|---|---|
| `id` | |
| `type` | `work_history` \| `artifact` \| `self_report` \| `sap_rating` \| `learning_completion` \| `proof_of_skill` \| `manager_attestation` |
| `summary` | |
| `source_ref` | Quote, URL, SAP object, file id |
| `date` | |
| `provenance` | LIVE / SIMULATED / SYNTHETIC / MOCKED / USER-PROVIDED |
| `reliability` | Heuristic: proof > sap_rating > artifact > work_history > self_report |
| `confidence` | |

Self-report alone cannot produce `proficiency >= 0.7`.

### Catalog Skill

Canonical node: `skill_id`, description, aliases, optional `sap_attribute_id`, `status=active`.

### Task (from job)

`task_id`, text, `required_skill_ids[]`, `importance` (`core|supporting`), `on_site_likelihood` (`unknown|low|high`).

### Role

Container of tasks + outcomes + requirement clauses. Maps to SAP job role / requisition.

### Opportunity

A fillable opening: internal OMM, requisition, or synthetic demo job. Points at a Role.

---

## 2. Proficiency scale (deterministic interpretation)

Use a 0–1 scale with labels for UI:

| Score | Label | Operational meaning |
|---|---|---|
| 0.0–0.19 | Awareness | Heard of it; cannot perform |
| 0.20–0.39 | Assisted | Can perform with close supervision |
| 0.40–0.59 | Working | Can perform standard tasks with review |
| 0.60–0.79 | Independent | Can own typical role tasks |
| 0.80–1.00 | Advanced | Can handle messy/edge cases or guide others |

LLM may propose a score; **clamp** using evidence rules:

- Only self-report → max 0.45
- Work history mention without artifact → max 0.60
- Artifact or SAP rating → up to 0.80
- Proof-of-skill pass against role rubric → up to 0.90
- Never 1.00 from a single resume line

---

## 3. Confidence (separate from proficiency)

Proficiency = how well. Confidence = how sure we are we know.

Low confidence + high proficiency is a **review flag**, not a hidden average.

---

## 4. Kinds of skills

| Kind | Rule |
|---|---|
| explicit | Named in evidence (“SQL”) |
| inferred | Strongly implied (wrote complex Excel data models → data wrangling, lower confidence) |
| transferable | Same skill, new context (SQL in MIS → SQL in analytics) |
| adjacent | Nearby skill not evidenced (SQL → Power BI is adjacent, not claimed as possessed) |

Adjacent skills are **pathway fuel**, never silently added as possessed capabilities.

---

## 5. Example: SQL is not true/false

```json
{
  "skill_id": "sql",
  "label": "SQL",
  "kind": "explicit",
  "proficiency": 0.62,
  "confidence": 0.74,
  "recency": "2023-03",
  "context": "MIS / business analysis, shared services, India",
  "evidence_ids": ["ev_mis_reporting", "ev_resume_sql"],
  "sap_attribute_id": null,
  "task_ids_supported": ["t_extract_clean", "t_adhoc_queries"],
  "business_outcome_relevance": 0.85
}
```

Career break does **not** decrement proficiency automatically. Recency is shown; Diagnosis may request proof if the role demands current practice.

---

## 6. Graph shape (without Neo4j)

Relational:

- `skills` (catalog)
- `skill_edges` (`from_id`, `to_id`, `rel=adjacent|parent|alias`, `weight`)
- `candidate_skills` (capability instances)
- `evidence`
- `candidate_skill_evidence`
- `job_tasks`
- `job_task_skills`

Queries: required skills for a role; candidate overlap; adjacent for pathway. pgvector optional on `skills.embedding` for alias matching, not for final rank.

---

## 7. Transfer rules (conservative)

A transfer edge may raise **confidence in a target context** only if:

- source proficiency ≥ 0.5
- evidence context is documented
- target is tagged `transferable` not `explicit` until proof

Example: Excel pivot tables ↛ “statistical modeling.”

---

## 8. What is stored vs computed

| Stored | Computed at match time |
|---|---|
| instances, evidence, recency | task relevance vs current job |
| catalog edges | readiness state |
| proof results | pathway remaining duration |

Do not persist “match %” as a capability field.

---

## 9. Anti-patterns

- One embedding for the whole resume as the capability model
- Dropping evidence when summarizing
- Encoding institution or city as a skill
- Encoding “returner” as a capability (it is a timeline fact)
