"""Live SAP provider — only when credentials verified."""

from typing import Any

import httpx

from app.adapters.sap.mapper import SAPMapper
from app.adapters.sap.provider import SAPProvider
from app.domain.candidate import CandidateCapability
from app.domain.enums import IntegrationStatus, SourceMode
from app.domain.job import JobProfile
from app.domain.pathway import LearningItem, Opportunity
from app.domain.sap import SAPContext
from app.services.fixture_service import FixtureService


class LiveSAPProvider(SAPProvider):
    """
    Read-only live SAP integration.
    Does not invent endpoints — uses configured base URL when credentials exist.
  Falls back explicitly when connection fails (caller must not hide fallback).
    """

    def __init__(
        self,
        api_url: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
        company_id: str | None = None,
    ) -> None:
        self._api_url = (api_url or "").rstrip("/")
        self._client_id = client_id
        self._client_secret = client_secret
        self._company_id = company_id
        self._mapper = SAPMapper()
        self._verified = False
        self._fallback_fixtures = FixtureService()

    def _authenticate(self) -> str | None:
        if not self._api_url or not self._client_id or not self._client_secret:
            raise NotImplementedError("Live SAP credentials incomplete.")
        # OAuth token exchange — tenant-specific; attempt only when fully configured
        token_url = f"{self._api_url}/oauth/token"
        try:
            with httpx.Client(timeout=15.0) as client:
                resp = client.post(
                    token_url,
                    data={
                        "grant_type": "client_credentials",
                        "client_id": self._client_id,
                        "client_secret": self._client_secret,
                    },
                )
                if resp.status_code == 200:
                    self._verified = True
                    return resp.json().get("access_token")
        except httpx.HTTPError:
            pass
        raise ConnectionError("SAP authentication failed — no verified connection.")

    def _failure_source_mode(self, exc: Exception) -> SourceMode:
        if isinstance(exc, (ConnectionError, NotImplementedError)):
            return SourceMode.NOT_CONNECTED
        return SourceMode.ERROR

    def get_context(self) -> SAPContext:
        try:
            self._authenticate()
            modules = ["WorkforceContext", "SkillsContext"]
            return self._mapper.map_context(
                system_name=self._api_url,
                source_mode=SourceMode.LIVE,
                modules=modules,
                status=IntegrationStatus.AVAILABLE,
                message="Live SAP connected (token acquired).",
            )
        except Exception as exc:
            return self._mapper.map_context(
                system_name="SAP (connection failed)",
                source_mode=self._failure_source_mode(exc),
                modules=[],
                status=IntegrationStatus.UNAVAILABLE,
                message=str(exc),
            )

    def get_candidate_context(self, candidate_id: str) -> dict[str, Any]:
        raise NotImplementedError(
            "Live workforce read not verified for this tenant — use SIMULATED mode."
        )

    def get_employee_skills(self, candidate_id: str) -> list[CandidateCapability]:
        raise NotImplementedError("Live skills read not verified for this tenant.")

    def get_role_context(self, job_id: str) -> JobProfile | None:
        raise NotImplementedError("Live role read not verified for this tenant.")

    def get_learning_items(self) -> list[LearningItem]:
        raise NotImplementedError("Live learning catalog not verified for this tenant.")

    def get_opportunities(self) -> list[Opportunity]:
        raise NotImplementedError("Live opportunities not verified for this tenant.")

    def update_skill_progress(
        self,
        candidate_id: str,
        skill_id: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        raise NotImplementedError("SAP write-back disabled until read integration validated.")
