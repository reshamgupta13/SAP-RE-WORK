"""Student workspace — SAP skill CRUD (skillProject integration)."""

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.student_skill_service import StudentSkillService

router = APIRouter()
_service = StudentSkillService()


class SkillPayload(BaseModel):
    SkillId: str | None = None
    SkillName: str | None = None
    Description: str | None = None


class SkillMutateBody(BaseModel):
    payload: dict[str, Any] = Field(default_factory=dict)


@router.get("/connection")
def student_connection() -> dict[str, Any]:
    return _service.connection_info()


@router.post("/get-skills")
def get_skills() -> dict[str, Any]:
    return _service.get_all()


@router.post("/get-skill")
def get_skill(body: SkillMutateBody) -> dict[str, Any]:
    skill_id = body.payload.get("SkillId")
    if not skill_id:
        raise HTTPException(status_code=400, detail="SkillId is required.")
    return _service.get_one(str(skill_id))


@router.post("/create-skill")
def create_skill(body: SkillMutateBody) -> dict[str, Any]:
    return _service.create(body.payload)


@router.post("/update-skill")
def update_skill(body: SkillMutateBody) -> dict[str, Any]:
    return _service.update(body.payload)


@router.post("/delete-skill")
def delete_skill(body: SkillMutateBody) -> dict[str, Any]:
    skill_id = body.payload.get("SkillId")
    if not skill_id:
        raise HTTPException(status_code=400, detail="SkillId is required.")
    return _service.delete(str(skill_id))
