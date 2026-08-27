"""Deterministic simulated SAP SuccessFactors-compatible provider."""

from datetime import datetime, timezone
from typing import Any

from app.adapters.sap.provider import SAPProvider
from app.domain.candidate import CandidateCapability
from app.domain.enums import IntegrationStatus, SourceMode
from app.domain.job import JobProfile
from app.domain.pathway import LearningItem, Opportunity
from app.domain.sap import SAPCapabilityStatus, SAPContext
from app.services.fixture_service import FixtureService


class SimulatedSAPProvider(SAPProvider):
    """Fixture-backed SAP provider. Every result is source_mode=SIMULATED."""

    def __init__(self, fixture_service: FixtureService | None = None) -> None:
        self._fixtures = fixture_service or FixtureService()

    def get_context(self) -> SAPContext:
        return SAPContext(
            source="SAP",
            source_mode=SourceMode.SIMULATED,
            system_name="SuccessFactors-compatible demo environment",
            integration_status=IntegrationStatus.AVAILABLE,
            last_sync=datetime.now(timezone.utc),
            retrieved_entities=[
                "WorkforceContext",
                "SkillsContext",
                "RoleContext",
                "LearningCatalog",
                "OpportunityCatalog",
            ],
            capabilities=[
                SAPCapabilityStatus(
                    name="Workforce context",
                    status=IntegrationStatus.AVAILABLE,
                    source_mode=SourceMode.SIMULATED,
                    last_sync=datetime.now(timezone.utc),
                ),
                SAPCapabilityStatus(
                    name="Skills context",
                    status=IntegrationStatus.AVAILABLE,
                    source_mode=SourceMode.SIMULATED,
                    last_sync=datetime.now(timezone.utc),
                ),
                SAPCapabilityStatus(
                    name="Role context",
                    status=IntegrationStatus.AVAILABLE,
                    source_mode=SourceMode.SIMULATED,
                    last_sync=datetime.now(timezone.utc),
                ),
                SAPCapabilityStatus(
                    name="Learning catalog",
                    status=IntegrationStatus.AVAILABLE,
                    source_mode=SourceMode.SIMULATED,
                    last_sync=datetime.now(timezone.utc),
                ),
                SAPCapabilityStatus(
                    name="Opportunity catalog",
                    status=IntegrationStatus.AVAILABLE,
                    source_mode=SourceMode.SIMULATED,
                    last_sync=datetime.now(timezone.utc),
                ),
            ],
            message="Simulated SAP context — not a live tenant connection.",
        )

    def get_candidate_context(self, candidate_id: str) -> dict[str, Any]:
        data = self._fixtures.get_sap_fixture_data()
        gp = data.get("growth_portfolio", {})
        if gp.get("candidate_id") == candidate_id:
            return {
                "candidate_id": candidate_id,
                "growth_portfolio": gp,
                "source": "SAP",
                "source_mode": SourceMode.SIMULATED.value,
            }
        return {
            "candidate_id": candidate_id,
            "growth_portfolio": None,
            "source": "SAP",
            "source_mode": SourceMode.SIMULATED.value,
            "message": "No employee record — external candidate in demo",
        }

    def get_employee_skills(self, candidate_id: str) -> list[CandidateCapability]:
        # Simulated SAP skills — empty for external candidate Ananya
        if candidate_id == "ananya-sharma":
            return []
        return []

    def get_role_context(self, job_id: str) -> JobProfile | None:
        job = self._fixtures.get_data_analyst_job()
        if job.id == job_id:
            return job
        return None

    def get_learning_items(self) -> list[LearningItem]:
        return self._fixtures.get_sap_learning_items()

    def get_opportunities(self) -> list[Opportunity]:
        return self._fixtures.get_sap_opportunities()
