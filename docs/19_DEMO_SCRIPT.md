# 19 — Demo Script (3–5 minutes)

**Audience:** SAP architects, HR, AI engineers, RAI reviewers, hackathon judges.  
**Mode:** `DEMO_LOCK=true`, temperature 0, Ananya fixtures.  
**Wow moment:** Traditional “does not meet requirements” vs typed diagnosis + pathway + human decision.

Spoken rule: say **simulated SAP context** unless a live GET is actually on screen.

---

## Minute 0:00–0:20 — Frame

> Traditional systems ask: does she currently match this job?  
> RE:WORK asks: what can she do, what does the work require, what is a real gap, what may be a proxy, and what evidence would meet the **same** performance bar?

Show product name. No chatbot full-screen.

---

## 0:20–0:40 — Load candidate + SAP context

**UI:** Candidate view / Control Room “Load Ananya.”

- Timeline: employment → **caregiving break 3 years** → now
- SAP panel: Growth Portfolio snapshot **badge: SIMULATED** (or LIVE if true)
- Skills from evidence, not from gap length

**State:** `load_context` done.

---

## 0:40–1:10 — Load target role

Noisy requisition: Junior Data Analyst, Bangalore 5 days, 3 years continuous, premier institute preferred, SQL + dashboards.

**Job Decomposition** runs (visible node).

Point at classified requirements: capability vs experience vs credential vs workplace.

---

## 1:10–1:50 — Discover + Diagnose (wow)

**Candidate Intelligence** capability graph: SQL, stakeholder comms, Excel, requirements — evidenced. Power BI low.

**Diagnosis:**

> Traditional system: candidate does not meet requirements.  
> RE:WORK: strong demonstrated capability. The mismatch is primarily a **career-history proxy** and a **location condition**, plus **one trainable capability gap** (dashboarding).

Open **Barrier** rows: continuous years → counterfactual `would_likely_be_able` if SQL proof; institute → not a task; Bangalore → HR policy / task on-site low.

This is the wow. Pause.

---

## 1:50–2:20 — Market + Recomposition + Pathway

**Market:** In the **demo corpus**, Power BI unlocks N analyst openings (footnote synthetic).

**Pathway:** 4 weeks, Power BI item, practical exercise, **proof** attached. Hours from table.

If Learning Hub titles verified, name them. Else say synthetic catalog mapped to the gap.

---

## 2:20–2:40 — Proof + readiness

Show proof task (SQL mini) **pass** (seeded or live). Capability recency updates. Readiness: still pathway until BI proof, or `ready_with_proof` if script uses only SQL currency — **pick one story and stick to it.**

**Recommended demo lock story:** SQL proof passed (currency after break); BI still pathway → `ready_with_bounded_pathway`.

---

## 2:40–3:20 — Match + explainability + HR

Inclusive matching: 2 hybrid/Lucknow-feasible roles `ready_with_bounded_pathway`; senior DE `not_ready` (honest).

**Explainability:** WHAT / WHY / EVIDENCE / CONFIDENCE / ALTERNATIVES.

**HR view:** Approve pathway match; **do not** auto-rewrite Bangalore policy — HR clicks `modify` or `approve with location waiver` explicitly.

**Decision recorded.** Audit event visible.

---

## 3:20–3:45 — Governance / bias snapshot

Show: in this run, knockouts would have been *experience + location + credential*, not missing SQL. Batch tile optional.

Human remains in the loop. No hire.

---

## 3:45–4:30 — Buffer / Q&A bait

One line on adapter: “Live SuccessFactors is a destination swap.”  
One line on RAI: “We do not rank on identity.”

---

## State transition checklist (exact)

1. created  
2. sap_context loaded (labeled)  
3. discover → capability_assessment  
4. decompose → job_profile  
5. diagnose → gaps + barriers  
6. market_signals attached  
7. pathway generated  
8. proof_result applied (SQL)  
9. match recommendations  
10. explainability  
11. human_decision approve/modify  
12. run completed  

If LLM flakes: Control Room “Replay golden Ananya” loads `golden/ananya_run.json` — still show it as DEMO fixture, not magic.

---

## Timing if only 3 minutes

Cut market details and bias batch. **Never cut** wow diagnosis, pathway, HR decision.
