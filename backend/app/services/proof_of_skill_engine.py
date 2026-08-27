"""Deterministic proof-of-skill assessment and evaluation."""

from datetime import datetime, timezone

from app.domain.enums import ProofResultStatus, SourceMode
from app.domain.pathway import (
    ProofCriterionResult,
    ProofEvidence,
    ProofOfSkillAssessment,
    ProofOfSkillResult,
    ProofRubricCriterion,
    ProofSubmission,
)

PASS_THRESHOLD = 0.7

POWER_BI_RUBRIC: list[ProofRubricCriterion] = [
    ProofRubricCriterion(
        id="rubric-pbi-prep",
        criterion="Data Preparation",
        weight=0.25,
        description="Import, clean, and model source data appropriately.",
    ),
    ProofRubricCriterion(
        id="rubric-pbi-dash",
        criterion="Dashboard Construction",
        weight=0.25,
        description="Build coherent dashboard layout with relevant visuals.",
    ),
    ProofRubricCriterion(
        id="rubric-pbi-viz",
        criterion="Visualization Quality",
        weight=0.2,
        description="Charts are accurate, readable, and appropriately formatted.",
    ),
    ProofRubricCriterion(
        id="rubric-pbi-insight",
        criterion="Business Insight",
        weight=0.2,
        description="Identifies trends, top performers, and declining segments.",
    ),
    ProofRubricCriterion(
        id="rubric-pbi-comm",
        criterion="Communication",
        weight=0.1,
        description="Findings are explained clearly for business stakeholders.",
    ),
]

POWER_BI_TASK = (
    "Using the provided sales dataset, create a Power BI dashboard that identifies "
    "monthly revenue trends, top-performing regions, and the largest declining segment. "
    "Explain your analytical approach and key findings."
)


class ProofOfSkillEngine:
    """Evaluate capability through structured proof tasks — not generic exams."""

    def create_assessment(
        self,
        skill_id: str,
        candidate_id: str,
        is_demo: bool = False,
    ) -> ProofOfSkillAssessment:
        if skill_id == "power_bi":
            return ProofOfSkillAssessment(
                id=f"assess-{skill_id}-{candidate_id}",
                skill_id=skill_id,
                task_key="power_bi_sales_dashboard",
                task_description=POWER_BI_TASK,
                rubric_json={
                    "criteria": [c.model_dump() for c in POWER_BI_RUBRIC],
                    "pass_threshold": PASS_THRESHOLD,
                },
                rubric_criteria=POWER_BI_RUBRIC,
                source_mode=SourceMode.SYNTHETIC,
                is_demo=is_demo,
            )
        return ProofOfSkillAssessment(
            id=f"assess-{skill_id}-{candidate_id}",
            skill_id=skill_id,
            task_key=f"{skill_id}_general",
            task_description=f"Demonstrate {skill_id.replace('_', ' ')} capability through a structured task.",
            rubric_criteria=[
                ProofRubricCriterion(
                    id=f"rubric-{skill_id}",
                    criterion="Task completion",
                    weight=1.0,
                )
            ],
            source_mode=SourceMode.SYNTHETIC,
            is_demo=is_demo,
        )

    def evaluate_submission(
        self,
        assessment: ProofOfSkillAssessment,
        submission: ProofSubmission,
    ) -> tuple[ProofOfSkillResult, ProofEvidence]:
        criteria = assessment.rubric_criteria
        if not criteria and assessment.rubric_json.get("criteria"):
            criteria = [
                ProofRubricCriterion.model_validate(c)
                for c in assessment.rubric_json["criteria"]
            ]

        criterion_results: list[ProofCriterionResult] = []
        total_weighted = 0.0
        responses = submission.responses

        for criterion in criteria:
            key = criterion.criterion.lower().replace(" ", "_")
            score = responses.get(key)
            if score is None:
                for k, v in responses.items():
                    if key in k or criterion.criterion.lower() in k.lower():
                        score = v
                        break
            if score is None:
                score = 0.0
            score = float(max(0.0, min(1.0, score)))
            criterion_results.append(
                ProofCriterionResult(
                    id=f"result-{criterion.id}",
                    criterion=criterion.criterion,
                    weight=criterion.weight,
                    score=score,
                    evidence=f"Rubric response score: {score:.2f}",
                    feedback=self._feedback_for_score(criterion.criterion, score),
                )
            )
            total_weighted += score * criterion.weight

        passed = total_weighted >= PASS_THRESHOLD
        result_status = ProofResultStatus.PASSED if passed else ProofResultStatus.FAILED

        result = ProofOfSkillResult(
            id=f"proof-result-{assessment.id}",
            assessment_id=assessment.id,
            candidate_id=submission.candidate_id,
            skill_id=assessment.skill_id,
            scores_json=dict(responses),
            criterion_results=criterion_results,
            total=round(total_weighted, 2),
            result=result_status,
            evaluator="deterministic_rubric",
            source_mode=submission.source_mode,
            is_demo=submission.is_demo,
        )

        evidence = ProofEvidence(
            id=f"proof-evidence-{assessment.id}",
            assessment_id=assessment.id,
            candidate_id=submission.candidate_id,
            capability=assessment.skill_id,
            criterion_results=criterion_results,
            overall_result=result_status,
            evidence_refs=[result.id],
            confidence=round(total_weighted, 2),
            verification_status="VERIFIED_BY_ASSESSMENT",
            timestamp=datetime.now(timezone.utc),
            source_mode=submission.source_mode,
            is_demo=submission.is_demo,
        )
        return result, evidence

    def _feedback_for_score(self, criterion: str, score: float) -> str:
        if score >= 0.8:
            return f"Strong demonstration of {criterion}."
        if score >= PASS_THRESHOLD:
            return f"Adequate {criterion}; minor improvements possible."
        return f"{criterion} needs additional practice before role readiness."
