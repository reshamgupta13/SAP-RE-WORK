# MASTER BUILD PLAN

**Status:** Awaiting explicit approval before any application code.  
**Date:** 2026-08-28  
**Constraint:** North Region finale **3 September 2026**. Build window is days, not weeks.  
**Repo today:** empty, no git, no SAP tenant **[NOT VERIFIED]**.

This plan is the only implementation order. If a feature is not P0, it does not start until P0 is demoable.

---

## 1. Final product architecture

**RE:WORK** is a LangGraph-orchestrated reasoning extension beside SAP SuccessFactors.

```
UI (Next.js) → FastAPI → Orchestrator state machine
                              ├ discover (LLM)
                              ├ decompose (LLM)
                              ├ diagnose (LLM + rules)
                              ├ pathway (LLM + hour tables)
                              ├ match (deterministic)
                              ├ explain (LLM, grounded)
                              ├ bias snapshot (rules + narrative)
                              └ human decision (deterministic)

SAP Adapter: SimulatedSuccessFactorsAdapter | LiveODataAdapter
DB: PostgreSQL (+ pgvector optional)
LLM: Gemini or permitted model (GenAI Hub if entitled)
```

**One product, two seats** (candidate + HR) on one `run_id`.  
**Principle:** Do not lower the bar. Challenge proxies. Prove capability. Humans decide.

---

## 2. P0 — MUST WORK (demo-critical)

End-to-end **Ananya / Lucknow returner** loop:

1. SAP / workforce context panel (simulated, labeled) + user-provided resume
2. Candidate Intelligence (real LLM agent)
3. Job Decomposition (real LLM agent)
4. Capability gap + barrier/counterfactual (Diagnosis)
5. Job recomposition + learning pathway (bound to gaps + proof stub)
6. Inclusive matching (deterministic readiness)
7. Explainability panel (WHAT/WHY/EVIDENCE/CONFIDENCE/ALTERNATIVES)
8. Human review approve/modify/reject persisted
9. Control Room showing orchestrator tiles mapped to the brief (Skills Discovery, Market, Learning, Matching, Bias audit)
10. `DEMO_LOCK` golden replay if LLM fails
11. Provenance badges everywhere
12. Synthetic market **corpus** panel (honest footnote) — keep thin but present so the orchestrator is “complete”

**P0 explicitly excludes:** live SAP writes, Neo4j, auth, file ingest if paste works, Joule, demographic fairness dashboards, 10 LLM agents, web scraping.

---

## 3. P1 — HIGH VALUE

- Live **read-only** OData GET if tenant/practice system appears (one requisition or one user)
- Real SAP Learning Hub course titles in the pathway
- PDF/DOCX resume upload
- Live SQL proof grader (unit-test style)
- Candidate confirmation of inferred skills
- Employer-readiness edits that re-enter diagnose
- Eval pack S01–S10 automated
- Deployed URL

---

## 4. P2 — POLISH

- Motion, refined graph viz, print-ready explainability
- Appeal flow
- BTP deploy / Destination screenshot in landscape we own
- OpenTelemetry
- Extra personas in UI switcher (fixtures already designed)

---

## 5. P3 — ONLY IF TIME

- GenAI Hub provider
- Integration Center CSV ingest
- A2A / Joule mention as future
- Mentorship marketplace
- Wage data

---

## 6. Implementation order (after approval)

| Step | Deliverable | Depends on |
|---|---|---|
| 0 | Git init, monorepo, env template, DEMO_MODE flag | Approval |
| 1 | JSON schemas + Postgres tables + seed Ananya fixtures | 0 |
| 2 | SAP adapter interface + simulated payloads (documented entity names) | 1 |
| 3 | LangGraph state + audit_events + interrupt before decision | 1 |
| 4 | Skill catalog + matching formula + pathway hour table (no LLM) | 1 |
| 5 | Candidate Intelligence node | 3, catalog |
| 6 | Job Decomposition node | 3, catalog |
| 7 | Diagnosis node (rules first, LLM second) | 5, 6 |
| 8 | Pathway node | 7, learning catalog |
| 9 | Match + market queries on synthetic table | 4, 7, 8 |
| 10 | Explainability + bias snapshot | 9 |
| 11 | Human decision API | 3 |
| 12 | Control Room + HR + Candidate + SAP + Explain UI | 11 |
| 13 | Golden replay + Ananya eval assertions | 12 |
| 14 | Demo rehearsal against script `19` | 13 |
| 15 | P1 only if 14 is stable | — |

