# Implementation Checkpoint 05

**Date:** 2026-08-28  
**Branch:** `feature/rework-p0`  
**Scope:** Opportunity Viability + Market Intelligence + Employer Readiness  
**Prerequisite:** Checkpoint 04 (`9c7c12a`)

---

## 1. Opportunity Viability architecture

RE:WORK does **not** implement job matching. It implements **opportunity viability**:

> Can this candidate realistically become successful in this opportunity, what would it take, and what conditions would enable that success?

```
Diagnosis + Pathway + Proof (optional)
        ↓
MarketIntelligenceEngine
        ↓
OpportunityViabilityEngine (per opportunity)
        ↓
EmployerReadinessEngine (two-sided gap)
        ↓
OpportunityComparisonService
        ↓
OpportunityCounterfactual
```

LangGraph nodes: `market_intelligence` → `opportunity_viability` → `employer_readiness` → `opportunity_comparison`

Run mode: `OPPORTUNITY_ANALYSIS` (diagnosis through counterfactual, then viability — no fabricated proof)

---

## 2. Market Intelligence

`MarketIntelligenceEngine` reasons over **structured synthetic signals** (`fixtures/market/signals.json`).

- Signal types: `SKILL_DEMAND`, `ROLE_DEMAND`, `LEARNING_PRIORITY`, etc.
- All signals: `source_mode=SYNTHETIC` — not presented as live labor statistics
- `SkillInvestmentScenario`: unlockable roles, effort estimate, proof requirement

Answers: *"What capability investment gives the best opportunity expansion?"*

---

## 3. Skill Investment

Compares investments (Power BI, Python, Data Modeling) against market signals and opportunity catalog.

Example: Power BI unlocks Data Analyst, BI Analyst, Reporting Analyst roles in demo fixtures.

---

## 4. Employer Readiness

`EmployerReadinessEngine` assesses employer-side readiness factors:

- Mentorship, onboarding, hybrid/remote, phased responsibility, learning support, proof acceptance, etc.
- States: `READY`, `PARTIALLY_READY`, `NOT_READY`, `UNKNOWN`
- Unknown factors → human review + evidence-based interventions
- Does not assume unspecified employer support

---

## 5. Two-sided gap model

| Side | Example |
|---|---|
| Candidate gap | Power BI proficiency below role threshold |
| Employer gap | No structured onboarding (if `NOT_READY`) |

Viability states combine both — e.g. `VIABLE_WITH_PATHWAY_AND_ADAPTATION` when candidate gap is trainable but employer readiness is partial.

---

## 6. Opportunity Counterfactual

`OpportunityCounterfactual` asks: *What would have to change for this opportunity to become viable?*

Lists required changes (capability pathway, proof, employer adaptations) without discrimination verdicts.

---

## 7. Ananya comparison (OPPORTUNITY_ANALYSIS, pre-proof)

| Opportunity | Typical result |
|---|---|
| Data Analyst | `VIABLE_WITH_TARGETED_PATHWAY` — Power BI gap, experience proxy flagged |
| Operations Analyst | `IMMEDIATELY_VIABLE` — strong fit, low effort, compatible work mode |
| BI Analyst | Higher development effort — additional modeling gap |

**Recommended next step:** Operations Analyst (fastest transition)  
**Medium-term aligned path:** Data Analyst

---

## 8. SAP boundary

- Opportunity catalog and market signals are RE:WORK synthetic fixtures
- SAP Opportunity Marketplace adapter (`SimulatedSAPProvider.get_opportunities`) remains separate from viability logic
- No live SAP Opportunity Marketplace or Talent Intelligence Hub integration

**No live SAP integration has been claimed or implemented.**

---

## 9. Fallback behavior

All viability logic is **deterministic**. `OPPORTUNITY_ANALYSIS` works with `engine_mode=DEMO_FALLBACK` — no LLM required.

---

## 10. Tests

| Suite | Count |
|---|---|
| Checkpoint 01–04 | 87 |
| Opportunity viability | 18 |
| **Total** | **105 passed** |

---

## 11. Known limitations

- Synthetic market signals only — not calibrated labor data
- Opportunity catalog is demo-scoped (4 roles)
- Workplace compatibility uses opportunity work_modes, not full candidate preference matching yet
- No HR decision UI or explainability dashboard
- FULL_DEMO_REPLAY + opportunity analysis requires separate runs (or extend run mode later)

---

## 12. Next checkpoint

**Human Review + Explainability + Enterprise Control Room**

---

## 13. API quick reference

```bash
# Full opportunity viability analysis
curl -X POST http://localhost:8000/api/runs/viability \
  -H "Content-Type: application/json" \
  -d '{"candidate_id":"ananya-sharma","job_id":"data-analyst-junior"}'

# Demo fixtures
curl http://localhost:8000/api/demo/opportunities
curl http://localhost:8000/api/demo/market
```

---

**No live SAP integration has been claimed or implemented.**
