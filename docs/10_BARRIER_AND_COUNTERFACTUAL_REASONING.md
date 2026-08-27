# 10 — Barrier and Counterfactual Reasoning

**This is a primary differentiator.**  
**This is also a high-harm surface.** Conservative language. No legal conclusions. No automatic requirement deletion.

---

## 1. The question

> If this requirement were removed **or replaced with direct evidence of the underlying capability**, would the candidate still be unable to perform the work?

Answers: `still_unable` | `would_likely_be_able` | `uncertain`

---

## 2. What we compare (examples)

| Stated requirement | Possible underlying capability | Counterfactual test |
|---|---|---|
| 3 years continuous experience | Practice volume, reliability, currentness | Supervised work sample + reference or probation |
| Top-tier institution | Trainability, baseline academics | Direct skill evidence |
| Physical office 5 days | Collaboration, data access, equipment | Hybrid if tasks are digital and access is solvable |
| Recent employment | Skill currency | Dated proof-of-skill |
| “Native” language / accent | Communication with stakeholders | Language fit test **if volunteered** / role-true language requirement |
| Specific prior title | Task overlap | Task-level evidence from adjacent title |

---

## 3. Output object (per requirement)

```json
{
  "requirement_id": "r1",
  "requirement_text": "3 years continuous professional experience",
  "why_it_may_be_relevant": "May stand in for enough repetitions of messy data work and workplace reliability.",
  "why_it_may_be_a_proxy": "A caregiving break is not evidence of inability to write SQL or interview stakeholders.",
  "evidence_needed_to_replace": ["sql_work_sample", "stakeholder_case_writeup"],
  "counterfactual": "would_likely_be_able",
  "confidence": 0.64,
  "recommendation": "replace_with_evidence",
  "human_review_required": true,
  "legal_or_statutory_risk": "unknown",
  "notes_for_hr": "Do not drop if used as a proxy for background-check tenure policies — confirm with HR policy."
}
```

`recommendation` enum: `keep` | `replace_with_evidence` | `rephrase` | `human_review`  
Never `delete_because_biased`.

---

## 4. Deterministic guards (run before/after LLM)

1. If requirement class is `A_direct_capability` and candidate lacks skill with no transfer → counterfactual cannot be `would_likely_be_able`.
2. If requirement is clearly location/title/years/institution/gap and tasks are digital analysis → LLM may propose proxy tag; **human_review_required=true** always.
3. If text includes license, visa, citizenship, security clearance → `recommendation=human_review`, `legal_or_statutory_risk=possible`, **no replace suggestion**.
4. If on_site_likelihood for core tasks is `high` → do not recommend remote as equivalent.
5. Forbidden outputs: protected-class inferences; “this JD is illegal”; “you should hire her because she is a woman.”

---

## 5. Language policy

| Use | Do not use |
|---|---|
| potential exclusionary factor | biased, discriminatory (as a system verdict) |
| potential proxy | ageist, sexist, casteist (as auto-labels) |
| requires review | must remove |
| evidence-based alternative | ignore qualifications |

---

## 6. Aggregation (Bias Audit snapshot)

Do **not** infer demographics. Aggregate over **requirement classes** and **recommendations**:

- How often did `D_experience` / gap-length clauses drive `not_ready` vs capability gaps?
- How often did institution clauses appear as knockouts?
- Location hard-filters vs task on-site likelihood mismatch rate

Flag for human review if, in a batch, **eligibility proxies dominate** capability gaps. That is a **process** flag, not a people score.

---

## 7. Wow-moment logic (flagship)

Traditional: fail on continuous experience + metro location + institute.

RE:WORK:

- SQL and BA capabilities evidenced → bar for core tasks largely met
- Continuous years → `would_likely_be_able` if proof replaces tenure
- Bangalore 5-day → workplace condition; tasks `on_site_likelihood=low`; **HR policy decision**
- Institute preferred → not a capability
- Power BI → genuine `trainable` capability gap

The story is **typed diagnosis**, not a higher match percentage.
