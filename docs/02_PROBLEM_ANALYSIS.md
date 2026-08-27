# 02 — Problem Analysis

**Rule:** No vague “AI will make hiring more inclusive.” Each failure mode is operational.

**Shared engine:** PERSON → CAPABILITY → EVIDENCE → TASK → ROLE → OPPORTUNITY

---

## How to read this document

For every failure mode:

- **Stakeholder** — who is harmed or blocked
- **Current workflow** — what happens today
- **Failure point** — where the workflow is wrong
- **Consequence**
- **Why existing tools may not solve it**
- **Where RE:WORK adds value**

“Existing tools” means typical ATS + SuccessFactors Recruiting / TIH / Learning / Opportunity Marketplace **as commonly configured**, not a claim that SAP can never address a topic with custom work.

---

## 1. Career-gap penalties

**Stakeholder:** Career returners (flagship: woman, 28, Lucknow, 3-year caregiving break); also health-break returners. HR filling “experienced but not senior” analyst roles.

**Current workflow:** Resume parsed → employment dates computed → gap flagged or recency filter applied → recruiter never sees the profile. Managers treat “recent relevant experience” as a proxy for skill decay.

**Failure point:** Time away is treated as negative capability evidence, even when skills were demonstrated immediately before the break and can be re-verified.

**Consequence:** Capable people exit the labor market; employers overpay for continuously employed profiles; returner programs remain side-projects disconnected from requisitions.

**Why existing tools may not solve it:** ATS recency filters are blunt. Skills platforms store last-rated proficiency but rarely *reason* that a gap is not a task failure. Opportunity Marketplace recommends from current attributes, not from “attributes + bounded re-proof.”

**RE:WORK:** Classify “employment recency” as an **experience / eligibility requirement**, run a counterfactual against current evidence, and offer proof-of-skill rather than silent discard.

---

## 2. Credential proxies

**Stakeholder:** Candidates from non-target institutions; bootcamp / MOOC learners; internal employees without the “right” certificate name. Recruiters using degree brand as a screen.

**Current workflow:** Requisition lists “B.Tech from premier institute preferred” → knockout question or rank boost → remaining pipeline looks homogeneous.

**Failure point:** Credential is used as a cheap signal of capability instead of as one optional evidence type.

**Consequence:** False negatives at scale; diversity of thought and geography collapses; hiring becomes a prestige auction.

**Why existing tools may not solve it:** Job Profile Builder and requisitions will faithfully store whatever HR typed. TIH can map certificates to skills **[VERIFIED API / product existence; live tenant NOT VERIFIED]** but will not challenge the *necessity* of the credential for the tasks.

**RE:WORK:** Requirement class `credential`. Ask: is this legally required, customer-contract required, or a proxy? If proxy, propose evidence replacement. Human reviews. Never auto-delete a license that is actually required (e.g., statutory).

---

## 3. Institution prestige bias

**Stakeholder:** Tier-2/3 talent; first-generation graduates. Campus teams that only visit a short list of colleges.

**Current workflow:** Source from preferred campuses → remaining applicants keyword-matched → prestige still used in tie-breaks.

**Failure point:** Institution is not a task. It is a network and signaling variable.

**Consequence:** India’s own tier-2 hiring narrative (present in the SAP brief) fails at the filter layer.

**Why existing tools may not solve it:** Recruiting marketing and campus modules optimize *where you already look*. They do not decompose whether the work needs that look.

**RE:WORK:** Treat institution as metadata, not a capability. Matching weights demonstrated evidence. Prestige may appear in a **review note** (“this was in the JD”) but not as a hidden score.

---

## 4. Geographic filtering

**Stakeholder:** Lucknow / non-metro candidates; caregivers who cannot relocate; employers who default to Bangalore/Hyderabad/NCR.

**Current workflow:** Location field = knockout. Hybrid/remote not modeled as a property of **tasks**.

**Failure point:** Workplace condition is conflated with capability. Some work is genuinely on-site (lab, plant, regulated floor). Some is not.

**Consequence:** Entire cities become invisible; returners with local constraints never enter the funnel.

**Why existing tools may not solve it:** Requisition location is a first-class filter because logistics are real. The missing piece is *task-level* on-site necessity and labeled flexibility.

