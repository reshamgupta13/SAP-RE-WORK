"""Deterministic learning pathway generation from diagnosed gaps."""

from app.adapters.sap_learning import get_sap_learning_provider
from app.domain.assessment import CapabilityAssessmentItem, CapabilityGap
from app.domain.enums import GapStatus, MilestoneStatus, PathwayStatus, ReadinessState, SourceMode
from app.domain.job import JobCapability
from app.domain.pathway import LearningItem, LearningPath, PathwayMilestone


class PathwayEngine:
    """Generate minimum-effective pathways bound to diagnosed capability gaps."""

    def generate(
        self,
        candidate_id: str,
        target_role_id: str,
        run_id: str | None,
        capability_gaps: list[CapabilityGap],
        capability_items: list[CapabilityAssessmentItem],
        job_capabilities: list[JobCapability],
        role_title: str | None = None,
    ) -> LearningPath | None:
        genuine_gaps = [
            g for g in capability_gaps if g.gap_status == GapStatus.GENUINE_CAPABILITY_GAP
        ]
        if not genuine_gaps:
            return None

        primary_gap = self._select_primary_gap(genuine_gaps, capability_items, job_capabilities)
        if not primary_gap or not primary_gap.skill_id:
            return None

        skill_id = primary_gap.skill_id
        item = next((i for i in capability_items if i.skill_id == skill_id), None)
        job_cap = next((c for c in job_capabilities if c.skill_id == skill_id), None)

        current_level = item.candidate_proficiency if item else 0.0
        required_level = item.required_proficiency if item else (job_cap.min_proficiency if job_cap else 0.6)
        gap_magnitude = max(0.0, required_level - (current_level or 0.0))

        learning_provider = get_sap_learning_provider()
        role_context = {"role_id": target_role_id, "title": role_title}
        learning_items = learning_provider.search_learning_items(
            capability=skill_id,
            proficiency_gap=gap_magnitude,
            role_context=role_context,
        )

        if not learning_items:
            learning_items = self._synthetic_fallback_items(skill_id)

        label = item.label if item else (job_cap.label if job_cap else skill_id)
        milestones = self._build_milestones(
            skill_id, label, current_level or 0.0, required_level, learning_items
        )
        total_hours = sum(i.hours or i.estimated_duration or 0 for i in learning_items)
        practical_tasks = [m.practice_task for m in milestones if m.practice_task]

        pathway = LearningPath(
            id=f"pathway-{candidate_id}-{target_role_id}-{skill_id}",
            candidate_id=candidate_id,
            target_role_id=target_role_id,
            created_from_run_id=run_id,
            status=PathwayStatus.READY_FOR_PROOF,
            current_state=f"{label} proficiency {current_level:.2f}",
            target_state=f"{label} proficiency {required_level:.2f}",
            target_capabilities=[skill_id],
            gap_skill_ids=[skill_id],
            milestones=milestones,
            learning_item_ids=[i.id for i in learning_items],
            learning_items=learning_items,
            practical_tasks=[t for t in practical_tasks if t],
            proof_of_skill_id=f"assess-{skill_id}-{candidate_id}",
            duration_weeks=round(total_hours / 8, 1) if total_hours else 2.0,
            estimated_duration_hours=total_hours or 16.0,
            expected_readiness=ReadinessState.READY_WITH_PROOF,
            confidence=0.78,
            why=f"{label} is the primary diagnosed capability gap for the target {role_title or 'role'}.",
            what=(
                f"Build {label} capability through targeted learning and a role-specific "
                "dashboard project."
            ),
            how="Complete milestones, practice task, and defined proof-of-skill assessment.",
            success_criteria=(
                "Demonstrate data preparation, dashboard construction, business insight, "
                "and communication in the proof task."
            ),
            source_mode=SourceMode.SYNTHETIC,
        )
        return pathway

    def _select_primary_gap(
        self,
        gaps: list[CapabilityGap],
        items: list[CapabilityAssessmentItem],
        job_caps: list[JobCapability],
    ) -> CapabilityGap:
        scored: list[tuple[float, CapabilityGap]] = []
        for gap in gaps:
            if not gap.skill_id:
                continue
            item = next((i for i in items if i.skill_id == gap.skill_id), None)
            job_cap = next((c for c in job_caps if c.skill_id == gap.skill_id), None)
            importance = 1.0 if (job_cap and job_cap.importance == "core") else 0.5
            magnitude = (item.gap or 0.0) if item else 0.3
            scored.append((importance * magnitude, gap))
        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[0][1]

    def _build_milestones(
        self,
        skill_id: str,
        label: str,
        current_level: float,
        required_level: float,
        learning_items: list[LearningItem],
    ) -> list[PathwayMilestone]:
        mid_level = round((current_level + required_level) / 2, 2)
        item_ids = [i.id for i in learning_items]

        milestones = [
            PathwayMilestone(
                id=f"milestone-{skill_id}-1",
                sequence=1,
                objective=f"{label} foundations",
                capability=skill_id,
                starting_level=current_level,
                target_level=mid_level,
                learning_item_ids=item_ids[:1],
                practice_task=None,
                completion_criteria=learning_items[0].completion_criteria if learning_items else None,
                status=MilestoneStatus.PENDING,
            ),
            PathwayMilestone(
                id=f"milestone-{skill_id}-2",
                sequence=2,
                objective=f"{label} dashboard construction",
                capability=skill_id,
                starting_level=mid_level,
                target_level=required_level,
                learning_item_ids=item_ids[1:2] if len(item_ids) > 1 else item_ids,
                practice_task=(
                    f"Build a recurring {label} dashboard for operational leadership KPIs."
                ),
                completion_criteria="Dashboard includes trends, rankings, and declining segments.",
                status=MilestoneStatus.PENDING,
            ),
            PathwayMilestone(
                id=f"milestone-{skill_id}-3",
                sequence=3,
                objective="Business analytics project",
                capability=skill_id,
                starting_level=mid_level,
                target_level=required_level,
                learning_item_ids=item_ids[2:3] if len(item_ids) > 2 else [],
                practice_task="Complete role-specific analytics exercise using provided sales dataset.",
                completion_criteria="Project demonstrates analytical reasoning and stakeholder-ready output.",
                status=MilestoneStatus.PENDING,
            ),
            PathwayMilestone(
                id=f"milestone-{skill_id}-4",
                sequence=4,
                objective="Proof-of-skill assessment",
                capability=skill_id,
                starting_level=current_level,
                target_level=required_level,
                learning_item_ids=[],
                practice_task=None,
                proof_requirement=f"assess-{skill_id}",
                completion_criteria="Pass structured proof-of-skill rubric.",
                status=MilestoneStatus.PENDING,
            ),
        ]
        return milestones

    def _synthetic_fallback_items(self, skill_id: str) -> list[LearningItem]:
        return [
            LearningItem(
                id=f"learn-synthetic-{skill_id}",
                title=f"{skill_id.replace('_', ' ').title()} essentials (synthetic)",
                description="Synthetic fallback learning item when catalog is empty.",
                capability=skill_id,
                hours=4,
                source_mode=SourceMode.SYNTHETIC,
                skill_alignment=[skill_id],
                completion_criteria="Complete practice exercises.",
            )
        ]
