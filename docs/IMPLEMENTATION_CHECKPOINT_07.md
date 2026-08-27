# Implementation Checkpoint 07

## Canonical case architecture

- `ReworkCase` — source of truth for candidate/opportunity journey
- `CaseSnapshot` — full validated state at a point in time
- `CaseEvent` — audit backbone for transformations
- `CaseService` — unified execution, review, control room projection
- Finale case ID: `case-ananya-finale`

## Case state machine

Lifecycle states from `CASE_CREATED` through `EXPLANATION_READY`, `DECISION_RECORDED`, `OUTCOME_*`, `CLOSED`, `EVIDENCE_PENDING`.

Partial execution via `CaseStage` + `execute_until` mapped to existing LangGraph `RunMode` values.

## Persistence strategy

- `CaseRepository` interface
- `InMemoryCaseRepository` — default for `DEMO_MODE=true` and tests
- `PostgresCaseRepository` — optional when `PERSISTENCE_MODE=postgres`
- SQLAlchemy models in `app/db/models.py`

## SAP integration status

| Capability | Status |
|------------|--------|
| Workforce context | SIMULATED (fixtures) |
| Skills/attributes | SIMULATED |
| Learning catalog | SIMULATED |
| Opportunities | SIMULATED |
| Live OData/OAuth | Stub only — requires verified tenant credentials |
| Write-back | Disabled for live mode |

**No live SAP capability has been claimed unless verified through an actual successful connection.**

## Live/simulated switching

- `SAP_MODE=SIMULATED` (default) or `LIVE`
- `get_sap_provider()` never silently switches to LIVE
- `GET /api/sap/health` — configured, reachable, authenticated, modules, source_mode
- `SAPMapper` — SAP responses → canonical domain objects
- Live failures return `source_mode=LIVE`, `status=ERROR` — no hidden fallback

## Event log

`CaseEvent` records transformations with actor_type, snapshot refs, rationale, idempotency_key.

## Versioning

`case_version` increments on each state mutation. Human review accepts `reviewed_case_version` to detect stale reviews.

## Explainability

Case-level explainability with integrity validation (`ExplainabilityIntegrityService`).
Evidence reference validation tests included.

## Golden replay

- Fixture: `fixtures/golden/finale_ananya_case.json`
- Script: `scripts/golden_replay.py`
- Output: `artifacts/golden/finale_ananya_replay.json`

## Benchmark results

- Catalog: `fixtures/benchmark/scenarios.json` (22 scenarios)
- Script: `scripts/benchmark_eval.py`
- Output: `artifacts/evaluation/latest_report.json`
- S01 (Ananya) fully executed; others metadata catalog for expansion

## Security

- SAP credentials via environment only — never exposed in API
- CORS limited to localhost:3000
- No resume upload surface in CP7
- LLM prompts use structured fixtures; untrusted document separation documented
- Live SAP read-only; write-back raises NotImplementedError

## Known limitations

- Live SAP requires tenant-specific endpoint verification
- Postgres persistence optional — not required for demo
- 21 benchmark scenarios await dedicated fixtures
- Intervention simulator still uses baseline fixture for projection story

## Tests

147+ tests including case lifecycle, idempotency, SAP health, integrity, golden fixture presence.

**No live SAP integration has been claimed or implemented without verified connection.**
