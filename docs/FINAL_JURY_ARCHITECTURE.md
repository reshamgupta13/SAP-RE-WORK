# Final Jury Architecture

## One canonical case

`case-ananya-finale` — single source of truth for the jury demo.

## Flow

```
SAP Adapter → ReworkCase → LangGraph → Control Room → Human Decision
```

## Layers

| Layer | Responsibility |
|-------|----------------|
| SAP Adapter | Workforce, skills, learning, opportunities (read-only) |
| LangGraph | Agent + engine orchestration |
| Case Service | Persistence, timeline, export, reset |
| Control Room | Jury UX — no business logic |
| Human Review | Governance boundary |

## Reset

`POST /api/demo/reset` — restores finale case without server restart.

## Negative demonstration

`GET /api/demo/negative-case?scenario_id=B07` — shows intelligence refusing forced outcomes.

## Source modes

Every object carries `source` and `source_mode`. LIVE only when verified.
