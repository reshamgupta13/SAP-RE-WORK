# 14 — Inclusive Matching

Matching considers capability, transfer, readiness, learning gap, accessibility **compatibility**, workplace conditions, geography, language, and preferences.

**It does not** use protected characteristics as a ranking advantage.  
No “inclusion boost” for being a woman, a returner-as-identity, or a person with a disability.  
Returner **timeline facts** may explain recency; they are not a score bonus.

---

## 1. Readiness states

| State | Meaning |
|---|---|
| `ready_now` | Core capabilities at min proficiency with acceptable evidence/recency |
| `ready_with_proof` | Capabilities likely sufficient; evidence stale or transfer needs a work sample |
| `ready_with_bounded_pathway` | One or more trainable gaps; path within policy |
| `not_ready` | Blocking capability gaps beyond policy, or core on-site conditions incompatible and not waived |

`not_ready` is a valid, respectful outcome.

---

## 2. Feature vector (allowed)

Used for rank **within** the same readiness band, not to override constraints.

- Core skill coverage (deterministic overlap / weighted proficiency vs min)
- Supporting skill coverage
- Evidence quality (proof > artifact > history)
- Pathway remaining weeks (lower is better for pathway band)
- Preference fit: work mode, location feasibility, language **as declared**

**Hard constraints (fail closed):**

- Candidate `work_modes` ∩ opportunity `work_modes` empty → cannot be `ready_now` / `ready_with_proof` unless HR waived
- Required language not in candidate languages → not matched
- Accessibility: only if candidate **stated** needs and opportunity **stated** conditions; unknown ≠ fail; unknown = flag “insufficient job condition data”

**Forbidden features:**

- Name, photo, gender, age, caste, religion, disability inference
- Institution prestige score
- Gap length as a negative number in the ranker
- “Diversity” sliders

Gap length and institution may appear in **explainability** as requirement clauses, not as rank inputs.

---

## 3. Scoring (deterministic)

```
coverage = sum(w_i * min(1, prof_i / min_i)) / sum(w_i)   # core skills
constraint_ok = 0 or 1
if constraint_ok == 0: eligible = false

rank_key = (readiness_band, coverage, -pathway_weeks)
```

LLM does not produce `coverage`. LLM explains the already computed breakdown.

Preferred JD items (`strength=preferred`) contribute to a **secondary** score only, never knockout.

---

## 4. Inclusive constraints (the actual inclusion mechanism)

| Constraint | Inclusive behavior |
|---|---|
| Accessibility | Match stated needs to stated workplace conditions; surface HR gaps |
| Flexible work | If tasks on_site_likelihood=low, show hybrid/remote opportunities and flag office-only JDs for review |
| Schedule | If opportunity has night shifts and candidate excluded nights, fail closed |
| Language | Role language vs declared skills |
| Geography | Distance/relocate willingness; Lucknow + hybrid is feasible; Lucknow + 5-day Bangalore is constraint fail unless waiver |
| Accommodations readiness | Employer-readiness checklist, not a candidate penalty |

---

## 5. Outputs

Each `MatchRecommendation`:

- opportunity_id
- readiness_state
- coverage
- top 3 contributing capabilities (ids)
- top 3 missing capabilities (ids)
- constraint failures (ids)
- barrier_ids still in force
- pathway_id if any
- explanation refs

HR may **modify**: waive a workplace condition (recorded), or reject.

---

## 6. Anti-gaming

Do not let candidates self-report 1.0 proficiency to win coverage. Clamps from the capability model apply before matching.
