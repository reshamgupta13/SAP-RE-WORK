# Checkpoint 07 — Pre-Implementation Audit

Audit date: CP7 start. Scope: full backend, tests, fixtures, frontend.

## Duplicated models

| Area | Finding | CP7 action |
|------|---------|------------|
| Run state vs case | `ReworkGraphState` and API responses duplicate case-shaped data | Introduce `ReworkCase` + `CaseSnapshot` as canonical store |
| Human review | `HumanReview` + `GovernanceAuditEntry` + review_store separate from runs | Link reviews to `case_id`; preserve AI snapshot |
| Decision card | Built on-the-fly in ExplainabilityService | Build from case snapshot; cache on case |
| SAP context | Returned from graph state and demo endpoints | Single path via SAP adapter + mapper |

No duplicate Pydantic models for Candidate/Job — reuse domain models inside snapshot JSON.

## Duplicated run logic

| Location | Issue | CP7 action |
|----------|-------|------------|
| `OrchestrationService.execute_demo_run` | Each API endpoint creates new run | Case `execute` resumes/replays with stage targets |
| `ControlRoomService.build_control_room` | Runs full graph independently | Delegate to `CaseService` finale case |
| `InterventionSimulator.run` | Re-runs opportunity analysis | Link scenarios to `case_id`; never mutate case |
| Multiple RunModes | Parallel stop points | Map `execute_until` lifecycle stages to RunMode |

## Duplicate calculations

- Frontend: **no** viability/diagnosis calculation found — displays API fields only.
- Backend: opportunity analysis invoked in graph and intervention simulator — acceptable for projections with explicit `SIMULATED` label.

## Inconsistent IDs

- `run_id` vs `case_id` — runs were ephemeral; cases become primary.
- Opportunity IDs (`opp-data-analyst`) vs job IDs (`data-analyst-junior`) — preserved; case stores both.
- Intervention/scenario IDs prefixed inconsistently — normalized in case snapshot.

## Source_mode behavior

- Fixtures: SYNTHETIC/SIMULATED consistent.
- SAP adapter: always SimulatedSAPProvider when `demo_mode=true` regardless of env — **fixed** with explicit `SAP_MODE`.
- Control room hardcoded `sap: SIMULATED` — **fixed** to read adapter health.

## Frontend business logic

- Control Room, Candidate, Employer, HR Review: presentation only.
- Intervention simulator UI: selection/compare only; no score computation.

## Unnecessary agent calls

- Graph invokes LLM agents; `DEMO_FALLBACK` avoids external LLM.
- `CONTROL_ROOM_DEMO` runs full graph once per case execute — golden replay uses single execute.

## Unsafe LLM assumptions

- Agents use fixture fallback when demo_mode — OK.
- Resume upload: **not implemented** — no upload surface in CP6.
- Prompt separation: agents receive structured task + fixture data — document UNTRUSTED for future upload.

## SAP boundaries

| Component | Status pre-CP7 |
|-----------|----------------|
| `SimulatedSAPProvider` | Fixture-backed, SIMULATED |
| `LiveSAPProvider` | Stub NotImplemented |
| `get_sap_provider()` | Always simulated |
| Write-back (`update_skill_progress`) | Called in graph for demo — **read-only live rule** documented |
| SAP Learning adapter | Simulated catalog |

## Persistence

- `run_store`, `review_store`: in-memory dicts.
- SQLAlchemy engine exists but unused — **CP7 adds repository layer + optional Postgres**.

## Recommended convergence

1. **ReworkCase** as source of truth.
2. **CaseRepository** interface; InMemory default; Postgres optional.
3. **CaseEvent** log for all transformations.
4. **case_version** increment on mutation; human review references version.
5. **Single execute path** via CaseService → OrchestrationService.
6. **SAP_MODE** explicit; health endpoint; mapper layer.
7. Keep legacy `/api/runs/*` working via orchestration wrapper.

## Do not rewrite blindly

- LangGraph nodes remain — case wraps graph output.
- Diagnosis/pathway/viability engines unchanged.
- CP1–CP6 tests must continue passing.
