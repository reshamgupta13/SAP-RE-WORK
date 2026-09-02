"""RE:WORK FastAPI application entrypoint."""

import logging
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.core.config import get_settings
from app.core.paths import resolve_fixtures_dir

logger = logging.getLogger(__name__)

settings = get_settings()

_DEV_CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
]


def _cors_origins() -> list[str]:
    if settings.cors_origins:
        return [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]
    if settings.environment.lower() == "development":
        return _DEV_CORS_ORIGINS
    return []


def _configure_logging() -> None:
    level = logging.DEBUG if settings.debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )


_configure_logging()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="AI-Powered Inclusive Workforce Recomposition Engine",
)

_cors = _cors_origins()
if _cors:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_cors,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    logger.warning("No CORS origins configured — browser clients may be blocked in production.")

app.include_router(api_router, prefix="/api")


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred. Please try again later.",
            }
        },
    )


@app.on_event("startup")
def on_startup() -> None:
    fixtures = resolve_fixtures_dir(settings.fixtures_dir)
    logger.info(
        "Starting %s (environment=%s, sap_mode=%s, persistence=%s, fixtures=%s, cors=%s)",
        settings.app_name,
        settings.environment,
        settings.sap_mode,
        settings.persistence_mode,
        fixtures,
        _cors or "none",
    )
    if not fixtures.exists():
        logger.warning("Fixtures directory not found at %s", fixtures)


@app.get("/")
def root() -> dict:
    return {"service": settings.app_name, "docs": "/docs", "health": "/health"}


@app.get("/health")
def root_health() -> dict:
    return {"status": "ok"}


@app.get("/health/ready")
def root_health_ready() -> dict:
    fixtures = resolve_fixtures_dir(settings.fixtures_dir)
    checks: dict[str, str] = {
        "api": "ok",
        "fixtures": "ok" if fixtures.exists() else "missing",
    }
    ready = checks["fixtures"] == "ok"
    return {
        "status": "ready" if ready else "degraded",
        "checks": checks,
        "sap_mode": settings.sap_mode,
        "persistence_mode": settings.persistence_mode,
    }
