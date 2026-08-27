# 01 — Product Vision

**Product:** RE:WORK — AI-Powered Inclusive Workforce Recomposition Engine  
**Users:** Candidate / employee **and** employer / HR, joined by one capability intelligence layer  
**Principle:** Do not lower the performance standard. Remove unnecessary barriers to reaching it.

---

## A. Problem

Enterprise hiring and internal mobility systems are optimized for **current documented fit**.

They ask: *Does this profile currently match this requisition?*

That question systematically fails people who can do the work, or could do it after a bounded, evidence-based pathway, because the system confuses:

- **capability** (can this person perform the tasks?)
- **eligibility theater** (degree brand, unbroken tenure, city, keyword overlap)
- **missing paperwork** (no recent title, no branded certificate)
- **trainable gaps** (one adjacent skill, not a different occupation)

The result is not “strict standards.” It is **noisy standards**: high performers with non-linear careers are discarded, while keyword-matched profiles pass. Organizations then spend more on hiring, remain understaffed, and still do not know *why* someone was excluded.

RE:WORK exists to re-ask the question:

> What can this person actually do, what does the role actually require, what is genuinely missing, which barriers may be unnecessary, and what evidence-based pathway could help this person become successful in the role?

---

## B. Target users

One product. Two seats. Same objects.

### Candidate / employee

- Career returners after caregiving or health breaks
- Displaced workers (including IT/BPM role shrinkage)
- Rural / tier-2 / tier-3 talent
- Persons with disabilities seeking compatible work design
- Non-traditional candidates (bootcamps, projects, military, family business, informal sector)
- Internal employees seeking mobility or reskilling

They need: a truthful picture of capability, a target role that is real, a gap that is specific, a pathway that is finite, and a way to **prove** the missing piece.

### Employer / HR / recruiter / talent development

- Recruiters filling requisitions
- HRBPs and hiring managers
- L&D / talent development
- DEI / people-sustainability leads (as reviewers, not as a scoring engine)
- Internal mobility / opportunity marketplace operators

They need: requirement hygiene, barrier review, ranked **defensible** matches, learning that maps to a job, and an approval trail they can stand behind in audit.

### Not a user

- The model. The model proposes. Humans decide.

---

## C. Primary user journeys

### Journey 1 — Returner to a target role (flagship)

1. Candidate (or HR on their behalf) loads a profile + evidence pack.
2. Optional: pull SAP workforce context (Growth Portfolio, learning history, employee record) if a connector is live; otherwise simulated SAP-shaped context is labeled as such.
3. Candidate Intelligence produces a capability graph with evidence and confidence.
4. A real target role (requisition or job profile) is decomposed into tasks and requirement classes.
5. Diagnosis separates capability gaps from potential proxies.
6. Recomposition proposes a pathway (learning + proof + possible work-design adjustments).
7. Matching shows current-fit and pathway-fit opportunities.
8. Candidate and HR each see explanations.
9. HR records approve / modify / reject. Nothing is hired or rejected autonomously.

### Journey 2 — Hiring manager posts a noisy requisition

1. Job Decomposition classifies requirements.
2. Employer-readiness view flags potential exclusionary factors for **human review**.
3. HR can keep, rephrase, or replace a proxy with an evidence requirement.
4. Matching then runs against the **reviewed** requirement set, not the raw JD only.

### Journey 3 — Internal mobility

Same engine. Source of truth is more likely SAP (employee, skills, learning, opportunities). Destination is an internal role or gig. Governance is the manager + talent team.

These are not three products. They are three entries into the same loop: **DISCOVER → DECOMPOSE → DIAGNOSE → RECOMPOSE → DEVELOP → PROVE → MATCH → REVIEW → LEARN**.

---

## D. Core pain points

| Pain | Who feels it |
|---|---|
| Career-gap penalties in ATS and manager heuristics | Returners, HR filling roles slowly |
| Credential and institution proxies | Tier-2/3 graduates, career switchers |
| Geographic hard-filters unrelated to the work | Lucknow / non-metro talent |
| Rigid “N years in title X” | Anyone with adjacent experience |
| Inaccessible work design | Persons with disabilities, caregivers |
| Transferable skills invisible | Career switchers, internal staff |
| “Not a match” with no close-the-gap path | Candidates and L&D |
| Courses disconnected from a specific job | L&D spend with no placement |
| Learning without proof | Hiring managers who do not trust certificates |
| No explanation of exclusion | Legal, DEI, the candidate, the hiring manager |
| Optimization for current fit only | Enterprises with skills shortages |

---

## E. Product thesis

**Capability is a graph, not a keyword.**  
A person is a set of capabilities supported by heterogeneous evidence. A job is a set of tasks that produce outcomes under constraints. Matching is comparison of those graphs, plus an explicit treatment of missing evidence, trainable gaps, and potential proxies.

