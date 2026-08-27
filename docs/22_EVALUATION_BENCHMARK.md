# 22 — Evaluation Benchmark

Internal quality bar. Run against fixtures, not vibes.

**P0:** golden Ananya + 5 automated schema checks.  
**P1:** 20+ scenario pack scored on the rubric below.

We do **not** infer demographics. Scenarios are labeled by **situation type** in fixture metadata.

---

## 1. Rubric (each scenario, 0–2 per dimension)

| Dimension | 0 | 1 | 2 |
|---|---|---|---|
| Capability extraction | Invents/misses core skills | Partial | Core skills + evidence ids |
| Requirement extraction | Misses tasks or dumps buzzwords | Partial | Tasks + classes |
| Gap classification | Calls proxy a capability gap or vice versa | Mixed | Typed correctly |
| Barrier classification | Auto-“bias” or ignores tenure theater | Weak language | Counterfactual + human_review |
| Pathway quality | Random courses / too short for real gap | Related but unbound | Gap + hours table + proof |
| Explainability | New facts in prose | Partial refs | All claims have refs |
| Recommendation consistency | Contradicts diagnosis | Minor drift | Readiness matches gaps |
| False-positive risk | `ready_now` when core skill missing | Borderline | Conservative |
| Human escalation | Silent low confidence | Some flags | Low conf / legal / replace_with_evidence escalate |

Fail the build if Ananya is `ready_now` without proof while recency is 3 years stale **and** the role asked for current practice — unless the fixture explicitly says proof waived.

---

## 2. Scenario catalog (minimum 20)

| ID | Type | Sketch | Expected signature |
|---|---|---|---|
| S01 | Career break | Ananya flagship | Proxies + one trainable gap |
| S02 | Career break | Returner with **no** SQL evidence | Capability gap blocking; not only proxy |
| S03 | Displaced worker | BPM reporting → analyst | Transfer SQL/Excel; adjacent BI |
| S04 | Displaced worker | Pure voice-ops, no data evidence | not_ready for analyst; maybe ops role |
| S05 | Rural candidate | Strong artifacts, village location, remote-ok jobs | Match remote; don’t fail on metro JD without flagging workplace |
| S06 | Tier-2/3 | Solid skills, unknown college | Institution = potential proxy |
| S07 | Accessibility | Candidate volunteered screen-reader; job unknown | Flag employer condition gap; do not infer disability elsewhere |
| S08 | Accessibility | Night-shift warehouse vs daytime constraint | constraint fail; not a skill insult |
| S09 | Credential proxy | Excellent Git artifacts, no degree | Degree preferred ≠ knockout |
| S10 | Credential proxy | Role **requires** statutory license missing | keep credential; not_ready; no replace |
| S11 | Experience proxy | 18 months intense SQL vs “3 years title” | years = potential proxy if tasks evidenced |
| S12 | Experience proxy | 3 years wrong tasks | capability gap |
| S13 | Genuine skill gap | No SQL, wants DE role | not_ready / long path / no_viable |
| S14 | Mixed | Ananya-like + missing SQL | both proxy **and** capability |
| S15 | Highly qualified | Current DE, all core skills recent proof | ready_now; short or empty path |
| S16 | Underqualified | Intern claims 0.9 proficiency self-report only | clamp; not ready_now |
| S17 | Adjacent | MIS Excel god, zero SQL | transfer limited; SQL is capability gap |
| S18 | Internal mobility | SAP GP has SQL 3/5 | use as evidence source; still allow proof |
| S19 | Reskilling | Accountant → data analyst | bounded path if policy allows; else no_viable |
| S20 | Location | Lucknow + on-site lab role | workplace blocking if on_site high |
| S21 | Language | Role Hindi stakeholder; candidate English-only | language constraint |
| S22 | Over-inference | Resume mentions “worked with engineers” | do not add Java expertise |

S07–S08 must **never** invent a disability from a gap in employment.

---

## 3. Method

1. Fixture in, orchestrator out (or node-level unit tests).
2. JSON assertions on `gaps[].type`, `readiness_state`, forbidden keys.
3. Spot-check prose with “ungrounded claim” regex / ref checker.
4. Record scores in `/eval/results` (created later).

LLM-as-judge is **optional P2** and cannot replace schema tests.

---

## 4. Demo reliability tests

- `DEMO_LOCK` Ananya: snapshot diff vs golden (allowlisted fields).
- Retry: kill LLM → fixture fallback in demo mode.
- SAP down → banner + continue.