**RE:WORK:** Classify `workplace_condition`. Counterfactual: if hybrid were allowed for these tasks, would capability still fail? Output is a recommendation for HR, not a silent location rewrite.

---

## 5. Rigid experience requirements

**Stakeholder:** Adjacent-skill candidates; internal mobility candidates whose titles do not match.

**Current workflow:** “3–5 years as Data Analyst” as knockout. Years-in-title ≠ years-on-task.

**Failure point:** Duration is used as a substitute for proficiency and evidence.

**Consequence:** People who have done the tasks under another title (“Business Analyst,” “MIS Executive,” “Operations analyst”) are removed.

**Why existing tools may not solve it:** Skills inference can add skills from a job profile, but requisition templates still encode years as hard fields. Matching engines typically score overlap, not *substitutability*.

**RE:WORK:** Split `experience_requirement` from `direct_capability_requirement`. If evidence shows task performance, years become a **reviewable proxy** with confidence, not an automatic fail.

---

## 6. Inaccessible work arrangements

**Stakeholder:** Persons with disabilities; caregivers; people needing schedule predictability. HR teams with policy but no requisition-level encoding.

**Current workflow:** Accessibility is a careers-page paragraph. Requisition does not capture screen-reader compatibility, shift rigidity, sensory environment, or equipment.

**Failure point:** Matching cannot respect constraints that were never structured.

**Consequence:** “Inclusive hiring” remains brand language. Candidates self-select out or fail late.

**Why existing tools may not solve it:** Some SAP accessibility and accommodation processes exist in HR admin. They are not typically bound to **task decomposition + matching constraints**. We have **not verified** a live accommodations API in our landscape **[NOT VERIFIED]**.

**RE:WORK:** Inclusive matching uses **compatibility constraints** (work mode, schedule, language, geography, stated accessibility needs if the candidate chooses to provide them). No inference of disability from text. Employer-readiness flags missing condition data for HR.

---

## 7. Failure to recognize transferable skills

**Stakeholder:** Career switchers; returners whose last title is stale; people with project/informal evidence.

**Current workflow:** Parser looks for literal skill strings. “SQL in a finance MIS role” does not transfer to “SQL for analytics.”

**Failure point:** Skills are tokens, not capabilities-in-context.

**Consequence:** Adjacent talent is treated as junior-from-zero.

**Why existing tools may not solve it:** TIH / skills graphs (SAP-side) are designed for this **in principle**. In practice, heterogeneous evidence (GitHub, Excel models, NGO ops, family-business accounts) never enters the graph. Inference from performance forms only exists if the person is already an employee with data.

**RE:WORK:** Candidate Intelligence extracts capabilities from heterogeneous evidence with `proficiency`, `confidence`, `recency`, `context`. Transfer edges are explicit and reviewable (“SQL in MIS → SQL for analytics, confidence 0.71, needs proof on window functions”).

---

## 8. Capability gaps vs eligibility proxies (not distinguished)

**Stakeholder:** Everyone in a “not a match” pipeline. Especially mixed cases (one real gap + several proxies).

**Current workflow:** Match score 42%. Recruiter does not know whether the 58% miss is “cannot do SQL” or “no degree from list.”

**Failure point:** A single distance metric collapses different kinds of mismatch.

**Consequence:** L&D assigns random courses; recruiters ghost; candidates internalize “I am unqualified” when they are *uncredentialed*.

**Why existing tools may not solve it:** Recommenders optimize similarity. They do not output a **typed diagnosis**.

**RE:WORK:** Diagnosis object with `gap_type`: `capability` | `evidence` | `credential` | `experience` | `workplace` | `potential_proxy` | `unknown_needs_review`.

---

## 9. “Not a match” without a close-the-gap path

**Stakeholder:** Candidates; internal employees rejected for mobility; L&D.

**Current workflow:** Rejection or silence. Sometimes a generic “upskill on our LMS.”

**Failure point:** Negative match is a dead end.

**Consequence:** Skills-gap cost (the brief’s enterprise story) continues because the people already in the funnel are not developed toward open roles.

**Why existing tools may not solve it:** Learning can recommend content from skills. It rarely generates a **role-bound, time-bound, proof-bound** path tied to a specific requisition the human is considering.

**RE:WORK:** `ready_with_bounded_pathway` is a first-class match state, with duration, proof, and a human checkpoint.

---

## 10. Reskilling disconnected from actual jobs

