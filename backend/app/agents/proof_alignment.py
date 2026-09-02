"""Proof Alignment Agent — connect learning to verifiable proof requirements."""

from app.adapters.llm.base import LLMProvider
from app.adapters.llm.fallback import DeterministicFallbackProvider
from app.agents.learning_schemas import (
    LearningStrategistOutput,
    ProofAlignmentExtract,
    ProofAlignmentOutput,
)
from app.domain.enums import EngineMode


class ProofAlignmentAgent:
    """Define what evidence would convince an HR reviewer."""

    def __init__(self, llm_provider: LLMProvider) -> None:
        self._llm = llm_provider

    @property
    def engine_mode(self) -> EngineMode:
        return self._llm.engine_mode

    def run(
        self,
        strategist_output: LearningStrategistOutput,
        role_title: str,
    ) -> ProofAlignmentOutput:
        fallback = self._build_fallback(strategist_output)
        if isinstance(self._llm, DeterministicFallbackProvider):
            return self._llm.generate_structured(
                prompt="fallback",
                schema=ProofAlignmentOutput,
                context={"fallback_payload": fallback.model_dump()},
            )
        try:
            prompt = (
                f"Target role: {role_title}\n"
                f"Interventions:\n{strategist_output.model_dump_json()}\n\n"
                "Define proof-of-skill requirements with acceptance criteria. "
                "Learning completion alone does not equal readiness."
            )
            return self._llm.generate_structured(
                prompt=prompt,
                schema=ProofAlignmentOutput,
                context={"system_instruction": self._system_instruction()},
            )
        except Exception:
            fb = DeterministicFallbackProvider()
            return fb.generate_structured(
                prompt="fallback",
                schema=ProofAlignmentOutput,
                context={"fallback_payload": fallback.model_dump()},
            )

    def _system_instruction(self) -> str:
        return (
            "You are RE:WORK Proof Alignment. Define verifiable proof tasks linked to capability gaps. "
            "Use only supplied capabilities and role requirements. "
            "Acceptance criteria must be observable and testable. Return JSON only."
        )

    def _build_fallback(self, strategist: LearningStrategistOutput) -> ProofAlignmentOutput:
        proofs: list[ProofAlignmentExtract] = []
        for iv in strategist.interventions:
            if not iv.addressable:
                continue
            is_odata = "odata" in iv.capability.lower()
            if is_odata:
                proofs.append(
                    ProofAlignmentExtract(
                        gap_id=iv.gap_id,
                        proof_type="hands_on_task",
                        proof_title="Build an SAP OData CRUD service",
                        proof_description=(
                            "Demonstrate OData capability by building and testing a working CRUD service."
                        ),
                        acceptance_criteria=[
                            "Service is exposed and reachable",
                            "Entity set is accessible via GET",
                            "CREATE operation works",
                            "UPDATE operation works",
                            "DELETE operation works",
                        ],
                        linked_capability=iv.capability,
                        required_proficiency=iv.required_level,
                    )
                )
            elif iv.intervention_type == "evidence_clarification":
                proofs.append(
                    ProofAlignmentExtract(
                        gap_id=iv.gap_id,
                        proof_type="evidence_submission",
                        proof_title=f"Submit verifiable evidence for {iv.capability}",
                        proof_description=(
                            "Provide work samples, certifications, or project artifacts "
                            f"demonstrating {iv.capability}."
                        ),
                        acceptance_criteria=[
                            "Evidence is independently verifiable",
                            "Evidence maps to role-required proficiency",
                            "Evidence is recent and relevant",
                        ],
                        linked_capability=iv.capability,
                        required_proficiency=iv.required_level,
                    )
                )
            else:
                proofs.append(
                    ProofAlignmentExtract(
                        gap_id=iv.gap_id,
                        proof_type="hands_on_task",
                        proof_title=f"Demonstrate {iv.capability} proficiency",
                        proof_description=(
                            f"Complete a structured task demonstrating {iv.capability} "
                            "at the required proficiency level."
                        ),
                        acceptance_criteria=[
                            f"Task demonstrates {iv.capability} at required level",
                            "Output is reviewable by HR",
                            "Criteria align with role requirements",
                        ],
                        linked_capability=iv.capability,
                        required_proficiency=iv.required_level,
                    )
                )
        return ProofAlignmentOutput(
            proofs=proofs,
            summary_rationale="Deterministic fallback: gap-aligned proof requirements.",
        )
