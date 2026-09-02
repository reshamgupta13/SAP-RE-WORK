"""SAP source-mode provenance regression tests."""

from unittest.mock import patch

from fastapi.testclient import TestClient

from app.adapters.sap.live import LiveSAPProvider
from app.adapters.sap.simulated import SimulatedSAPProvider
from app.domain.enums import IntegrationStatus, SourceMode
from app.main import app

client = TestClient(app)


def test_simulated_provider_source_mode():
    ctx = SimulatedSAPProvider().get_context()
    assert ctx.source_mode == SourceMode.SIMULATED
    assert ctx.integration_status == IntegrationStatus.AVAILABLE


def test_live_provider_auth_failure_not_connected():
    live = LiveSAPProvider(
        odata_base_url="https://sap.example.com/odata/v4",
        api_url="https://sap.example.com",
        client_id="client",
        client_secret="secret",
        auth_mode="OAUTH2",
    )
    with patch.object(live, "verify_connection", side_effect=ConnectionError("SAP authentication failed")):
        ctx = live.get_context()
    assert ctx.source_mode == SourceMode.NOT_CONNECTED
    assert ctx.source_mode != SourceMode.LIVE
    assert ctx.integration_status == IntegrationStatus.UNAVAILABLE


def test_live_provider_missing_credentials_not_connected():
    live = LiveSAPProvider()
    ctx = live.get_context()
    assert ctx.source_mode == SourceMode.NOT_CONNECTED
    assert ctx.source_mode != SourceMode.LIVE
    assert ctx.integration_status == IntegrationStatus.UNAVAILABLE


def test_live_provider_connection_failure_not_connected():
    live = LiveSAPProvider(
        odata_base_url="https://sap.example.com/odata/v4",
        api_url="https://sap.example.com",
    )
    with patch.object(live, "verify_connection", side_effect=ConnectionError("timeout")):
        ctx = live.get_context()
    assert ctx.source_mode == SourceMode.NOT_CONNECTED
    assert ctx.source_mode != SourceMode.LIVE


def test_live_provider_successful_verification_returns_live():
    from datetime import datetime, timezone

    live = LiveSAPProvider(
        odata_base_url="https://sap.example.com/odata/v4",
        api_url="https://sap.example.com",
    )

    def _fake_verify() -> bool:
        live._verified = True
        live._data_verified = True
        live._entity_status = {"user": "AVAILABLE", "job": "PENDING_OFFICIAL_ODATA_METADATA"}
        live._last_sync = datetime.now(timezone.utc)
        return True

    with patch.object(live, "verify_connection", side_effect=_fake_verify):
        ctx = live.get_context()
    assert ctx.source_mode == SourceMode.LIVE
    assert ctx.integration_status == IntegrationStatus.AVAILABLE
    assert "user" in ctx.retrieved_entities


def test_live_provider_unexpected_error_returns_error():
    live = LiveSAPProvider(
        odata_base_url="https://sap.example.com/odata/v4",
        api_url="https://sap.example.com",
    )
    with patch.object(live, "verify_connection", side_effect=RuntimeError("unexpected")):
        ctx = live.get_context()
    assert ctx.source_mode == SourceMode.ERROR
    assert ctx.source_mode != SourceMode.LIVE


def test_health_demo_mode_never_live():
    health = client.get("/api/sap/health").json()
    assert health["source_mode"] == SourceMode.SIMULATED.value
    assert health["source_mode"] != SourceMode.LIVE.value


def test_api_context_never_claims_live_on_auth_failure():
    live = LiveSAPProvider(
        odata_base_url="https://sap.example.com/odata/v4",
        api_url="https://sap.example.com",
    )
    with patch("app.api.routes.sap.get_sap_provider", return_value=live):
        with patch.object(live, "verify_connection", side_effect=ConnectionError("failed")):
            with patch("app.api.routes.sap.SAPHealthService") as mock_health:
                mock_health.return_value.check.return_value = {
                    "configured": True,
                    "reachable": False,
                    "authenticated": False,
                    "healthy": False,
                    "source_mode": SourceMode.NOT_CONNECTED.value,
                    "fallback_reason": "connection_failed",
                }
                resp = client.get("/api/sap/context")
    body = resp.json()
    assert body["source_mode"] != SourceMode.LIVE.value
    assert body["live_connection"] is False
    assert body["source_mode"] in {SourceMode.NOT_CONNECTED.value, SourceMode.ERROR.value}


def test_fallback_does_not_silently_become_live():
    """Failed live context must not be relabeled LIVE by health aggregation."""
    live = LiveSAPProvider()
    ctx = live.get_context()
    assert ctx.source_mode in {SourceMode.NOT_CONNECTED, SourceMode.ERROR}
    assert ctx.source_mode != SourceMode.LIVE
