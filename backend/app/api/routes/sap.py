"""SAP context endpoint."""

from fastapi import APIRouter

from app.adapters.sap import get_sap_provider

router = APIRouter()


@router.get("/context")
def get_sap_context() -> dict:
    provider = get_sap_provider()
    context = provider.get_context()
    return {
        "sap_context": context.model_dump(mode="json"),
        "source_mode": context.source_mode.value,
        "live_connection": False,
        "message": context.message,
    }