**Stakeholder:** Displaced workers; employers running academy programs; government/CSR skilling partners.

**Current workflow:** Course catalogs and “trending skills” lists. Completion certificates accumulate. Open requisitions still require “2 years commercial experience.”

**Failure point:** Learning success ≠ hiring success.

**Consequence:** Reskilling cynicism; wasted spend; displaced workers complete courses and remain unmatched.

**Why existing tools may not solve it:** LMS completion is a record, not a negotiation with Recruiting’s knockout fields.

**RE:WORK:** Pathway items exist only if they map to a decomposed capability on a real role. Proof-of-skill is the bridge Recruiting can accept *if HR agrees*.

---

## 11. Learning without proof of capability

**Stakeholder:** Hiring managers; candidates with many certificates and little trust.

**Current workflow:** Badge displayed. Manager still asks for years of experience.

**Failure point:** Consumption of content is treated as mastery.

**Consequence:** Certificate inflation; managers ignore L&D; candidates overestimate readiness.

**Why existing tools may not solve it:** Learning history APIs can show completion **[VERIFIED API existence for SuccessFactors Learning; our tenant NOT VERIFIED]**. They do not design role-valid work samples.

**RE:WORK:** Proof-of-skill engine: claim → task → submission → evaluation rubric → evidence object → updated capability confidence.

---

## 12. Job matching without readiness analysis

**Stakeholder:** Recruiters drowning in “good enough” scores; candidates receiving mismatched recs.

**Current workflow:** Rank by similarity. Send top 20. Interview reveals unreadiness.

**Failure point:** No `ready_now` vs `ready_with_proof` vs `not_ready`.

**Consequence:** Interview load, candidate drop-off, manager distrust of AI.

**Why existing tools may not solve it:** Intelligent recommendations exist in Opportunity Marketplace / Career Explorer **[VERIFIED as SAP product behavior in public docs; live access NOT VERIFIED]**. They are not the same as a readiness state machine bound to human review.

**RE:WORK:** Readiness is a structured enum with evidence and a pathway if not ready.

---

## 13. Opportunity without a development pathway

**Stakeholder:** Internal mobility candidates shown a stretch role with no plan.

**Current workflow:** “You might like this role.” No skills-to-tasks plan.

**Failure point:** Inspiration without scaffolding.

**Consequence:** People do not apply; managers do not take stretch bets.

**RE:WORK:** Recomposition always produces either “no path within policy bounds” or a path with cost/time/proof.

---

## 14. Workforce systems that do not explain WHY a person was excluded

**Stakeholder:** Candidates (fairness and dignity); HR (audit); legal; DEI.

**Current workflow:** Knockout or low score. Reason codes are coarse (“minimum qualifications”).

**Failure point:** No evidence chain.

**Consequence:** Cannot improve the requisition; cannot defend the process; cannot appeal.

**Why existing tools may not solve it:** Audit logs in enterprise HCM record *transactions*. They do not record *reasoning* over requirement classes.

**RE:WORK:** Every recommendation carries WHAT / WHY / EVIDENCE / CONFIDENCE / ALTERNATIVES. AuditEvent stores agent I/O. HumanDecision is mandatory for employment-affecting actions.

---

## 15. Systems that optimize for current fit instead of future potential

**Stakeholder:** Enterprises in skills shortage; employees whose next role is adjacent.

**Current workflow:** Fill with the closest current match. Stretch and develop only ad hoc.

**Failure point:** Potential is either ignored or used as a vague DEI slogan.

**Consequence:** Shortage persists beside a pile of “almost” candidates.

**RE:WORK:** Potential is operationalized as **bounded pathway + proof**, not as a personality judgment or identity flag.

---

## Cross-cutting failure: two disconnected products

If candidate tools and HR tools do not share the capability graph, inclusion dies in the handoff (“the career app said I was ready; the ATS said no”).

RE:WORK forbids that split. Candidate view and HR view are two projections of the same `Recommendation` object.

---

## What we will not claim as “problems we fully solve”

- Structural labor-market issues (childcare infrastructure, transport, statutory discrimination)
- Live, nationally representative labor-market statistics without a licensed data feed
- Perfect bias detection across demographics (we will not infer demographics)
- Replacing human hiring judgment

We solve **decision quality at the capability/requirement boundary**, with humans remaining accountable.
