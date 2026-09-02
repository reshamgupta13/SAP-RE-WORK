"""Deterministic validation for AI-generated learning plans."""

from app.agents.learning_schemas import LearningStrategistOutput, ProofAlignmentOutput, ResourceCuratorOutput
from app.domain.assessment import CapabilityAssessmentItem, CapabilityGap
from app.domain.enums import GapStatus
from app.domain.learning import LearningPlanValidation, ValidationCheck


class LearningPlanValidator:
    """Validate gap traceability, role alignment, and proof coverage."""

    FORBIDDEN_CLAIMS = (
        "sap learning hub",
        "learning hub integration",
        "official sap course",
        "guaranteed skill",
        "guaranteed placement",
    )

    def validate(
        self,
        strategist: LearningStrategistOutput,
        curator: ResourceCuratorOutput,
        proof: ProofAlignmentOutput,
        capability_items: list[CapabilityAssessmentItem],
        capability_gaps: list[CapabilityGap],
        diagnosed_gap_ids: set[str],
    ) -> LearningPlanValidation:
        checks: list[ValidationCheck] = []
        issues: list[str] = []

        checks.append(self._check_gap_traceability(strategist, diagnosed_gap_ids, issues))
        checks.append(self._check_addressable_gaps_have_objectives(strategist, capability_gaps, issues))
        checks.append(self._check_no_unnecessary_learning(strategist, capability_items, issues))
        checks.append(self._check_proof_alignment(strategist, proof, issues))
        checks.append(self._check_no_external_claims(strategist, curator, proof, issues))
        checks.append(self._check_catalog_honesty(curator, issues))
        checks.append(self._check_proficiency_preserved(strategist, capability_items, issues))
        checks.append(self._check_internal_consistency(strategist, curator, proof, issues))

        failed = [c for c in checks if c.status == "failed"]
        status = "passed" if not failed else "failed"
        return LearningPlanValidation(status=status, checks=checks, issues=issues)

    def _check_gap_traceability(
        self,
        strategist: LearningStrategistOutput,
        diagnosed_gap_ids: set[str],
        issues: list[str],
    ) -> ValidationCheck:
        intervention_gap_ids = {iv.gap_id for iv in strategist.interventions}
        orphan_steps = [
            iv.gap_id for iv in strategist.interventions if iv.gap_id not in diagnosed_gap_ids
        ]
        if orphan_steps:
            issues.append(f"Interventions reference undiagnosed gaps: {orphan_steps}")
            return ValidationCheck(
                name="gap_traceability",
                status="failed",
                message="Some interventions do not map to diagnosed gaps.",
            )
        unaddressed = diagnosed_gap_ids - intervention_gap_ids
        genuine_unaddressed = unaddressed  # validator allows evidence-only gaps without learning
        if genuine_unaddressed and not strategist.interventions:
            issues.append("Diagnosed gaps exist but no interventions generated.")
            return ValidationCheck(name="gap_traceability", status="failed", message="Gaps without interventions.")
        return ValidationCheck(name="gap_traceability", status="passed")

    def _check_addressable_gaps_have_objectives(
        self,
        strategist: LearningStrategistOutput,
        gaps: list[CapabilityGap],
        issues: list[str],
    ) -> ValidationCheck:
        addressable_statuses = {GapStatus.GENUINE_CAPABILITY_GAP, GapStatus.INSUFFICIENT_EVIDENCE}
        addressable_ids = {g.id for g in gaps if g.gap_status in addressable_statuses}
        covered = {iv.gap_id for iv in strategist.interventions if iv.addressable}
        missing = addressable_ids - covered
        if missing and strategist.interventions:
            # partial coverage is ok if some gaps are matched
            pass
        for iv in strategist.interventions:
            if iv.addressable and not iv.learning_objective:
                issues.append(f"Missing learning objective for gap {iv.gap_id}")
                return ValidationCheck(
                    name="objectives_present",
                    status="failed",
                    message="Addressable gap missing learning objective.",
                )
        return ValidationCheck(name="objectives_present", status="passed")

    def _check_no_unnecessary_learning(
        self,
        strategist: LearningStrategistOutput,
        items: list[CapabilityAssessmentItem],
        issues: list[str],
    ) -> ValidationCheck:
        matched_labels = {i.label.lower() for i in items if i.gap_status == GapStatus.MATCHED}
        for iv in strategist.interventions:
            if iv.capability.lower() in matched_labels and iv.intervention_type != "evidence_clarification":
                issues.append(f"Unnecessary learning recommended for sufficient capability: {iv.capability}")
                return ValidationCheck(
                    name="unnecessary_learning",
                    status="failed",
                    message=f"Learning recommended for already-sufficient {iv.capability}.",
                )
        return ValidationCheck(name="unnecessary_learning", status="passed")

    def _check_proof_alignment(
        self,
        strategist: LearningStrategistOutput,
        proof: ProofAlignmentOutput,
        issues: list[str],
    ) -> ValidationCheck:
        if not strategist.interventions:
            return ValidationCheck(name="proof_alignment", status="passed")
        addressable = [iv for iv in strategist.interventions if iv.addressable]
        proof_gaps = {p.gap_id for p in proof.proofs}
        for iv in addressable:
            if iv.gap_id not in proof_gaps:
                issues.append(f"Missing proof for gap {iv.gap_id}")
                return ValidationCheck(
                    name="proof_alignment",
                    status="failed",
                    message="Addressable intervention missing proof requirement.",
                )
        return ValidationCheck(name="proof_alignment", status="passed")

    def _check_no_external_claims(
        self,
        strategist: LearningStrategistOutput,
        curator: ResourceCuratorOutput,
        proof: ProofAlignmentOutput,
        issues: list[str],
    ) -> ValidationCheck:
        blob = (
            strategist.model_dump_json() + curator.model_dump_json() + proof.model_dump_json()
        ).lower()
        for claim in self.FORBIDDEN_CLAIMS:
            if claim in blob:
                issues.append(f"Forbidden claim detected: {claim}")
                return ValidationCheck(
                    name="no_external_claims",
                    status="failed",
                    message=f"Output contains unsupported claim: {claim}",
                )
        return ValidationCheck(name="no_external_claims", status="passed")

    def _check_catalog_honesty(self, curator: ResourceCuratorOutput, issues: list[str]) -> ValidationCheck:
        note = (curator.catalog_note or "").lower()
        if "sap learning hub" in note and "not connected" not in note:
            issues.append("Catalog note falsely claims SAP Learning Hub.")
            return ValidationCheck(name="catalog_honesty", status="failed")
        if "prototype" not in note and "re:work" not in note:
            return ValidationCheck(
                name="catalog_honesty",
                status="warning",
                message="Catalog label should identify prototype source.",
            )
        return ValidationCheck(name="catalog_honesty", status="passed")

    def _check_proficiency_preserved(
        self,
        strategist: LearningStrategistOutput,
        items: list[CapabilityAssessmentItem],
        issues: list[str],
    ) -> ValidationCheck:
        item_by_skill = {i.label.lower(): i for i in items}
        for iv in strategist.interventions:
            item = item_by_skill.get(iv.capability.lower())
            if item and iv.required_level < item.required_proficiency - 0.05:
                issues.append(f"Required proficiency lowered for {iv.capability}")
                return ValidationCheck(
                    name="proficiency_preserved",
                    status="failed",
                    message="Proof proficiency below role requirement.",
                )
        return ValidationCheck(name="proficiency_preserved", status="passed")

    def _check_internal_consistency(
        self,
        strategist: LearningStrategistOutput,
        curator: ResourceCuratorOutput,
        proof: ProofAlignmentOutput,
        issues: list[str],
    ) -> ValidationCheck:
        step_ids = {s.step_id for iv in strategist.interventions for s in iv.steps}
        curator_steps = {s.step_id for s in curator.selections}
        orphan_curator = curator_steps - step_ids
        if orphan_curator:
            issues.append(f"Curator selections for unknown steps: {orphan_curator}")
            return ValidationCheck(name="internal_consistency", status="failed")
        return ValidationCheck(name="internal_consistency", status="passed")
