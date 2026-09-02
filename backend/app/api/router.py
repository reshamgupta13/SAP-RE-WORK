"""API route handlers."""

from fastapi import APIRouter

from app.api.routes import cases, catalog, demo, health, learning_plans, reviews, runs, sap, student

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(demo.router, prefix="/demo", tags=["demo"])
api_router.include_router(sap.router, prefix="/sap", tags=["sap"])
api_router.include_router(catalog.router, prefix="/catalog", tags=["catalog"])
api_router.include_router(student.router, prefix="/student", tags=["student"])
api_router.include_router(learning_plans.router, prefix="/learning-plans", tags=["learning-plans"])
api_router.include_router(cases.router, prefix="/cases", tags=["cases"])
api_router.include_router(runs.router, prefix="/runs", tags=["runs"])
api_router.include_router(reviews.router, prefix="/reviews", tags=["reviews"])
