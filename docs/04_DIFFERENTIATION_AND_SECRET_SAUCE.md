# 04 — Differentiation and Secret Sauce

**Judge-summarizable line:**

> SAP provides the workforce ecosystem. RE:WORK provides the intelligence that reasons across it.

If a feature does not survive the question *“Does this solve a workforce problem a real user cares about, beyond what SAP already provides?”* it does not ship.

---

## 1. Two layers

```
+------------------------------------------------------------------+
|  SAP FOUNDATION                                                  |
|  People, roles, requisitions, attributes, learning,              |
|  opportunities, workflows, permissions, audit of transactions    |
+------------------------------------------------------------------+
                              |
                              | adapter (live or simulated)
                              v
+------------------------------------------------------------------+
|  RE:WORK INTELLIGENCE                                            |
|  Evidence synthesis, job decomposition, gap vs proxy diagnosis,  |
|  counterfactual barrier analysis, pathway + proof orchestration, |
|  explainable matching, human decision capture, outcome learning  |
+------------------------------------------------------------------+
```

SAP is **system of record**.  
RE:WORK is **system of reasoning**.  
RE:WORK must not become a second HCM.

---

## 2. What SAP already covers (do not rebuild)

| Capability | Typical SAP home | RE:WORK stance |
|---|---|---|
| Store employees and org | Employee Central | Consume |
| Store requisitions / applications | Recruiting | Consume; do not become an ATS |
| Canonical skill attributes | Talent Intelligence Hub | Align IDs; do not fork taxonomy in production |
| Per-person skill portfolio | Growth Portfolio | One evidence source |
| Courses, assignments, completion | SuccessFactors Learning | Map pathway items |
| Internal gigs / career exploration | Opportunity Marketplace | Opportunity source |
| Workflow, RBAC, employee UX | SuccessFactors / BTP | Respect; prototype uses our UI |
| In-product copilot agents | Joule family | Complement, do not clone |

---

## 3. The gap: store / infer / recommend vs reason

| SAP-like operation | What it does | What it does not do (gap) |
|---|---|---|
| **Store skills** | Attribute on person or role | Explain *why* we believe it, from mixed evidence |
| **Infer skills** | Suggest attributes from SF data | Ingest caregiving-era operations, informal work, projects with calibrated confidence |
| **Recommend jobs** | Similarity / career explorer | Separate “cannot do the work” from “fails a proxy filter” |
| **Recommend learning** | Catalog by skill gap | Bind to a *specific* requisition, a proof, and a readiness state |

RE:WORK is the layer that **decomposes, diagnoses, challenges, and recomposes**.

---

## 4. Secret sauce (the only features that justify a prototype)

### 4.1 Demonstrated capability from heterogeneous evidence

Not “skills on a resume.” An evidence set: artifacts, outcomes, recency, context, source reliability. Output is a capability instance, not a boolean.

### 4.2 Job as tasks, not as a paragraph

JD → outcomes → responsibilities → tasks → capabilities → evidence expectations → constraints → credential/experience clauses. Each clause gets a **requirement class**.

### 4.3 Capability gap vs historical eligibility gap

The diagnosis object is the product. A single match percentage is explicitly *not* the product.

### 4.4 Counterfactual barrier analysis

> If this requirement were replaced with direct evidence of the underlying capability, would the person still be unable to perform the work?

Never auto-declares bias. Language: **potential exclusionary factor**, **potential proxy**, **requires review**.

### 4.5 Proof-of-skill as the trust bridge

Learning and matching fail without a work sample the hiring manager can inspect. Proof updates the capability graph.

### 4.6 Closed-loop recomposition

Pathway is not a course list. It is the plan that changes match state from `not_ready` / `ready_with_pathway` toward `ready_with_proof` / `ready_now`.

### 4.7 Evidence chains humans can sign

WHAT / WHY / EVIDENCE / CONFIDENCE / ALTERNATIVES / HUMAN DECISION.

### 4.8 Systematic exclusion monitoring without demographic inference

Audit **requirement classes** and **knockout patterns** (gap length, institution, city, years-in-title) across a batch of recommendations. Do not infer gender, caste, religion, disability.

---

## 5. Differentiation framework (feature tests)

| Proposed feature | SAP already? | User pain? | Keep? |
|---|---|---|---|
| Chat UI as home screen | Joule exists | Low for this problem | **No** — control room + artifacts |
| Match percentage only | Recruiting / OMM | Causes the problem | **No** |
| Skills cloud visualization | TIH / GP | Partial | Only if tied to evidence |
| Course carousel | LMS | Low | **No** unless bound to gap+proof |
| “Inclusive score” from identity | Not acceptable | Harmful | **Never** |
| Barrier counterfactual panel | No | Yes | **P0** |
| Requirement classification | No (not like this) | Yes | **P0** |
| Proof-of-skill tied to role | Assessments exist in SF; not this loop | Yes | **P0/P1** |
| Human approve/modify/reject | Workflows exist; not this reasoning | Yes | **P0** |
| Live market scraping | No | Unreliable | **No** for P0 |
| Neo4j | No | Unjustified | **No** |

---

## 6. What a judge should *not* be able to say

- “This is a chatbot with an SAP logo.”
- “This is cosine similarity on JD and resume.”
- “This lowers the bar for a demographic group.”
- “SuccessFactors already recommends jobs and courses.”
- “They invented a TIH API.”

## 7. What a judge should be able to say

- “They kept the performance standard and attacked proxies.”
- “The Lucknow returner wasn’t given a pity match; she was given evidence, one trainable gap, and a proof.”
- “HR can disagree and the system records it.”
- “SAP is clearly the system of record even if the tenant is simulated, and they know the difference.”

---

## 8. Non-secret, still required

Orchestration, provenance labels, demo fixtures, and UX polish are **table stakes**, not differentiators. They make the sauce visible. They are not the sauce.
