"""API route handlers."""

from fastapi import APIRouter

from app.api.routes import demo, health, sap

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(demo.router, prefix="/demo", tags=["demo"])
api_router.include_router(sap.router, prefix="/sap", tags=["sap"])
