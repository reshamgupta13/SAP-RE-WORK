"""SAP adapter tests."""

from app.adapters.sap import get_sap_provider
from app.adapters.sap.live import LiveSAPProvider
from app.adapters.sap.simulated import SimulatedSAPProvider
from app.domain.enums import IntegrationStatus, SourceMode


def test_factory_returns_simulated_in_demo_mode():
    provider = get_sap_provider()
    assert isinstance(provider, SimulatedSAPProvider)


def test_simulated_context_source_mode():
    provider = SimulatedSAPProvider()
    context = provider.get_context()
    assert context.source_mode == SourceMode.SIMULATED
    assert context.integration_status == IntegrationStatus.AVAILABLE
    assert "Simulated" in context.message or "demo" in context.message.lower()


def test_simulated_no_fake_live_flag():
    provider = SimulatedSAPProvider()
    context = provider.get_context()
    assert context.source_mode != SourceMode.LIVE


def test_get_role_context_data_analyst():
    provider = SimulatedSAPProvider()
    job = provider.get_role_context("data-analyst-junior")
    assert job is not None
    assert job.title == "Junior Data Analyst"


def test_external_candidate_empty_sap_skills():
    provider = SimulatedSAPProvider()
    skills = provider.get_employee_skills("ananya-sharma")
    assert skills == []


def test_learning_and_opportunities_simulated():
    provider = SimulatedSAPProvider()
    items = provider.get_learning_items()
    opps = provider.get_opportunities()
    assert len(items) >= 1
    assert len(opps) >= 1
    assert all(
        i.source_mode in {SourceMode.SYNTHETIC, SourceMode.SIMULATED} for i in items
    )


def test_live_provider_not_connected():
    live = LiveSAPProvider()
    ctx = live.get_context()
    assert ctx.source_mode == SourceMode.NOT_CONNECTED
    assert ctx.source_mode != SourceMode.LIVE
    assert ctx.integration_status == IntegrationStatus.UNAVAILABLE
    assert ctx.message
