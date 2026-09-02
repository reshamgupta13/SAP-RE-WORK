# SAP OData Configuration

Configure RE:WORK to consume the official SAP OData service when faculty provides the URL.

## Environment variables

Set these in `backend/.env` (never commit secrets):

```env
SAP_MODE=SIMULATED          # SIMULATED | LIVE
DEMO_MODE=true              # true = always simulated (hackathon demo)

# OData transport
SAP_ODATA_BASE_URL=         # e.g. https://<sap-host>/<odata-service>
SAP_ODATA_SERVICE=          # logical service name (optional label)
SAP_ODATA_METADATA_URL=     # optional override; defaults to {BASE_URL}/$metadata
SAP_TIMEOUT_SECONDS=15
SAP_AUTH_MODE=NONE          # NONE | BASIC | OAUTH2

# OAuth (only if landscape requires it)
SAP_API_URL=
SAP_CLIENT_ID=
SAP_CLIENT_SECRET=
SAP_COMPANY_ID=

# Entity set mappings — fill after inspecting official $metadata
SAP_ENTITY_PERSON=
SAP_ENTITY_JOB=
SAP_ENTITY_POSITION=
SAP_ENTITY_ORGANIZATION=
SAP_ENTITY_QUALIFICATION=
SAP_ENTITY_APPLICATION=
SAP_ENTITY_LEARNING=
SAP_ENTITY_OPPORTUNITY=
```

## Source modes

| Mode | Meaning |
|------|---------|
| `SIMULATED` | Demo fixtures — no external SAP |
| `NOT_CONNECTED` | LIVE configured but not verified |
| `LIVE` | Metadata verified and OData accessible |
| `ERROR` | Unexpected integration failure |

**LIVE is never inferred from configuration alone.** The backend must successfully fetch and parse `$metadata`.

## Quick start (when URL arrives)

1. Set `DEMO_MODE=false` and `SAP_MODE=LIVE`
2. Set `SAP_ODATA_BASE_URL` to the faculty-provided URL
3. Set `SAP_AUTH_MODE` if authentication is required
4. Run connectivity check:

```bash
python scripts/sap_connectivity_check.py
```

5. Inspect `$metadata` and set entity env vars (`SAP_ENTITY_*`)
6. Re-run connectivity check until entities show `AVAILABLE`
7. Execute a RE:WORK case — intelligence pipeline is unchanged

## Testing connectivity

```bash
# Simulated (default demo)
DEMO_MODE=true python scripts/sap_connectivity_check.py

# Live probe (no secrets printed)
DEMO_MODE=false SAP_MODE=LIVE python scripts/sap_connectivity_check.py
```

API endpoints:

- `GET /api/sap/health` — lightweight health
- `GET /api/sap/diagnostics` — detailed OData status
- `GET /api/sap/trace` — SAP → RE:WORK pipeline trace

## Failure behavior

- Demo mode always uses `SimulatedSAPProvider`
- LIVE failures do **not** silently claim LIVE
- LIVE mode does **not** silently substitute synthetic data
- Partial entity availability is disclosed as partial context

## Security

- Never commit credentials
- Browser never calls SAP directly (`Browser → RE:WORK API → SAP`)
- Authorization headers are redacted in logs

## Unresolved mappings

Entity field mappings remain **PENDING_OFFICIAL_ODATA_METADATA** until the official service contract is inspected. See `docs/SAP_ODATA_FIELD_MAPPING.md`.
