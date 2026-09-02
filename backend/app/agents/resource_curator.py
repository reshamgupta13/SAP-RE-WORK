"""Resource Curator Agent — map learning objectives to prototype catalog resources."""

from app.adapters.learning_resources import get_learning_resource_provider
from app.adapters.llm.base import LLMProvider
from app.adapters.llm.fallback import DeterministicFallbackProvider
from app.agents.learning_schemas import LearningStrategistOutput, ResourceCuratorOutput, ResourceSelectionExtract
from app.domain.enums import EngineMode


class ResourceCuratorAgent:
    """Select resources from the prototype catalog — never claim SAP Learning Hub."""

    def __init__(self, llm_provider: LLMProvider) -> None:
        self._llm = llm_provider
        self._catalog = get_learning_resource_provider()

    @property
    def engine_mode(self) -> EngineMode:
        return self._llm.engine_mode

    def run(self, strategist_output: LearningStrategistOutput) -> ResourceCuratorOutput:
        fallback = self._build_fallback(strategist_output)
        if isinstance(self._llm, DeterministicFallbackProvider):
            return self._llm.generate_structured(
                prompt="fallback",
                schema=ResourceCuratorOutput,
                context={"fallback_payload": fallback.model_dump()},
            )
        try:
            catalog_summary = [
                f"{r.id}: {r.title} ({r.type}, {r.capability}, {r.estimated_minutes}min)"
                for r in self._catalog.list_resources()
            ]
            prompt = (
                f"Strategist interventions:\n{strategist_output.model_dump_json()}\n\n"
                f"Available prototype catalog (source_type=prototype_catalog only):\n"
                + "\n".join(catalog_summary)
                + "\n\nSelect resource_ids for each step. Use only IDs from the catalog."
            )
            output = self._llm.generate_structured(
                prompt=prompt,
                schema=ResourceCuratorOutput,
                context={"system_instruction": self._system_instruction()},
            )
            return self._sanitize_selections(output, strategist_output)
        except Exception:
            fb = DeterministicFallbackProvider()
            return fb.generate_structured(
                prompt="fallback",
                schema=ResourceCuratorOutput,
                context={"fallback_payload": fallback.model_dump()},
            )

    def _system_instruction(self) -> str:
        return (
            "You are RE:WORK Resource Curator. Select resources ONLY from the provided prototype catalog. "
            "Never claim SAP Learning Hub or external course availability. "
            "catalog_note must state 'RE:WORK Prototype Learning Catalog'. "
            "If no matching resource exists, leave resource_ids empty and provide fallback_intervention text. "
            "Return JSON only."
        )

    def _build_fallback(self, strategist: LearningStrategistOutput) -> ResourceCuratorOutput:
        selections: list[ResourceSelectionExtract] = []
        for intervention in strategist.interventions:
            cap = intervention.capability.lower().replace(" ", "_")
            skill_key = "skill0002" if "odata" in cap else cap
            for step in intervention.steps:
                resources = self._catalog.search(skill_key, step_type=step.type, limit=1)
                if resources:
                    selections.append(
                        ResourceSelectionExtract(
                            step_id=step.step_id,
                            resource_ids=[resources[0].id],
                            why_recommended=resources[0].why_recommended or resources[0].description or "",
                        )
                    )
                else:
                    selections.append(
                        ResourceSelectionExtract(
                            step_id=step.step_id,
                            resource_ids=[],
                            why_recommended="Structured intervention created; prototype resource unavailable.",
                            fallback_intervention=step.title,
                        )
                    )
        return ResourceCuratorOutput(
            selections=selections,
            catalog_note=self._catalog.get_catalog_label(),
            summary_rationale="Deterministic fallback: catalog-matched resources.",
        )

    def _sanitize_selections(
        self,
        output: ResourceCuratorOutput,
        strategist: LearningStrategistOutput,
    ) -> ResourceCuratorOutput:
        valid_ids = {r.id for r in self._catalog.list_resources()}
        sanitized: list[ResourceSelectionExtract] = []
        for sel in output.selections:
            ids = [rid for rid in sel.resource_ids if rid in valid_ids]
            if not ids:
                step = next(
                    (
                        s
                        for iv in strategist.interventions
                        for s in iv.steps
                        if s.step_id == sel.step_id
                    ),
                    None,
                )
                sanitized.append(
                    ResourceSelectionExtract(
                        step_id=sel.step_id,
                        resource_ids=[],
                        why_recommended=sel.why_recommended,
                        fallback_intervention=step.title if step else sel.fallback_intervention,
                    )
                )
            else:
                sanitized.append(
                    ResourceSelectionExtract(
                        step_id=sel.step_id,
                        resource_ids=ids,
                        why_recommended=sel.why_recommended,
                    )
                )
        return ResourceCuratorOutput(
            selections=sanitized,
            catalog_note="RE:WORK Prototype Learning Catalog",
            summary_rationale=output.summary_rationale,
        )
