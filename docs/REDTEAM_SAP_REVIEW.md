# Red Team — SAP Architecture Review

**Auditor:** SAP Solution Architect persona  
**Verdict:** PASS with SIMULATED boundary (no live tenant verified)

## Boundary summary

| Layer | SAP | RE:WORK |
|-------|-----|---------|
| Workforce context | `SimulatedSAPProvider.get_candidate_context()` | Case orchestration, evidence merge |
| Skills / attributes | Empty for external candidate (Ananya) | Candidate Intelligence from evidence |
| Role context | `get_role_context()` via adapter | Job Decomposition + diagnosis |
| Learning | `sap_learning` adapter + fixtures | Gap-bound pathway selection |
| Opportunities | Fixture catalog | Viability + employer readiness reasoning |
| Write-back | Simulated `update_skill_progress()` | Capability refresh after proof only |

## Feature matrix

### Candidate Intelligence
- **SAP:** Workforce/growth portfolio context (simulated)
- **SAP already does:** Employee records, attributes
- **RE:WORK adds:** Evidence synthesis, verification status, inference labels
- **Why it matters:** SAP stores context; RE:WORK interprets what is *demonstrable*

### Diagnosis
- **SAP:** Role requirements context
- **SAP already does:** Role definitions in SF
- **RE:WORK adds:** Genuine gap vs eligibility proxy vs workplace constraint
- **Why it matters:** Separates capability from barrier

### Learning Pathway
- **SAP:** Learning catalog items with `sap_learning_item_id`
- **SAP already does:** Learning delivery and assignment
- **RE:WORK adds:** Minimum-effective pathway tied to diagnosed gap
- **Why it matters:** Avoids generic learning feeds

### Opportunity Viability
- **SAP:** Opportunity fixtures
- **SAP already does:** Opportunity Marketplace listing
- **RE:WORK adds:** Two-sided readiness, proof requirement, intervention projection
- **Why it matters:** Answers *when* opportunity becomes viable

### Proof-of-Skill
- **SAP:** Not used for completion in demo
- **RE:WORK adds:** Rubric-based verification loop
- **Why it matters:** Closes capability claim with evidence

## Duplicate functionality risks

| Risk | Status |
|------|--------|
| Rebuilding ATS | PASS — no applicant tracking |
| Rebuilding Opportunity Marketplace | PASS — viability layer only |
| Rebuilding Learning LMS | PASS — catalog query + pathway binding |
| Fake LIVE SAP | PASS — demo forces SIMULATED |

## Unsupported claims found

| Claim | Code support | Action |
|-------|--------------|--------|
| `SuccessFactors-compatible` in simulated context | Fixture label only | ACCEPTED — labeled SIMULATED |
| Live OAuth success | Auth stub only | Documented UNAVAILABLE |
| BTP / Integration Suite | Not implemented | Documented UNAVAILABLE |

## Architecture leak check

PASS — Diagnosis engine uses canonical `JobCapability`, `CandidateCapability`, not SAP JSON.

```
SAP → SAPMapper / Provider → Canonical Domain → Engines
```

**No SAP capability presented as LIVE unless verified through a successful real connection.**
