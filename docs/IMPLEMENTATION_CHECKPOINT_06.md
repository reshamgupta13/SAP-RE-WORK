# Implementation Checkpoint 06

## Intervention Simulator

- `InterventionSimulator` (`backend/app/services/intervention_simulator.py`)
- Domain models: `Intervention`, `InterventionEffect`, `Scenario`, `InterventionBundle`
- Types: `LEARNING`, `PROOF_OF_SKILL`, `MENTORSHIP`, `HYBRID_WORK`, `STRUCTURED_ONBOARDING`, `EVIDENCE_SUBSTITUTION`, and others
- Single intervention and bundle simulation with scenario tree
- Minimum effective intervention ranking by effort vs viability change
- Two-sided: candidate interventions (learning, proof) and employer interventions (mentorship, onboarding, hybrid)
- All projections labeled **SIMULATED PROJECTION** — not guaranteed outcomes

## Scenario model

- `Scenario` preserves parent, assumptions, before/after viability, `InterventionEffect`
- Bundles A–D: Learning only → Learning + Proof → + Mentorship → + Hybrid Work
- Counterfactual language: "potential eligibility barrier reduced under this scenario"

## Explainability architecture

- `ExplainabilityReport`, `EvidenceChainNode`, `ReviewableRecommendation`
- `ExplainabilityService` — structured WHAT/WHY/EVIDENCE/CONFIDENCE/ALTERNATIVES/ASSUMPTIONS
- Confidence labels: `HIGH_CONFIDENCE`, `MEDIUM_CONFIDENCE`, `LOW_CONFIDENCE`, `UNCERTAIN`
- Evidence chains: Recommendation → Diagnosis → Capability → Evidence

## Human Review

- `HumanReview` extended with `modified_interventions`, `modified_pathway`, `ai_recommendation_snapshot`
- `HumanReviewService` — APPROVE, MODIFY, REJECT, REQUEST_MORE_EVIDENCE
- AI recommendation preserved; human decision logged via `GovernanceAuditEntry`
- Language: "AI recommendation generated" + "Human decision: APPROVED"

## Control Room

- `GET /api/demo/control-room` — aggregated demo payload
- `ControlRoomService` assembles full story from `CONTROL_ROOM_DEMO` run
- Frontend: `/control-room` — pipeline, decision card, intervention simulator, SAP context

## Candidate View

- `/candidate` — capability, target, gaps, pathway, proof, opportunities, next action
- No HR-only governance exposure

## Employer View

- `/employer` — mentorship, onboarding, work mode factors with READY / PARTIALLY_READY / UNKNOWN / NOT_READY

## SAP Context

- SAP ecosystem panel: SuccessFactors, Talent Intelligence, Learning, Opportunity — all **SIMULATED**
- BTP: **NOT_CONNECTED**
- No LIVE claim without verified credentials

## Source Modes

- `SourceBadge` component — LIVE, SIMULATED, SYNTHETIC, MOCKED, USER_PROVIDED

## Demo

- `RunMode.CONTROL_ROOM_DEMO` — full pipeline through intervention + explainability
- Deterministic under `DEMO_FALLBACK`
- Ananya → Data Analyst story with Power BI gap and intervention bundles

## APIs

| Endpoint | Purpose |
|----------|---------|
| `POST /api/runs/intervention-simulation` | Run or custom intervention simulation |
| `GET /api/runs/{id}/explainability` | Structured explainability reports |
| `POST /api/reviews` | Human review submission |
| `GET /api/demo/control-room` | Aggregated control room |
| `GET /api/demo/scenarios` | Intervention scenarios |

## Tests

- `test_intervention.py` — 11 tests
- `test_explainability.py` — 7 tests
- `test_human_review.py` — 7 tests
- `test_control_room.py` — 4 tests
- **134 total tests passing**

## Golden snapshot

- `fixtures/golden/checkpoint_06_ananya.json`

## Known limitations

- In-memory run and review stores (no persistence)
- Intervention baseline for demo uses pre-proof fixture capabilities for projection story
- Confidence labels are heuristic, not statistically calibrated
- No live SAP, market, or LLM required in demo mode
- Frontend fetches single aggregated endpoint; no client-side scoring

## Next

Production Hardening + SAP Landscape Integration + Golden Demo

**No live SAP integration has been claimed or implemented.**
