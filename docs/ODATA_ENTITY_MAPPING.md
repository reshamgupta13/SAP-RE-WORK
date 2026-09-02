# OData entity mapping

Names below are **not** claimed as the official faculty contract until `$metadata` is inspected against a real service URL.

The registry lives in `backend/app/adapters/sap/seven_table_registry.py`.

## Intended mapping

| SAP table | Canonical model | Config variable | Discovery hint |
| --- | --- | --- | --- |
| ZREWORK_USER | CandidateProfile | `SAP_ENTITY_USER` | `ZREWORK_USER` |
| ZREWORK_SKILL | Skill | `SAP_ENTITY_SKILL` | `ZREWORK_SKILL` |
| ZREWORK_PERSKILL | CandidateCapability | `SAP_ENTITY_PERSON_SKILL` | `ZREWORK_PERSKILL` |
| ZREWORK_JOB | JobProfile | `SAP_ENTITY_JOB` | `ZREWORK_JOB` (does not match `JOB_SKIL`) |
| ZREWORK_JOB_SKIL | JobCapability | `SAP_ENTITY_JOB_SKILL` | `ZREWORK_JOB_SKIL` |
| ZREWORK_ORGANIZA | Organization | `SAP_ENTITY_ORGANIZATION` | `ZREWORK_ORGANIZA` |
| ZREWORK_HR | HRReviewer | `SAP_ENTITY_HR` | `ZREWORK_HR` |

Entity set names are taken from configuration or from EntitySets that actually appear in `$metadata`. The application does not invent live names such as faculty sample `Z_SUG_STUDENT_SRV`.

Typical SEGW pattern after DDIC import: table `ZREWORK_USER` → entity type `ZREWORK_USER` → entity set `ZREWORK_USERSet`. That pattern is used only when the set is present in metadata.

## Keys

Key property names are parsed from `$metadata` (`EntityType/Key/PropertyRef`). Until a live document is verified, do not assume `USER_ID` vs `UserId`.

## Property aliases

`SAPMapper` accepts DDIC-style names (`USER_ID`, `SKILL_NAME`, `IS_MANDATORY`) and older SuccessFactors-style names. Canonical models never expose raw SAP property names above the mapper.

## Proficiency

Documented normalization only:

- `0..1` used as-is
- `1..5` divided by 5
- `>5..100` divided by 100
- labels `NOVICE|BEGINNER|BASIC|INTERMEDIATE|ADVANCED|EXPERT`

Anything else is **not scored**. The UI must say insufficient evidence, not `0`.

## Current verification status

In this repository checkout, official OData `$metadata` has **not** been retrieved from a live SAP system. Entity set cells remain `PENDING_OFFICIAL_ODATA_METADATA` until smoke/diagnostics report `AVAILABLE`.