**Standards stay. Proxies get challenged.**  
RE:WORK never says “hire because of identity.” It says “this requirement may not be the work; here is the counterfactual; a human must decide.”

**Pathway is part of matching.**  
A candidate can be `ready_now`, `ready_with_proof`, `ready_with_bounded_pathway`, or `not_ready`. The last state is allowed. Honesty is a feature.

---

## F. Value proposition

### For candidates

“See what you can actually do, what is blocking you, and the shortest honest path to a real role — including a way to prove it.”

### For employers

“Fill roles against true task requirements, stop discarding capable people for history proxies, and keep an audit trail of every recommendation and human decision.”

### For SAP customers (enterprise)

“Keep SuccessFactors as the system of record. Add a reasoning layer that SuccessFactors does not natively do: counterfactual barrier analysis, proof-of-skill evidence, and closed-loop pathway-to-opportunity orchestration with mandatory human review.”

---

## G. Why this matters to enterprises

IDC/WEF-class skills-shortage narratives are in the SAP brief itself. The operational translation is:

- Open requisitions stay open because filters are crude.
- Internal talent is invisible because skills are stored, not reasoned over.
- L&D catalogs are consumed without tying completion to role readiness.
- DEI programs cannot show that exclusion happened at a *requirement* layer rather than a *people* layer.
- Audit and works-council / legal exposure rises if AI rejects people opaquely.

RE:WORK is valuable if it reduces **false negatives** (capable people excluded) without increasing **false positives** (unready people advanced), and if every call is explainable.

---

## H. Why this fits Inclusive Workforce

The official theme asks for a **career orchestrator**, not a chatbot, with skills discovery, market intelligence, learning pathways, inclusive matching, bias audit, and human judgment.

RE:WORK maps onto that brief and adds the missing operational idea: **recomposition**. Inclusion is not a ranking bonus. Inclusion is:

- seeing capability the ATS missed
- classifying barriers without auto-labeling “bias”
- offering a path to the same performance bar
- keeping humans in charge of employment decisions

---

## I. Why existing HR systems alone do not fully solve it

SAP SuccessFactors (Talent Intelligence Hub, Growth Portfolio, Learning, Opportunity Marketplace, Recruiting) is strong at:

- storing people, roles, skills, learning, opportunities
- inferring or importing skills
- recommending roles and content inside its model
- running enterprise workflows

It is not, out of the box, a system that:

- decomposes a noisy JD into task-level capabilities vs proxies
- runs a counterfactual (“if this tenure clause were replaced by a work sample, would the person still fail?”)
- accepts heterogeneous evidence (projects, caregiving-adjacent ops, informal work) with explicit confidence
- generates proof-of-skill artifacts that update readiness
- explains exclusion as *requirement class + evidence + confidence*
- closes the loop from diagnosis → pathway → proof → match → human decision → outcome learning

Those are RE:WORK. Claiming otherwise would be overclaiming SAP **and** underselling the prototype.

---

## J. Why RE:WORK is different

| Typical tool | RE:WORK |
|---|---|
| Resume matcher | Capability + evidence graph |
| Career chatbot | State machine with artifacts, not chat-first |
| Job board | Opportunity objects with workplace conditions |
| DEI scoring | No protected-class ranking advantage |
| Course recommender | Pathway bound to a named gap and a proof |
| Black-box “match %” | WHAT / WHY / EVIDENCE / CONFIDENCE / ALTERNATIVES / HUMAN DECISION |
| Autonomous agent | Proposal engine + governance |

---

## K. Success criteria

### Product (demo)

- One persona, end-to-end, in 3–5 minutes, including the wow contrast.
- Every recommendation inspectable.
- Human can approve / modify / reject; state updates.
- SAP context is visible and honestly labeled (`LIVE` vs `SIMULATED`).
- At least one agent is genuinely functional (not a slideshow).
- Orchestrator shows Skills Discovery, Market Intelligence, Learning Pathway, Inclusive Matching, Bias/barrier audit working as one loop.

### Product (quality)

- Gap vs proxy classification is explicit and conservative.
- No autonomous hire/reject.
- No fabricated evidence.
- No silent synthetic data.

### Enterprise

- Adapter-shaped so a live SuccessFactors destination can replace simulation without rewriting the intelligence layer.

---

## L. Non-goals

- Autonomous hiring or rejection
- Identity-based ranking or quotas as a match feature
- Inferring protected characteristics from names, photos, or language
- Replacing SuccessFactors, LMS, or ATS
- A public consumer job marketplace
- Live scraping of job boards as a dependency
- Claiming real wage / demand statistics without sources
- Ten production-grade LLM agents
- Medical, psychometric, or discriminatory testing
- “Fairness score” that pretends to solve bias with a single number

---

## Positioning sentence (for judges)

> SAP provides the workforce ecosystem. RE:WORK provides the intelligence that reasons across it — capability, evidence, barriers, pathways, and human decisions — without lowering the bar.
