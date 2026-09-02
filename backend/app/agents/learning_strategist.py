"""Learning Strategist Agent — gaps to smallest effective interventions."""

from app.adapters.llm.base import LLMProvider
from app.adapters.llm.fallback import DeterministicFallbackProvider
from app.agents.learning_schemas import GapInterventionExtract, LearningStrategistOutput, StrategistStepExtract
from app.domain.assessment import CapabilityAssessmentItem, CapabilityGap
from app.domain.enums import EngineMode, GapStatus


class LearningStrategistAgent:
    """Convert diagnosed capability gaps into focused learning objectives."""

    def __init__(self, llm_provider: LLMProvider) -> None:
        self._llm = llm_provider

    @property
    def engine_mode(self) -> EngineMode:
        return self._llm.engine_mode

    def run(
        self,
        candidate_name: str,
        role_title: str,
        capability_items: list[CapabilityAssessmentItem],
        capability_gaps: list[CapabilityGap],
        counterfactual_summary: str | None = None,
    ) -> LearningStrategistOutput:
        fallback = self._build_fallback(
            candidate_name, role_title, capability_items, capability_gaps
        )
        if isinstance(self._llm, DeterministicFallbackProvider):
            return self._llm.generate_structured(
                prompt="fallback",
                schema=LearningStrategistOutput,
                context={"fallback_payload": fallback.model_dump()},
            )
        try:
            prompt = self._build_prompt(
                candidate_name, role_title, capability_items, capability_gaps, counterfactual_summary
            )
            return self._llm.generate_structured(
                prompt=prompt,
                schema=LearningStrategistOutput,
                context={"system_instruction": self._system_instruction()},
            )
        except Exception:
            fb = DeterministicFallbackProvider()
            return fb.generate_structured(
                prompt="fallback",
                schema=LearningStrategistOutput,
                context={"fallback_payload": fallback.model_dump()},
            )

    def _system_instruction(self) -> str:
        return (
            "You are RE:WORK Learning Strategist. Use ONLY supplied gap and capability facts. "
            "Recommend the SMALLEST effective intervention — never broad retraining when specific gaps exist. "
            "Do NOT recommend learning for capabilities already at or above required level. "
            "Do NOT invent skills, courses, or SAP Learning Hub content. "
            "For INSUFFICIENT_EVIDENCE gaps, prefer evidence clarification over beginner training. "
            "For non-addressable eligibility issues, set addressable=false. "
            "Return JSON only."
        )

    def _build_prompt(
        self,
        candidate_name: str,
        role_title: str,
        items: list[CapabilityAssessmentItem],
        gaps: list[CapabilityGap],
        counterfactual_summary: str | None,
    ) -> str:
        cap_lines = [
            f"- {i.label} ({i.skill_id}): candidate={i.candidate_proficiency}, "
            f"required={i.required_proficiency}, status={i.gap_status.value}, rationale={i.rationale}"
            for i in items
        ]
        gap_lines = [
            f"- {g.id}: skill={g.skill_id}, status={g.gap_status.value}, severity={g.severity}"
            for g in gaps
        ]
        cf = f"\nCounterfactual context: {counterfactual_summary}" if counterfactual_summary else ""
        return (
            f"Candidate: {candidate_name}\nTarget role: {role_title}\n"
            f"Capability assessment:\n" + "\n".join(cap_lines) + "\n"
            f"Diagnosed gaps:\n" + "\n".join(gap_lines) + cf + "\n"
            "Generate gap-driven interventions with 2-4 steps each for addressable gaps only."
        )

    def _build_fallback(
        self,
        candidate_name: str,
        role_title: str,
        items: list[CapabilityAssessmentItem],
        gaps: list[CapabilityGap],
    ) -> LearningStrategistOutput:
        sufficient = [
            i.label for i in items if i.gap_status == GapStatus.MATCHED
        ]
        interventions: list[GapInterventionExtract] = []

        genuine = [g for g in gaps if g.gap_status == GapStatus.GENUINE_CAPABILITY_GAP]
        evidence_gaps = [g for g in gaps if g.gap_status == GapStatus.INSUFFICIENT_EVIDENCE]

        for gap in genuine:
            item = next((i for i in items if i.skill_id == gap.skill_id), None)
            if not item:
                continue
            label = item.label
            skill = gap.skill_id or "unknown"
            current = item.candidate_proficiency or 0.0
            required = item.required_proficiency or 0.6
            is_odata = "odata" in label.lower() or skill == "skill0002"
            steps = self._default_steps(label, is_odata)
            interventions.append(
                GapInterventionExtract(
                    gap_id=gap.id,
                    capability=label,
                    current_level=current,
                    required_level=required,
                    target_role=role_title,
                    learning_objective=(
                        f"Build and consume a basic {label} service"
                        if is_odata
                        else f"Develop {label} to role-required proficiency"
                    ),
                    intervention_type="focused_skill_build",
                    estimated_effort="small" if required - current <= 0.4 else "medium",
                    reason=(
                        f"Candidate demonstrates adjacent capabilities; {label} is the material gap."
                        if sufficient
                        else f"{label} is below role threshold."
                    ),
                    smallest_effective_rationale=(
                        f"{'Java, SQL and REST APIs already satisfy the role. ' if sufficient else ''}"
                        f"Focused {label} pathway avoids unnecessary broad retraining."
                    ),
                    steps=steps,
                )
            )

        for gap in evidence_gaps:
            item = next((i for i in items if i.skill_id == gap.skill_id), None)
            if not item:
                continue
            interventions.append(
                GapInterventionExtract(
                    gap_id=gap.id,
                    capability=item.label,
                    current_level=item.candidate_proficiency or 0.0,
                    required_level=item.required_proficiency or 0.6,
                    target_role=role_title,
                    learning_objective=f"Provide verifiable evidence for {item.label}",
                    intervention_type="evidence_clarification",
                    estimated_effort="minimal",
                    reason="Capability claimed or inferred but evidence is insufficient.",
                    smallest_effective_rationale=(
                        "Evidence validation is smaller than assigning beginner training."
                    ),
                    steps=[
                        StrategistStepExtract(
                            step_id="E1",
                            title="Evidence clarification",
                            type="documentation",
                            rationale="Submit verifiable work samples before assigning training.",
                            estimated_minutes=20,
                        )
                    ],
                )
            )

        sufficient_text = ", ".join(sufficient) if sufficient else "none identified"
        why = (
            f"Your strongest capabilities already cover {sufficient_text}. "
            f"The primary gap{'s' if len(interventions) != 1 else ''} identified for {role_title} "
            f"require{'s' if len(interventions) == 1 else ''} targeted intervention, not broad retraining."
        )
        if not interventions:
            why = (
                f"{candidate_name} meets all required capabilities for {role_title}. "
                "No reskilling intervention is required."
            )

        return LearningStrategistOutput(
            why_this_path=why,
            gaps_sufficient=sufficient,
            interventions=interventions,
            summary_rationale="Deterministic fallback: gap-first intervention planning.",
        )

    def _default_steps(self, label: str, is_odata: bool) -> list[StrategistStepExtract]:
        if is_odata:
            return [
                StrategistStepExtract(
                    step_id="L1",
                    title="Understand OData fundamentals",
                    type="concept",
                    rationale="Required to understand the service model used by the target role.",
                    estimated_minutes=35,
                ),
                StrategistStepExtract(
                    step_id="L2",
                    title="Implement an OData CRUD service",
                    type="hands_on",
                    rationale="Converts conceptual understanding into demonstrated capability.",
                    estimated_minutes=75,
                ),
                StrategistStepExtract(
                    step_id="L3",
                    title="Validate the service through API testing",
                    type="assessment",
                    rationale="Provides observable evidence of practical capability.",
                    estimated_minutes=45,
                ),
            ]
        return [
            StrategistStepExtract(
                step_id="L1",
                title=f"{label} fundamentals",
                type="concept",
                rationale=f"Foundation for closing the {label} gap.",
                estimated_minutes=30,
            ),
            StrategistStepExtract(
                step_id="L2",
                title=f"{label} hands-on practice",
                type="hands_on",
                rationale=f"Apply {label} skills in a role-aligned exercise.",
                estimated_minutes=60,
            ),
        ]
