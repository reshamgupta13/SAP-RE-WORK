"""Candidate Intelligence Agent — evidence-backed capability extraction."""

from datetime import date

from app.adapters.llm.base import LLMProvider
from app.adapters.llm.fallback import DeterministicFallbackProvider
from app.agents.schemas import CandidateCapabilityExtract, CandidateIntelligenceOutput
from app.domain.candidate import CandidateCapability, CandidateEvidence, CandidateProfile
from app.domain.enums import (
    CapabilityVerificationStatus,
    EngineMode,
    InferenceStatus,
    RecencyStatus,
    SourceMode,
)
from app.domain.sap import SAPContext
from app.services.confidence import apply_confidence_to_capability, compute_recency_status
from app.services.fixture_service import FixtureService


class CandidateIntelligenceAgent:
    """Extracts what the candidate can evidence — not hiring recommendations."""

    def __init__(
        self,
        llm_provider: LLMProvider,
        fixture_service: FixtureService | None = None,
    ) -> None:
        self._llm = llm_provider
        self._fixtures = fixture_service or FixtureService()

    @property
    def engine_mode(self) -> EngineMode:
        return self._llm.engine_mode

    def run(
        self,
        profile: CandidateProfile,
        evidence: list[CandidateEvidence],
        sap_context: SAPContext | None = None,
        sap_skills: list[dict] | None = None,
    ) -> tuple[list[CandidateCapability], str]:
        evidence_by_id = {e.id: e for e in evidence}
        fallback_payload = self._build_fallback_output(profile, evidence, sap_skills)

        if isinstance(self._llm, DeterministicFallbackProvider):
            output = self._llm.generate_structured(
                prompt="fallback",
                schema=CandidateIntelligenceOutput,
                context={"fallback_payload": fallback_payload.model_dump()},
            )
        else:
            try:
                prompt = self._build_prompt(profile, evidence, sap_context, sap_skills)
                output = self._llm.generate_structured(
                    prompt=prompt,
                    schema=CandidateIntelligenceOutput,
                    context={"system_instruction": self._system_instruction()},
                )
            except Exception:
                fallback = DeterministicFallbackProvider()
                output = fallback.generate_structured(
                    prompt="fallback",
                    schema=CandidateIntelligenceOutput,
                    context={"fallback_payload": fallback_payload.model_dump()},
                )

        capabilities = self._to_domain(profile, output, evidence_by_id)
        if not capabilities and sap_skills:
            capabilities = self._capabilities_from_sap_records(profile, sap_skills, evidence_by_id)
        sap_note = ""
        if sap_context:
            sap_note = f" SAP context ({sap_context.source_mode.value}) consulted."
        if sap_skills:
            sap_note += f" {len(sap_skills)} SAP skill records on file."
        rationale = (output.summary_rationale or "Capabilities derived from supplied evidence.") + sap_note
        return capabilities, rationale

    def _system_instruction(self) -> str:
        return (
            "You are RE:WORK Candidate Intelligence. Use ONLY supplied candidate data. "
            "Do not fabricate skills. Distinguish explicit, inferred, and transferable capabilities. "
            "Every capability must cite evidence IDs. SELF_REPORTED evidence cannot be VERIFIED. "
            "Return JSON only."
        )

    def _build_prompt(
        self,
        profile: CandidateProfile,
        evidence: list[CandidateEvidence],
        sap_context: SAPContext | None,
        sap_skills: list[dict] | None = None,
    ) -> str:
        sap_note = ""
        if sap_context:
            sap_note = (
                f"Workforce context source_mode={sap_context.source_mode.value}. "
                "Do not claim SAP facts unless present in context."
            )
        if sap_skills:
            sap_note += f" SAP skills on record: {len(sap_skills)} (use only as supplementary context)."
        evidence_lines = [
            f"- id={e.id} type={e.type.value} verification={e.verification_status.value}: {e.description}"
            for e in evidence
        ]
        return (
            f"Candidate: {profile.display_name} ({profile.id}), location={profile.location}\n"
            f"Notes: {profile.notes or 'none'}\n"
            f"{sap_note}\n"
            "Evidence:\n"
            + "\n".join(evidence_lines)
        )

    def _build_fallback_output(
        self,
        profile: CandidateProfile,
        evidence: list[CandidateEvidence],
        sap_skills: list[dict] | None = None,
    ) -> CandidateIntelligenceOutput:
        if profile.id == "ananya-sharma":
            bundle = self._fixtures.get_ananya_bundle()
            extracts: list[CandidateCapabilityExtract] = []
            for cap in bundle["capabilities"]:
                verification = CapabilityVerificationStatus.UNVERIFIED
                if cap.evidence_refs:
                    ev = next((e for e in evidence if e.id in cap.evidence_refs), None)
                    if ev and ev.type.value == "SELF_REPORTED":
                        verification = CapabilityVerificationStatus.SELF_REPORTED
                    elif ev and ev.verification_status.value == "VERIFIED":
                        verification = CapabilityVerificationStatus.VERIFIED
                    elif ev:
                        verification = CapabilityVerificationStatus.SUPPORTED
                recency = compute_recency_status(cap.recency)
                extracts.append(
                    CandidateCapabilityExtract(
                        skill_id=cap.skill_id,
                        label=cap.label,
                        proficiency=cap.proficiency,
                        raw_confidence=cap.confidence,
                        evidence_refs=cap.evidence_refs,
                        inference_status=cap.inference_status,
                        verification_status=verification.value,
                        recency_status=recency.value,
                        rationale=f"Detected {cap.label} from demo fixture evidence.",
                    )
                )
            skill_ids = {e.skill_id for e in extracts}
            if "data_analysis" not in skill_ids and any(
                any(
                    k in f"{e.title} {e.description}".lower()
                    for k in ("mis", "analytics", "reporting", "analyst", "business analyst")
                )
                for e in evidence
            ):
                extracts.append(
                    CandidateCapabilityExtract(
                        skill_id="data_analysis",
                        label="Data Analysis",
                        proficiency=0.58,
                        raw_confidence=0.65,
                        evidence_refs=["ev-ananya-project-mis"],
                        inference_status=InferenceStatus.INFERRED.value,
                        verification_status=CapabilityVerificationStatus.SUPPORTED.value,
                        recency_status=compute_recency_status(date(2023, 2, 1)).value,
                        rationale="Inferred data analysis from MIS analytics project evidence.",
                    )
                )
            if "reporting" not in skill_ids:
                extracts.append(
                    CandidateCapabilityExtract(
                        skill_id="reporting",
                        label="Reporting",
                        proficiency=0.6,
                        raw_confidence=0.7,
                        evidence_refs=["ev-ananya-project-mis", "ev-ananya-work-history"],
                        inference_status=InferenceStatus.INFERRED.value,
                        verification_status=CapabilityVerificationStatus.SUPPORTED.value,
                        recency_status=compute_recency_status(date(2023, 3, 1)).value,
                        rationale="Inferred reporting from MIS and work history evidence.",
                    )
                )
            return CandidateIntelligenceOutput(
                capabilities=extracts,
                summary_rationale="Demo fallback: capabilities from Ananya fixture evidence.",
            )

        if sap_skills:
            sap_output = self._sap_skills_fallback(profile, evidence, sap_skills)
            if sap_output.capabilities:
                return sap_output

        # Generic minimal fallback from evidence keywords
        return self._generic_evidence_fallback(profile, evidence)

    def _sap_skills_fallback(
        self,
        profile: CandidateProfile,
        evidence: list[CandidateEvidence],
        sap_skills: list[dict],
    ) -> CandidateIntelligenceOutput:
        from app.agents.schemas import CandidateCapabilityExtract

        evidence_by_id = {e.id: e for e in evidence}
        extracts: list[CandidateCapabilityExtract] = []
        for row in sap_skills:
            raw_skill_id = str(row.get("skill_id") or row.get("SKILL_ID") or "")
            skill_id = raw_skill_id.lower()
            if not skill_id:
                continue
            label = str(row.get("label") or row.get("skill_name") or row.get("SKILL_NAME") or skill_id)
            proficiency = row.get("proficiency")
            if proficiency is None:
                continue
            try:
                proficiency_f = float(proficiency)
            except (TypeError, ValueError):
                continue
            evidence_refs = list(row.get("evidence_refs") or [])
            if not evidence_refs and raw_skill_id:
                evidence_refs = [f"sap-evidence-{profile.id}-{raw_skill_id}"]
            ev = evidence_by_id.get(evidence_refs[0]) if evidence_refs else None
            verification = CapabilityVerificationStatus.UNVERIFIED
            if ev and ev.type.value == "SELF_REPORTED":
                verification = CapabilityVerificationStatus.SELF_REPORTED
            elif ev and ev.verification_status.value == "VERIFIED":
                verification = CapabilityVerificationStatus.VERIFIED
            elif ev:
                verification = CapabilityVerificationStatus.SUPPORTED
            recency = (
                compute_recency_status(ev.occurred_on)
                if ev and ev.occurred_on
                else RecencyStatus.UNKNOWN
            )
            extracts.append(
                CandidateCapabilityExtract(
                    skill_id=skill_id,
                    label=label,
                    proficiency=proficiency_f,
                    raw_confidence=float(row.get("confidence") or row.get("raw_confidence") or 0.65),
                    evidence_refs=evidence_refs,
                    inference_status=InferenceStatus.EXPLICIT.value,
                    verification_status=verification.value,
                    recency_status=recency.value if hasattr(recency, "value") else str(recency),
                    rationale=f"SAP person-skill record for {label}.",
                )
            )
        return CandidateIntelligenceOutput(
            capabilities=extracts,
            summary_rationale="Capabilities derived from SAP person-skill records.",
        )

    def _capabilities_from_sap_records(
        self,
        profile: CandidateProfile,
        sap_skills: list[dict],
        evidence_by_id: dict[str, CandidateEvidence],
    ) -> list[CandidateCapability]:
        output = self._sap_skills_fallback(profile, list(evidence_by_id.values()), sap_skills)
        return self._to_domain(profile, output, evidence_by_id)

    def _generic_evidence_fallback(
        self,
        profile: CandidateProfile,
        evidence: list[CandidateEvidence],
    ) -> CandidateIntelligenceOutput:
        from app.agents.schemas import CandidateCapabilityExtract

        keyword_map = {
            "java": ("skill0001", "Java"),
            "odata": ("skill0002", "OData"),
            "sap": ("skill0003", "SAP"),
            "hana": ("skill0004", "HANA"),
            "sql": ("skill0005", "SQL"),
            "excel": ("excel", "Excel"),
            "power bi": ("power_bi", "Power BI"),
            "stakeholder": ("communication", "Stakeholder communication"),
        }
        found: dict[str, CandidateCapabilityExtract] = {}
        for ev in evidence:
            text = f"{ev.title} {ev.description}".lower()
            for key, (skill_id, label) in keyword_map.items():
                if key in text and skill_id not in found:
                    verification = (
                        CapabilityVerificationStatus.SELF_REPORTED
                        if ev.type.value == "SELF_REPORTED"
                        else CapabilityVerificationStatus.SUPPORTED
                    )
                    found[skill_id] = CandidateCapabilityExtract(
                        skill_id=skill_id,
                        label=label,
                        proficiency=0.45 if verification == CapabilityVerificationStatus.SELF_REPORTED else 0.55,
                        raw_confidence=ev.confidence,
                        evidence_refs=[ev.id],
                        inference_status=InferenceStatus.EXPLICIT.value,
                        verification_status=verification.value,
                        recency_status=compute_recency_status(ev.occurred_on).value,
                        rationale=f"Detected {label} from evidence {ev.id}.",
                    )
        return CandidateIntelligenceOutput(
            capabilities=list(found.values()),
            summary_rationale="Generic evidence keyword fallback.",
        )

    def _safe_recency_status(self, value: str | None) -> RecencyStatus:
        if not value:
            return RecencyStatus.UNKNOWN
        normalized = str(value).strip().upper().replace(" ", "_")
        try:
            return RecencyStatus(normalized)
        except ValueError:
            return RecencyStatus.UNKNOWN

    def _safe_verification_status(self, value: str | None) -> CapabilityVerificationStatus:
        if not value:
            return CapabilityVerificationStatus.UNVERIFIED
        normalized = str(value).strip().upper().replace(" ", "_")
        try:
            return CapabilityVerificationStatus(normalized)
        except ValueError:
            return CapabilityVerificationStatus.UNVERIFIED

    def _to_domain(
        self,
        profile: CandidateProfile,
        output: CandidateIntelligenceOutput,
        evidence_by_id: dict[str, CandidateEvidence],
    ) -> list[CandidateCapability]:
        capabilities: list[CandidateCapability] = []
        for idx, item in enumerate(output.capabilities):
            cap_id = f"cap-{profile.id}-{item.skill_id}"
            recency_date = None
            for ref in item.evidence_refs:
                ev = evidence_by_id.get(ref)
                if ev and ev.occurred_on:
                    recency_date = ev.occurred_on
                    break
            cap = CandidateCapability(
                id=cap_id,
                candidate_id=profile.id,
                skill_id=item.skill_id,
                label=item.label,
                proficiency=item.proficiency,
                confidence=item.raw_confidence,
                evidence_refs=item.evidence_refs,
                recency=recency_date,
                source="REWORK",
                source_mode=SourceMode.SYNTHETIC,
                inference_status=item.inference_status,
                verification_status=self._safe_verification_status(item.verification_status),
                recency_status=self._safe_recency_status(item.recency_status),
                raw_confidence=item.raw_confidence,
                rationale=item.rationale,
            )
            capabilities.append(apply_confidence_to_capability(cap, evidence_by_id))
        return capabilities
