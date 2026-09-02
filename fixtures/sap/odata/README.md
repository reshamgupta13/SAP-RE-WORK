# SAP OData Contract Fixtures

This directory holds **contract test fixtures** for the official SAP OData service.

## Status: PENDING_OFFICIAL_ODATA_METADATA

Do **not** invent final entity schemas. When faculty provides the official OData URL:

1. Fetch `$metadata` and save as `metadata.xml`
2. Add sample entity responses as JSON files (e.g. `person.json`, `job.json`)
3. Update entity set env vars in `.env` (see `docs/SAP_ODATA_CONFIGURATION.md`)
4. Run `python scripts/sap_connectivity_check.py`

## Expected files (when contract is known)

| File | Purpose |
|------|---------|
| `metadata.xml` | Official `$metadata` document |
| `person.json` | Sample Person/Employee collection response |
| `job.json` | Sample Job collection response |
| `qualification.json` | Sample Qualification/Skill response |
| `organization.json` | Sample Org Unit response |
| `learning.json` | Sample Learning/Training response |

## Usage in tests

Tests mock HTTP and load fixtures from this directory. No real SAP connection required for CI.
