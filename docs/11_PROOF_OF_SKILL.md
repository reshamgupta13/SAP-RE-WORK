# 11 — Proof of Skill

A candidate must not be judged only by resume text.

```
CLAIM -> TASK -> SUBMISSION -> EVALUATION -> EVIDENCE -> UPDATED CAPABILITY
```

Proof is how RE:WORK keeps the **performance standard** while rejecting **paper proxies**.

---

## 1. When to use

| Situation | Proof? |
|---|---|
| High proficiency, high confidence, recent artifact | Optional |
| High proficiency, stale recency (career break) | **Recommended** |
| Transferable skill, new context | **Recommended** |
| Blocking trainable gap after learning | **Required** to move to `ready_now` |
| Statutory license | Proof-of-skill is **not** a substitute |

---

## 2. Task design rules

- Mapped to **one or few** `skill_id`s from the decomposed job
- Looks like the work (SQL, dashboard, memo, case) — not IQ puzzles, not gameified speed tests
- Time-boxed (e.g. 60–120 minutes) to respect caregivers
- No biometric, personality, or disability “detection”
- No culturally loaded trivia
- Instructions in the language of the role
- Rubric published **before** submission (transparency)

### Allowed examples (role-relevant)

- SQL: given a small schema + questions, write queries
- Dashboard: given a CSV, produce 3 charts + 5-sentence insight
- Code: small, job-like function with tests
- Writing: stakeholder email explaining a metric movement
- Business case: 1-page recommendation from a short brief

### Forbidden

- Brainteasers unrelated to tasks
- “Culture fit” scoring
- English-accent scoring
- Photo/video required unless the role truly needs on-camera work and HR has approved
- Medical or psychiatric items

---

## 3. Evaluation

**Primary:** deterministic rubric (points).  
**Assist:** LLM may suggest scores for open-ended writing **against the rubric only**, never a vibe score.

```json
{
  "assessment_id": "uuid",
  "claim": {"skill_id": "sql", "claimed_proficiency": 0.62},
  "task_id": "sql_ops_mini",
  "rubric": [
    {"id": "joins", "weight": 0.4, "max": 4},
    {"id": "filters", "weight": 0.3, "max": 4},
    {"id": "readability", "weight": 0.3, "max": 4}
  ],
  "submission": {"provenance": "USER-PROVIDED"},
  "scores": [{"id": "joins", "score": 3, "note": "correct inner join; missed left join edge"}],
  "total": 0.0,
  "result": "pass|borderline|fail",
  "evaluator": "rubric|llm_assist+human|human",
  "human_override": null
}
```

Pass thresholds: stored per task, not invented per candidate.

---

## 4. Effect on the graph

On pass:

- New evidence `type=proof_of_skill`, date=now, high reliability
- Proficiency may increase **within clamp rules** (see capability model)
- Recency updates
- Match may recompute

On fail:

- Do not delete prior evidence
- Pathway may add a targeted practice item
- Readiness stays `ready_with_bounded_pathway` or `not_ready`

---

## 5. Fairness and audit

- Same task version for the same role version (no harder test for returners)
- Store task version hash, rubric version, evaluator identity
- Candidate sees scores and notes
- Appeal: request human regrade (P1)

---

## 6. Prototype scope

**P0:** One SQL task + one dashboard insight task, seeded for Ananya; UI can show a **completed** evaluation in demo lock.  
**P1:** Live submit box with rubric auto-score for SQL (unit-test style).  
**P2:** LMS-triggered proof after course completion.

SAP: if Learning is live, completion ≠ proof. Proof is RE:WORK (or a SuccessFactors assessment object **only if** we verify that API — **[NOT VERIFIED]**).
