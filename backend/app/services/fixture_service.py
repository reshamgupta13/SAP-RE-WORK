"""Load and validate fixture data."""

from pathlib import Path
from typing import Any

from pydantic import TypeAdapter

from app.core.config import get_settings
from app.domain.candidate import CandidateCapability, CandidateEvidence, CandidateProfile
from app.domain.job import JobProfile
from app.domain.pathway import LearningItem, Opportunity


class FixtureService:
    def __init__(self, fixtures_dir: Path | None = None) -> None:
        settings = get_settings()
        base = fixtures_dir or Path(__file__).resolve().parents[3] / "fixtures"
        if not base.exists():
            # When running from backend/, fixtures are one level up
            base = Path(settings.fixtures_dir)
            if not base.is_absolute():
                base = Path(__file__).resolve().parents[3] / "fixtures"
        self.fixtures_dir = base

    def _read_json(self, relative: str) -> dict[str, Any]:
        path = self.fixtures_dir / relative
        if not path.exists():
            raise FileNotFoundError(f"Fixture not found: {path}")
        import json

        return json.loads(path.read_text(encoding="utf-8"))

    def get_ananya_bundle(self) -> dict[str, Any]:
        data = self._read_json("candidates/ananya.json")
        profile = CandidateProfile.model_validate(
            {k: v for k, v in data.items() if k not in ("evidence", "capabilities")}
        )
        evidence = TypeAdapter(list[CandidateEvidence]).validate_python(data.get("evidence", []))
        capabilities = TypeAdapter(list[CandidateCapability]).validate_python(
            data.get("capabilities", [])
        )
        return {
            "profile": profile,
            "evidence": evidence,
            "capabilities": capabilities,
        }

    def get_data_analyst_job(self) -> JobProfile:
        data = self._read_json("jobs/data_analyst.json")
        return JobProfile.model_validate(data)

    def list_demo_candidates(self) -> list[CandidateProfile]:
        bundle = self.get_ananya_bundle()
        return [bundle["profile"]]

    def list_demo_jobs(self) -> list[JobProfile]:
        return [self.get_data_analyst_job()]

    def get_sap_fixture_data(self) -> dict[str, Any]:
        return self._read_json("sap/simulated_context.json")

    def get_sap_learning_items(self) -> list[LearningItem]:
        data = self.get_sap_fixture_data()
        return TypeAdapter(list[LearningItem]).validate_python(data.get("learning_items", []))

    def get_sap_opportunities(self) -> list[Opportunity]:
        data = self.get_sap_fixture_data()
        return TypeAdapter(list[Opportunity]).validate_python(data.get("opportunities", []))