Do **not** start step 12 before 5–9 return real JSON. UI last among P0, but it must still look finished — allocate parallel UI **shell** (layout, badges, empty states) from step 3 using mock JSON **typed from schemas**, then bind.

---

## 7. Dependencies

- LLM API key (Gemini or other **permitted** model) — **blocked until provided**
- SAP tenant / Learning Hub practice system — **blocked for LIVE**; not blocked for SIMULATED P0
- Team 4–5 people (hackathon rule)
- Python packages on 3.13 (fallback 3.12 venv)

---

## 8. Team work split (4–5)

Assume 5; collapse D+E if 4.

| Person | Owns | P0 focus |
|---|---|---|
| **A — Orchestration / API** | FastAPI, LangGraph, audit, DEMO_LOCK | Steps 0–4, 11 |
| **B — Agents / eval** | Prompts, schemas, diagnosis rules, golden tests | Steps 5–10, 13 |
| **C — HR + Explain + Candidate UI** | shadcn surfaces A, B, E | Step 12 bind |
| **D — SAP adapter + fixtures + Control Room + SAP view** | Simulated payloads, provenance, market seed | Steps 1–2, 12 D/C |
| **E — Demo producer** | Script timing, visual polish, fallback drill, pitch alignment | 14, P2 polish |

If 4 people: C takes E polish; D takes Control Room.

---

## 9. Estimated difficulty

| Workstream | Difficulty | Risk |
|---|---|---|
| Adapter + fixtures | M | Overclaiming SAP |
| Diagnosis rules | H | Heart of wow |
| LLM extraction | M | Hallucinations |
| Deterministic match | M | Must stay boring |
| UI polish | M | Time |
| Live SAP | H | May never arrive |

---

## 10. Demo-critical components

- Ananya fixtures
- Wow diagnosis card
- Barrier counterfactual rows
- Pathway with proof
- HR decision bar
- Provenance + simulated SAP panel
- Golden replay

---

## 11. SAP-critical components

- Adapter contract
- Simulated SuccessFactors-shaped JSON
- Honest labeling
- Architecture story (BTP destination)
- **Stretch:** one live GET

Without live SAP, P0 is still viable **if** judges accept a rigorous extension story. A logo is not enough; the adapter and entity fidelity are the mitigation.

---

## 12. Biggest technical risks

1. No tenant → overclaim  
2. LLM nondeterminism on stage  
3. Scope creep (10 agents, Neo4j, scrapers)  
4. Discriminatory ranking by accident  
5. Python 3.13 package breaks  
6. UI started too late  
7. Invented TIH API  

---

## 13. Fallback if SAP APIs are unavailable

**Default P0 path.** Simulated adapter + official entity names + Integration Center sample file in fixtures + Learning Hub titles if the team pastes them + spoken production path.

**Escalate:** faculty/SAP mentor for practice-system credentials on day 1 of implementation.

**Do not:** fake network calls to `api.successfactors.com` and call it live.

---

## 14. Observability (P0)

`audit_events` rows per node: agent, input hash, output, confidence, evidence refs, latency, error, fallback, human override on decision.

---

## 15. Data provenance convention (product-wide)

Every external-ish field: `LIVE | SIMULATED | SYNTHETIC | MOCKED | USER-PROVIDED`.  
UI never presents synthetic market numbers as national facts.

---

## 16. Approval gate

No application scaffolding until you explicitly approve this MASTER BUILD PLAN.

**Ask of you next:** see the closing response — credentials, LLM key, Learning Hub access, team split, and whether `acdyon-pathway-engine` is related.
