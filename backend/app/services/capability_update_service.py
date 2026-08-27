"""Apply capability updates after successful proof-of-skill."""

from app.domain.candidate import CandidateCapability, CandidateEvidence
from app.domain.enums import (
    CapabilityVerificationStatus,
    EvidenceType,
    InferenceStatus,
    RecencyStatus,
    SourceMode,
    VerificationStatus,
)
from app.domain.pathway import CapabilityUpdateEvent, ProofEvidence, ProofOfSkillResult


class CapabilityUpdateService:
    """Update candidate capabilities from verified proof — preserves historical evidence."""

    def apply_proof_result(
        self,
        candidate_capabilities: list[CandidateCapability],
        proof_result: ProofOfSkillResult,
        proof_evidence: ProofEvidence,
        required_proficiency: float,
        run_id: str | None = None,
    ) -> tuple[list[CandidateCapability], CapabilityUpdateEvent | None, CandidateEvidence | None]:
        if proof_result.result.value != "PASSED":
            return candidate_capabilities, None, None

        skill_id = proof_result.skill_id
        existing = next((c for c in candidate_capabilities if c.skill_id == skill_id), None)
        old_level = existing.proficiency if existing else 0.0

        gap_to_required = max(0.0, required_proficiency - old_level)
        new_level = round(old_level + (proof_result.total * gap_to_required), 2)
        if proof_result.total >= 0.7:
            new_level = max(new_level, required_proficiency)
        new_level = round(min(max(new_level, 0.0), 1.0), 2)

        evidence_id = f"ev-proof-{proof_result.id}"
        new_evidence = CandidateEvidence(
            id=evidence_id,
            candidate_id=proof_result.candidate_id,
            type=EvidenceType.ASSESSMENT,
            title=f"Proof-of-skill: {skill_id.replace('_', ' ')}",
            description=(
                f"Structured proof-of-skill assessment passed (score {proof_result.total:.2f}). "
                f"{'DEMO synthetic proof.' if proof_result.is_demo else ''}"
            ),
            source="REWORK",
            source_mode=SourceMode.SYNTHETIC if proof_result.is_demo else SourceMode.USER_PROVIDED,
            verification_status=VerificationStatus.VERIFIED,
            confidence=proof_result.total,
        )

        if existing:
            updated_cap = existing.model_copy(
                update={
                    "proficiency": new_level,
                    "confidence": proof_result.total,
                    "evidence_refs": list(dict.fromkeys(existing.evidence_refs + [evidence_id])),
                    "verification_status": CapabilityVerificationStatus.VERIFIED_BY_ASSESSMENT,
                    "recency_status": RecencyStatus.RECENT,
                    "inference_status": InferenceStatus.VERIFIED,
                    "system_confidence": proof_result.total,
                    "rationale": "Capability refreshed via successful proof-of-skill assessment.",
                }
            )
            caps = [c if c.skill_id != skill_id else updated_cap for c in candidate_capabilities]
        else:
            new_cap = CandidateCapability(
                id=f"cap-{proof_result.candidate_id}-{skill_id}",
                candidate_id=proof_result.candidate_id,
                skill_id=skill_id,
                label=skill_id.replace("_", " ").title(),
                proficiency=new_level,
                confidence=proof_result.total,
                evidence_refs=[evidence_id],
                source="REWORK",
                source_mode=SourceMode.SYNTHETIC,
                inference_status=InferenceStatus.VERIFIED,
                verification_status=CapabilityVerificationStatus.VERIFIED_BY_ASSESSMENT,
                recency_status=RecencyStatus.RECENT,
                system_confidence=proof_result.total,
                rationale="Capability established via proof-of-skill assessment.",
            )
            caps = list(candidate_capabilities) + [new_cap]

        update_event = CapabilityUpdateEvent(
            id=f"cap-update-{proof_result.id}",
            candidate_id=proof_result.candidate_id,
            skill_id=skill_id,
            old_level=old_level,
            new_level=new_level,
            evidence_ref=evidence_id,
            reason="Successful proof-of-skill assessment demonstrated capability.",
            confidence=proof_result.total,
            source_mode=SourceMode.SYNTHETIC if proof_result.is_demo else SourceMode.USER_PROVIDED,
            run_id=run_id,
        )
        return caps, update_event, new_evidence
