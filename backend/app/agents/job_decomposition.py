"""Job Decomposition Agent — task-first role analysis."""

from datetime import datetime

from app.adapters.llm.base import LLMProvider
from app.adapters.llm.fallback import DeterministicFallbackProvider
from app.agents.schemas import (
    JobCapabilityExtract,
    JobDecompositionOutput,
    JobTaskExtract,
    RequirementAnalysisExtract,
    RoleOutcomeExtract,
)
from app.domain.enums import EngineMode, RequirementClass, ReviewTag, SourceMode
from app.domain.job import JobCapability, JobProfile, JobRequirement, JobTask, RoleOutcome


class JobDecompositionAgent:
    """Transforms job description into tasks, capabilities, and classified requirements."""

    def __init__(self, llm_provider: LLMProvider) -> None:
        self._llm = llm_provider

    @property
    def engine_mode(self) -> EngineMode:
        return self._llm.engine_mode

    def run(self, job: JobProfile) -> tuple[
        list[RoleOutcome],
        list[JobTask],
        list[JobCapability],
        list[JobRequirement],
        str,
    ]:
        fallback_payload = self._build_fallback_output(job)

        if isinstance(self._llm, DeterministicFallbackProvider):
            output = self._llm.generate_structured(
                prompt="fallback",
                schema=JobDecompositionOutput,
                context={"fallback_payload": fallback_payload.model_dump()},
            )
        else:
            try:
                output = self._llm.generate_structured(
                    prompt=self._build_prompt(job),
                    schema=JobDecompositionOutput,
                    context={"system_instruction": self._system_instruction()},
                )
            except Exception:
                fallback = DeterministicFallbackProvider()
                output = fallback.generate_structured(
                    prompt="fallback",
                    schema=JobDecompositionOutput,
                    context={"fallback_payload": fallback_payload.model_dump()},
                )

        outcomes, tasks, capabilities, requirements = self._to_domain(job, output)
        rationale = output.summary_rationale or "Job decomposed from supplied role definition."
        return outcomes, tasks, capabilities, requirements, rationale

    def _system_instruction(self) -> str:
        return (
            "You are RE:WORK Job Decomposition. Use ONLY supplied job information. "
            "Decompose into outcomes, tasks, capabilities, and requirement classifications. "
            "Do not declare discrimination. Use UNKNOWN when uncertain. "
            "Do not label POTENTIAL_PROXY without contextual reason. Return JSON only."
        )

    def _build_prompt(self, job: JobProfile) -> str:
        return (
            f"Job: {job.title} ({job.id})\n"
            f"Location: {job.location}\n"
            f"Raw text:\n{job.raw_text}\n"
        )

    def _build_fallback_output(self, job: JobProfile) -> JobDecompositionOutput:
        if job.tasks and job.capabilities and job.requirements:
            outcomes = [
                RoleOutcomeExtract(
                    id=o.id,
                    text=o.text,
                    confidence=0.75,
                )
                for o in job.outcomes
            ]
            tasks = [
                JobTaskExtract(
                    id=t.id,
                    text=t.text,
                    on_site_likelihood=t.on_site_likelihood,
                    importance=t.importance,
                    capability_ids=t.capability_ids,
                    source_requirement_ids=t.source_requirement_ids,
                )
                for t in job.tasks
            ]
            capabilities = [
                JobCapabilityExtract(
                    id=c.id,
                    skill_id=c.skill_id,
                    label=c.label,
                    min_proficiency=c.min_proficiency,
                    importance=c.importance,
                    evidence_expectation=c.evidence_expectation,
                    linked_task_ids=[
                        t.id for t in job.tasks if c.skill_id in t.capability_ids
                    ],
                )
                for c in job.capabilities
            ]
            requirements = [
                RequirementAnalysisExtract(
                    id=r.id,
                    text=r.text,
                    requirement_class=r.requirement_class.value,
                    review_tag=r.review_tag.value,
                    strength=r.strength,
                    why_relevant=r.why_relevant,
                    why_may_be_proxy=r.why_may_be_proxy,
                    linked_task_ids=r.linked_task_ids,
                    confidence=r.confidence,
                    rationale=f"Classified as {r.requirement_class.value}.",
                )
                for r in job.requirements
            ]
            return JobDecompositionOutput(
                outcomes=outcomes,
                tasks=tasks,
                capabilities=capabilities,
                requirements=requirements,
                summary_rationale="Demo fallback: structured job fixture decomposition.",
            )

        return JobDecompositionOutput(
            outcomes=[],
            tasks=[],
            capabilities=[],
            requirements=[],
            summary_rationale="Insufficient structured job data for fallback.",
        )

    def _to_domain(
        self,
        job: JobProfile,
        output: JobDecompositionOutput,
    ) -> tuple[list[RoleOutcome], list[JobTask], list[JobCapability], list[JobRequirement]]:
        now = datetime.utcnow()
        outcomes = [
            RoleOutcome(
                id=o.id,
                job_id=job.id,
                text=o.text,
                source_mode=SourceMode.SYNTHETIC,
                created_at=now,
            )
            for o in output.outcomes
        ]
        tasks = [
            JobTask(
                id=t.id,
                job_id=job.id,
                text=t.text,
                on_site_likelihood=t.on_site_likelihood,
                importance=t.importance,
                capability_ids=t.capability_ids,
                source_requirement_ids=t.source_requirement_ids,
                source_mode=SourceMode.SYNTHETIC,
                created_at=now,
            )
            for t in output.tasks
        ]
        capabilities = [
            JobCapability(
                id=c.id,
                job_id=job.id,
                skill_id=c.skill_id,
                label=c.label,
                min_proficiency=c.min_proficiency,
                importance=c.importance,
                evidence_expectation=c.evidence_expectation,
                source_mode=SourceMode.SYNTHETIC,
                created_at=now,
            )
            for c in output.capabilities
        ]
        requirements = [
            JobRequirement(
                id=r.id,
                job_id=job.id,
                text=r.text,
                requirement_class=RequirementClass(r.requirement_class),
                review_tag=ReviewTag(r.review_tag),
                strength=r.strength,
                why_relevant=r.why_relevant,
                why_may_be_proxy=r.why_may_be_proxy,
                linked_task_ids=r.linked_task_ids,
                confidence=r.confidence,
                source_mode=SourceMode.SYNTHETIC,
                created_at=now,
            )
            for r in output.requirements
        ]
        return outcomes, tasks, capabilities, requirements
