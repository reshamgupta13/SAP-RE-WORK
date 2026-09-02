"""Tests for prototype catalog fallback when only skills OData is configured."""

from unittest.mock import MagicMock, patch

from app.services.sap_catalog_service import SAPCatalogService


def test_list_candidates_uses_prototype_when_user_not_configured():
    mock_provider = MagicMock()
    mock_provider.is_live_verified.return_value = True
    mock_provider.get_context.return_value = MagicMock(
        source_mode=MagicMock(value="LIVE"),
        message="ok",
        integration_status=MagicMock(),
        retrieved_entities=["skill"],
        system_name="sap",
    )
    mock_provider.get_diagnostics.return_value = {
        "entity_status": {"skill": "AVAILABLE", "user": "PENDING_OFFICIAL_ODATA_METADATA"},
        "entity_counts": {"skill": 6},
        "write_available": False,
        "traces": [],
    }
    mock_provider.list_domain.side_effect = NotImplementedError("no user")

    with patch("app.services.sap_catalog_service.get_settings") as mock_settings:
        mock_settings.return_value = MagicMock(
            sap_mode="LIVE",
            sap_prototype_fallback=True,
            sap_entity_user=None,
            sap_entity_person=None,
            sap_entity_job=None,
            sap_entity_person_skill=None,
            sap_entity_qualification=None,
            sap_entity_job_skill=None,
            sap_entity_organization=None,
            sap_entity_hr=None,
            sap_odata_base_url="https://sap.example/skill",
            sap_api_url=None,
            sap_auth_mode="BASIC",
            sap_username="u",
            sap_password="p",
            sap_client_id=None,
            sap_client_secret=None,
        )
        service = SAPCatalogService(provider=mock_provider)
        data = service.list_candidates()

    assert data["count"] == 3
    assert data["hybrid_mode"] is True
    assert data["items"][0]["user_id"] == "USER001"


def test_list_jobs_uses_prototype_when_job_not_configured():
    mock_provider = MagicMock()
    mock_provider.is_live_verified.return_value = True

    with patch("app.services.sap_catalog_service.get_settings") as mock_settings:
        mock_settings.return_value = MagicMock(
            sap_mode="LIVE",
            sap_prototype_fallback=True,
            sap_entity_user=None,
            sap_entity_person=None,
            sap_entity_job=None,
            sap_entity_person_skill=None,
            sap_entity_qualification=None,
            sap_entity_job_skill=None,
            sap_entity_organization=None,
            sap_entity_hr=None,
        )
        service = SAPCatalogService(provider=mock_provider)
        with patch.object(service, "_ensure_live", return_value=(mock_provider, {"live_verified": True, "source_mode": "LIVE"})):
            data = service.list_jobs()

    assert data["count"] == 3
    assert data["items"][0]["job_id"] == "JOB001"
