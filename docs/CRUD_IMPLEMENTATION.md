# CRUD implementation

Gateway alignment (faculty CRUD reference):

| HTTP | DPC_EXT | Client method |
| --- | --- | --- |
| GET collection | GET_ENTITYSET | `get_collection` |
| GET by key | GET_ENTITY | `get_by_key` |
| POST | CREATE_ENTITY | `create_entity` |
| PUT / MERGE | UPDATE_ENTITY | `update_entity` (MERGE default) |
| DELETE | DELETE_ENTITY | `delete_entity` |

## CSRF

Write operations:

1. GET service root (or metadata) with `X-CSRF-Token: Fetch`
2. Store token + session cookies on the backend client
3. Send token on POST/PUT/MERGE/DELETE
4. Retry once if Gateway returns a CSRF failure

GET does not require a write token. Tokens are never placed in browser state.

## Product mutations

Frontend → `/api/catalog/...` → `SAPCatalogService.mutate` → OData. Success means SAP changed, then the UI reloads.

Priority (when the service exposes the verb):

1. ZREWORK_USER read/create/update
2. ZREWORK_PERSKILL read/create/update
3. ZREWORK_JOB read/create/update
4. ZREWORK_JOB_SKIL read/create/update
5. ZREWORK_SKILL read/create/update
6. ZREWORK_ORGANIZA read
7. ZREWORK_HR read / update if appropriate

DELETE is only surfaced if the service actually allows it.

If Gateway returns 405/501: **"Write operation is not available in the current SAP service."**

## Conflicts

Before update/delete the current record is fetched. 409/412 are mapped to a refresh-required message. Silent overwrite is not allowed.

## Readable errors

| Status | User message |
| --- | --- |
| 400 | SAP rejected the request because the payload was invalid. |
| 401 | SAP authentication failed. |
| 403 | SAP denied this operation. |
| 404 | SAP rejected the request because the record no longer exists. |
| 409 | SAP reported a conflict. Refresh the record and try again. |
| 412 | The record changed since it was loaded. Refresh before saving. |
| 429 | SAP is rate-limiting requests. Try again shortly. |
| 500+ | SAP encountered a server error. |

Technical exception text stays in logs/trace, not as the primary UI copy.
