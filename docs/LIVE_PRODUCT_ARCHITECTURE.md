# Live product architecture

```
SAP database
    → SEGW / OData
    → SAPODataClient (backend only)
    → SAP DTO
    → SAPMapper
    → canonical RE:WORK model
    → intelligence (LangGraph) + product APIs
    → UI
    → human HR decision
```

No React component computes diagnosis, viability, or gap state.

## Product vs demo

- Product: `/workspace`, `/candidate`, `/opportunities`, `/employer`, `/hr-review?caseId=`, `/control-room?caseId=`
- Product APIs: `/api/catalog/*`, `POST /api/cases` (then execute)
- Demo/test only: `/api/demo/*`, Ananya fixtures, golden replay, `case-ananya-finale`

The main UI does not call `/api/demo/control-room`.

## Case flow

1. User selects SAP candidate + SAP job in Workspace
2. `POST /api/cases` with those keys and `execute_until=FINALE`
3. For non-Ananya cases the graph runs `RunMode.LIVE_CASE` (diagnosis → pathway → explainability, no Ananya proof auto-pass)
4. Control Room and HR Review load `/api/cases/{id}/control-room`

## Source labels in the UI

**From SAP:** profile, recorded skill, evidence text, job, requirement, organization, HR identity.

**RE:WORK:** capability interpretation, gap diagnosis, pathway, proof task, viability, explanation.

## Security

- SAP base URL is configuration-only (no caller-supplied URLs → SSRF)
- Credentials stay in backend env
- OData `$filter/$select/$top` built only by the backend
- CSRF tokens stay on the server-side OData client
