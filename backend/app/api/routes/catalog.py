"""Product catalog APIs — SAP seven-table data only. No demo fixtures."""

from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.services.sap_catalog_service import SAPCatalogService

router = APIRouter()
_catalog = SAPCatalogService()


class MutateRequest(BaseModel):
    payload: dict[str, Any] = Field(default_factory=dict)


@router.get("/health")
def catalog_health() -> dict[str, Any]:
    return _catalog.connection_state()


@router.get("/trace")
def catalog_trace() -> dict[str, Any]:
    state = _catalog.connection_state()
    return {
        "source_mode": state.get("source_mode"),
        "live_verified": state.get("live_verified"),
        "access_plan": state.get("access_plan"),
        "entity_status": state.get("entity_status"),
        "traces": _catalog.traces(),
        "message": state.get("message"),
    }


@router.get("/candidates")
def list_candidates(q: str | None = Query(default=None)) -> dict[str, Any]:
    return _catalog.list_candidates(search=q)


@router.get("/candidates/{user_id}")
def get_candidate(user_id: str) -> dict[str, Any]:
    payload = _catalog.get_candidate(user_id)
    if payload.get("candidate") is None and payload.get("live_verified"):
        raise HTTPException(status_code=404, detail=payload.get("message") or "Candidate not found")
    return payload


@router.post("/candidates")
def create_candidate(body: MutateRequest) -> dict[str, Any]:
    result = _catalog.mutate("user", "create", payload=body.payload)
    if not result.get("ok"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result


@router.put("/candidates/{user_id}")
def update_candidate(user_id: str, body: MutateRequest) -> dict[str, Any]:
    result = _catalog.mutate("user", "update", key=user_id, payload=body.payload)
    if not result.get("ok"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result


@router.get("/skills")
def list_skills(q: str | None = Query(default=None)) -> dict[str, Any]:
    data = _catalog.list_skills()
    if q:
        needle = q.lower()
        data["items"] = [
            i
            for i in data.get("items", [])
            if needle in " ".join(str(i.get(k) or "") for k in ("skill_id", "skill_name")).lower()
        ]
        data["count"] = len(data["items"])
    return data


@router.post("/skills")
def create_skill(body: MutateRequest) -> dict[str, Any]:
    result = _catalog.mutate("skill", "create", payload=body.payload)
    if not result.get("ok"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result


@router.put("/skills/{skill_id}")
def update_skill(skill_id: str, body: MutateRequest) -> dict[str, Any]:
    result = _catalog.mutate("skill", "update", key=skill_id, payload=body.payload)
    if not result.get("ok"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result


@router.post("/candidates/{user_id}/skills")
def add_person_skill(user_id: str, body: MutateRequest) -> dict[str, Any]:
    payload = {"USER_ID": user_id, **body.payload}
    result = _catalog.mutate("person_skill", "create", payload=payload)
    if not result.get("ok"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result


@router.put("/candidates/{user_id}/skills/{skill_id}")
def update_person_skill(user_id: str, skill_id: str, body: MutateRequest) -> dict[str, Any]:
    result = _catalog.mutate("person_skill", "update", key=skill_id, payload={"USER_ID": user_id, **body.payload})
    if not result.get("ok"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result


@router.get("/jobs")
def list_jobs(q: str | None = Query(default=None)) -> dict[str, Any]:
    return _catalog.list_jobs(search=q)


@router.get("/jobs/{job_id}")
def get_job(job_id: str) -> dict[str, Any]:
    payload = _catalog.get_job(job_id)
    if payload.get("job") is None and payload.get("live_verified"):
        raise HTTPException(status_code=404, detail=payload.get("message") or "Job not found")
    return payload


@router.post("/jobs")
def create_job(body: MutateRequest) -> dict[str, Any]:
    result = _catalog.mutate("job", "create", payload=body.payload)
    if not result.get("ok"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result


@router.put("/jobs/{job_id}")
def update_job(job_id: str, body: MutateRequest) -> dict[str, Any]:
    result = _catalog.mutate("job", "update", key=job_id, payload=body.payload)
    if not result.get("ok"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result


@router.post("/jobs/{job_id}/skills")
def add_job_skill(job_id: str, body: MutateRequest) -> dict[str, Any]:
    result = _catalog.mutate("job_skill", "create", payload={"JOB_ID": job_id, **body.payload})
    if not result.get("ok"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result


@router.put("/jobs/{job_id}/skills/{skill_id}")
def update_job_skill(job_id: str, skill_id: str, body: MutateRequest) -> dict[str, Any]:
    result = _catalog.mutate(
        "job_skill",
        "update",
        key=skill_id,
        payload={"JOB_ID": job_id, **body.payload},
    )
    if not result.get("ok"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result


@router.get("/organizations")
def list_organizations(q: str | None = Query(default=None)) -> dict[str, Any]:
    return _catalog.list_organizations(search=q)


@router.get("/hr")
def list_hr(q: str | None = Query(default=None)) -> dict[str, Any]:
    return _catalog.list_hr(search=q)


@router.put("/hr/{hr_id}")
def update_hr(hr_id: str, body: MutateRequest) -> dict[str, Any]:
    result = _catalog.mutate("hr", "update", key=hr_id, payload=body.payload)
    if not result.get("ok"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result
