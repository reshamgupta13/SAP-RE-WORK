"""Job Decomposition Agent tests."""

from app.adapters.llm.fallback import DeterministicFallbackProvider
from app.agents.job_decomposition import JobDecompositionAgent
from app.domain.enums import EngineMode, RequirementClass
from app.services.fixture_service import FixtureService


def _agent() -> JobDecompositionAgent:
    return JobDecompositionAgent(DeterministicFallbackProvider())


def test_data_analyst_tasks_decomposed():
    job = FixtureService().get_data_analyst_job()
    outcomes, tasks, capabilities, requirements, _ = _agent().run(job)
    task_ids = {t.id for t in tasks}
    assert "task-da-sql" in task_ids
    assert "task-da-dashboard" in task_ids


def test_sql_capability_linked_to_task():
    job = FixtureService().get_data_analyst_job()
    _, tasks, capabilities, _, _ = _agent().run(job)
    sql_task = next(t for t in tasks if t.id == "task-da-sql")
    assert "sql" in sql_task.capability_ids
    assert any(c.skill_id == "sql" for c in capabilities)


def test_power_bi_capability_present():
    job = FixtureService().get_data_analyst_job()
    _, _, capabilities, _, _ = _agent().run(job)
    assert any(c.skill_id == "power_bi" for c in capabilities)


def test_continuous_experience_requirement():
    job = FixtureService().get_data_analyst_job()
    _, _, _, requirements, _ = _agent().run(job)
    exp = next(r for r in requirements if "continuous" in r.text.lower())
    assert exp.requirement_class == RequirementClass.EXPERIENCE_REQUIREMENT


def test_no_bias_confirmed_classification():
    job = FixtureService().get_data_analyst_job()
    _, _, _, requirements, _ = _agent().run(job)
    for r in requirements:
        assert "BIAS_CONFIRMED" not in r.requirement_class.value
        assert "bias" not in (r.text.lower())


def test_unknown_requirement_class_allowed():
    job = FixtureService().get_data_analyst_job()
    _, _, _, requirements, _ = _agent().run(job)
    assert all(r.requirement_class in RequirementClass for r in requirements)


def test_engine_mode_demo_fallback():
    assert _agent().engine_mode == EngineMode.DEMO_FALLBACK
