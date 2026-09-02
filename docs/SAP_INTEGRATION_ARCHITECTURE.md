# SAP Integration Architecture

## Principle

```
SAP (system of record)
  ↓ OData (transport)
  ↓ SAP Adapter (LiveSAPProvider / SimulatedSAPProvider)
  ↓ Canonical RE:WORK domain models
  ↓ AI + deterministic reasoning
  ↓ Human decision
```

RE:WORK is the **system of reasoning**. SAP is **enterprise context**.

## Adapter layer

```
SAPProvider (abstract)
├── SimulatedSAPProvider   ← fixtures, deterministic demo
└── LiveSAPProvider
      └── SAPODataClient   ← HTTP/OData only, no business logic
            └── SAPMapper  ← OData DTO → canonical models
```

### Key files

| File | Role |
|------|------|
| `backend/app/adapters/sap/provider.py` | Abstract interface |
| `backend/app/adapters/sap/simulated.py` | Demo provider |
| `backend/app/adapters/sap/live.py` | Live OData provider |
| `backend/app/adapters/sap/odata_client.py` | Metadata + collection reads |
| `backend/app/adapters/sap/odata_config.py` | Entity allow-list / access plan |
| `backend/app/adapters/sap/mapper.py` | Canonical mapping |
| `backend/app/adapters/sap/provenance.py` | Source trace metadata |
| `backend/app/adapters/sap/health.py` | Health probe |
| `backend/app/services/sap_context_service.py` | Case bundle aggregation |

## Source mode safety

- `SIMULATED` — demo fixtures
- `NOT_CONNECTED` — configured but unverified
- `LIVE` — metadata successfully verified
- `ERROR` — unexpected failure

Configuration saying `SAP_MODE=LIVE` does **not** imply LIVE source mode.

## Metadata-first integration

1. Fetch `$metadata`
2. Discover EntitySets
3. Validate configured mappings
4. Read approved entities only (allow-list)
5. Map to canonical models

No arbitrary entity names from the frontend.

## Evidence semantics

SAP qualifications map to `SAP_RECORDED` evidence — not automatic proof of capability. The Candidate Intelligence engine merges SAP context with other evidence types using existing priority rules.

## Provenance

Every imported object carries:

- `source = SAP`
- `source_mode`
- `entity_set`
- `object_id`
- `retrieved_at`
- `mapped_to`

## Control Room

The SAP panel shows:

- Source mode (backend truth)
- Domain slice status
- Record counts
- SAP → RE:WORK boundary
- Expandable trace

## Demo behavior

`DEMO_MODE=true` always uses `SimulatedSAPProvider`. The Ananya finale case (`case-ananya-finale`) remains fully executable without SAP credentials or network.

## Future live connection

When faculty provides the OData URL, only configuration and entity mapping change. No intelligence pipeline redesign required.
