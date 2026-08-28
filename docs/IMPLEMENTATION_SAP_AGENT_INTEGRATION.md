# SAP + Agent Orchestration Integration

## 1. Agent architecture

RE:WORK uses **LangGraph** as the orchestrator coordinating:

| Node | Type | Responsibility |
|------|------|----------------|
| `load_candidate` | Integration | SAP context load + candidate fixture |
| `candidate_intelligence` | AI Agent | Evidence → capability profile |
| `load_job` | Integration | SAP role context + job fixture |
| `job_decomposition` | AI Agent | Job → tasks, capabilities, requirements |
| `diagnosis` | Engine | Gap diagnosis (deterministic) |
| `counterfactual_analysis` | Engine | Eligibility proxy analysis |
| `pathway_generation` | Engine | SAP Learning → minimum-effective pathway |
| `proof_of_skill` | Engine | Capability verification |
| `capability_refresh` | Integration | Simulated SAP skill write-back |
| `reassessment` | Engine | Post-proof diagnosis |
| `market_intelligence` | Engine | Market signals (synthetic) |
| `opportunity_viability` | Engine | Two-sided viability |
| `employer_readiness` | Engine | Employer factors |
| `intervention_simulation` | Engine | Projected scenarios |
| `explainability` | Service | Decision card + reports |

Agents do **not** call SAP directly. All SAP access goes through `get_sap_provider()`.

## 2. SAP architecture

```
SAP Ecosystem
     │
SAP Adapter (SimulatedSAPProvider | LiveSAPProvider)
     │
SAPContextService.load_for_case()
     │
Canonical domain (SAPContext, SAPCaseBundle)
     │
LangGraph nodes
```

Key files:
- `backend/app/adapters/sap/` — provider layer
- `backend/app/services/sap_context_service.py` — case bundle loader
- `backend/app/adapters/sap_learning/` — learning catalog

## 3. SAP → RE:WORK data flow

1. `load_candidate` calls `SAPContextService.load_for_case(candidate_id, job_id)`
2. Adapter returns workforce, skills, role, learning, opportunity slices with provenance
3. `SAPContext` stored in graph state as `sap_context` + `sap_case_context`
4. `candidate_intelligence` receives SAP context (provenance note; no fabrication)
5. `load_job` tries `get_role_context()` via adapter, falls back to fixture
6. `pathway_generation` queries SAP Learning via `get_sap_learning_provider()`
7. `capability_refresh` calls simulated `update_skill_progress()`

## 4. Agent → SAP data flow

| Step | Action |
|------|--------|
| Pathway | Queries SAP Learning catalog for gap-aligned items |
| Capability refresh | Simulated skill progress write-back |
| Audit | Records `sap:{mode}` in source_references |

Live write-back is **disabled** until read integration is verified.

## 5. Live vs simulated

| Mode | Trigger | UI label |
|------|---------|----------|
| SIMULATED | `DEMO_MODE=true` or `SAP_MODE=SIMULATED` | SIMULATED |
| LIVE | `SAP_MODE=LIVE` + verified OAuth | LIVE (auth only; reads unverified) |

Control Room header shows actual `source_mode` from health check.

## 6. Source provenance

| Origin | `source` | `source_mode` |
|--------|----------|---------------|
| SAP adapter | SAP | LIVE / SIMULATED |
| Agent reasoning | REWORK | SYNTHETIC |
| Market fixtures | MARKET_SIMULATION | SYNTHETIC |
| Demo proof | REWORK | SYNTHETIC + `is_demo: true` |

## 7. Error / fallback behavior

| Failure | Fallback |
|---------|----------|
| LLM unavailable | DEMO_FALLBACK deterministic agents |
| SAP unavailable | SIMULATED provider |
| Live read NotImplemented | Slice status UNAVAILABLE; case continues |
| Learning empty | Synthetic fallback items in pathway |
| Proof failure | Capability does not upgrade |

## 8. Security

- Credentials env-only; redacted in export
- `test_live_sap.py` never prints secrets
- CORS: localhost:3000
- No production authN/Z

## 9. Explainability

Trace chain: Recommendation → Viability → Diagnosis → Capability → Evidence → Task → Requirement

Agent orchestrator panel exposes per-node: status, duration, confidence, evidence count, input sources.

## 10. Human governance

- AI recommendation stored separately from human decision
- Control Room footer shows both explicitly
- Stale review version blocked

## 11. Final demo architecture

```
                    SAP ECOSYSTEM
                         │
          ┌──────────────┼───────────────┐
          │              │               │
      Workforce        Skills         Learning
          │              │               │
          └──────────────┼───────────────┘
                         │
                    SAP ADAPTER
                         │
                         ▼
               ┌──────────────────┐
               │  RE:WORK CASE    │
               └────────┬─────────┘
                        │
                LANGGRAPH ORCHESTRATOR
                        │
       ┌────────────────┼─────────────────┐
       │                │                 │
       ▼                ▼                 ▼
 Candidate           Job              Diagnosis
 Intelligence     Decomposition
       │                │                 │
       └────────────────┼─────────────────┘
                        ▼
                 Counterfactual
                        │
                        ▼
                  Pathway Engine
                        │
                        ▼
                 Proof-of-Skill
                        │
                        ▼
                   Reassessment
                        │
                        ▼
                Opportunity Viability
                        │
                        ▼
                Intervention Simulator
                        │
                        ▼
                  EXPLAINABILITY
                        │
                        ▼
                  HUMAN DECISION
```

Canonical case: `case-ananya-finale`
