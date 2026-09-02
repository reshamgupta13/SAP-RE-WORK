# Live SAP setup

RE:WORK never talks to SAP from the browser. The frontend calls the RE:WORK API; the backend is the only process allowed to contact the OData service.

## Environment

Copy `backend/.env.example` and fill placeholders only. Do not commit secrets.

```
SAP_MODE=LIVE
SAP_ODATA_BASE_URL=
SAP_ODATA_SERVICE=
SAP_ODATA_METADATA_URL=
SAP_AUTH_MODE=BASIC
SAP_USERNAME=
SAP_PASSWORD=
SAP_TIMEOUT_SECONDS=15
```

`SAP_MODE=LIVE` alone is not enough. LIVE is reported only after:

1. The configured base URL is reachable
2. Authentication succeeds
3. `$metadata` can be read
4. At least one intended seven-table entity set returns a GET collection (empty is still a successful retrieval)

If credentials are missing: `NOT_CONNECTED`.
If the call fails: `NOT_CONNECTED` or `ERROR`.
Fixtures are never swapped in to make LIVE look populated.

## Discovery order

1. Set the official service root (typically `/sap/opu/odata/sap/<SERVICE>/`).
2. GET `$metadata`.
3. Map EntitySets to the seven tables (see `docs/ODATA_ENTITY_MAPPING.md`).
4. Optionally set `SAP_ENTITY_*` to lock the verified names.
5. Run `python scripts/sap_live_smoke_test.py`.

## Modes

| Mode | When | Product UI data |
| --- | --- | --- |
| LIVE | Verified OData retrieval | SAP records only |
| NOT_CONNECTED | Missing URL/credentials | Honest empty states |
| ERROR | Transport/auth/data failure | Error + retry |
| SIMULATED | `SAP_MODE` not LIVE, or automated tests | `/api/demo/*` only — not the main UI |

`DEMO_MODE=true` keeps Ananya fixtures for pytest and `/api/demo/*`. It does not feed the product catalog.
