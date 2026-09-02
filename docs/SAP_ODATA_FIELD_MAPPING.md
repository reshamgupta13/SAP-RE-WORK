# SAP OData Field Mapping

## Status: PENDING_OFFICIAL_ODATA_METADATA

This document will be completed once the official SAP OData `$metadata` and sample responses are available from faculty.

## Business domain → canonical model

| SAP business concept | Canonical RE:WORK model | Entity env var | Status |
|---------------------|------------------------|----------------|--------|
| Person / Employee | `CandidateProfile` context | `SAP_ENTITY_PERSON` | PENDING |
| Job | `JobProfile` | `SAP_ENTITY_JOB` | PENDING |
| Position | Role context | `SAP_ENTITY_POSITION` | PENDING |
| Organizational Unit | Org context | `SAP_ENTITY_ORGANIZATION` | PENDING |
| Qualification / Skill | `CandidateCapability` (SAP_RECORDED) | `SAP_ENTITY_QUALIFICATION` | PENDING |
| Applicant / Application | Application context | `SAP_ENTITY_APPLICATION` | PENDING |
| Learning / Training | `LearningItem` | `SAP_ENTITY_LEARNING` | PENDING |
| Opportunity | `Opportunity` | `SAP_ENTITY_OPPORTUNITY` | PENDING |

## Hypothetical field hints (for mapper development only)

These are **not** official SAP field names. The mapper uses flexible key lookup until the real contract is known:

### Person → CandidateProfile context

| OData field (hypothetical) | Canonical field |
|---------------------------|-----------------|
| `userId` / `personIdExternal` / `id` | `employee_id` |
| `displayName` / `defaultFullName` | `display_name` |
| `department` | `department` |
| `jobTitle` / `positionTitle` | `role_title` |

### Qualification → CandidateCapability

| OData field (hypothetical) | Canonical field |
|---------------------------|-----------------|
| `skillId` / `name` | `skill_id` / `label` |
| `proficiencyLevel` | `proficiency` (normalized 0–1) |

### Job → JobProfile

| OData field (hypothetical) | Canonical field |
|---------------------------|-----------------|
| `jobCode` / `id` | `id` |
| `title` / `jobTitle` | `title` |
| `description` / `jobDescription` | `raw_text` |

## Steps when metadata arrives

1. Save `$metadata` to `fixtures/sap/odata/metadata.xml`
2. Add sample JSON responses per entity
3. Set `SAP_ENTITY_*` env vars to actual EntitySet names
4. Update this document with verified field mappings
5. Add contract tests using fixtures
6. Run `python scripts/sap_connectivity_check.py`

## Evidence grade

| SAP data type | Evidence type in RE:WORK |
|--------------|-------------------------|
| Recorded qualification | `SAP_RECORDED` |
| Contextual org/role data | Context (not evidence-grade) |
| Missing field | No fabrication |
