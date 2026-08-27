# 15 — Responsible AI and Governance

Employment-related recommendations. Treat as high-risk.

**RE:WORK proposes. Humans decide. The system never hires or rejects autonomously.**

---

## 1. Every recommendation is explainable as

| Field | Content |
|---|---|
| **WHAT** | Readiness state + ranked opportunities / pathway |
| **WHY** | Requirement classes, coverage math, constraints |
| **EVIDENCE** | Evidence ids, quotes, SAP object refs |
| **CONFIDENCE** | Per stage + inherited |
| **ALTERNATIVES** | Other roles, keep vs replace requirement, no_viable_path |
| **HUMAN DECISION** | approve / modify / reject / defer + actor + timestamp |

If any field cannot be filled, do not show a fake match %.

---

## 2. Controls

| Control | Rule |
|---|---|
| Evidence traceability | No capability without evidence or explicit `unsupported` drop |
| No fabricated evidence | Validators strip unsourced employers/skills |
| No unsupported sensitive traits | Schema forbids; prompts forbid; eval tests this |
| No hidden scoring | Rank formula published in UI “method” drawer |
| No black-box final decision | Governance state machine |
| Uncertainty | Low confidence → escalate; disable one-click approve (P1) |
| Override | HR field-level override stored as `HumanDecision.patches` |
| Appeal | P1: candidate requests re-review; new run_id linked |
| Audit logs | `audit_events` append-only |
| Human approval | Mandatory for employment-affecting persist |
| No autonomous rejection | `not_ready` is a recommendation state, not “rejected applicant” in SAP |
| No autonomous hiring | No write to “hired” |

---

## 3. Prompt and model policy

- System prompt includes: do not infer gender/religion/caste/disability; do not give legal advice; do not invent SAP records; do not claim statistics not in tools.
- Temperature 0 in demo.
- Tool outputs are the only numeric market data.

---

## 4. Data minimization

Store work-relevant evidence. Do not store medical details, children’s names, or caste. Caregiving break can be stored as `timeline.kind=break` with optional note “caregiving” **only if the candidate entered it**.

---

## 5. Fairness approach (honest)

We **cannot** prove group fairness without demographics, and we **will not** infer them.

We **can**:

- Reduce proxy knockouts via counterfactuals + human review
- Equal task versions for proofs
- Audit requirement-class patterns
- Fail closed on undeclared sensitive ranking features

This is **process fairness**, not a demographic parity dashboard.

---

## 6. Failure / incident

If the model produces a prohibited claim: discard narrative, show structured artifacts, log `safety_block`.

---

## 7. Accountability

`HumanDecision.actor_role` must be `hr` for approve-on-requisition. Candidate can accept a pathway without implying HR approval.
