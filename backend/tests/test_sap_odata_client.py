"""SAP OData client contract tests — HTTP layer mocked, no real SAP required."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import httpx
import pytest

from app.adapters.sap.mapper import SAPMapper
from app.adapters.sap.odata_client import (
    ODataAuthError,
    ODataMalformedError,
    ODataNotFoundError,
    ODataTimeoutError,
    SAPODataClient,
)
from app.adapters.sap.odata_config import EntityMapping, ODataAccessPlan
from app.adapters.sap.provenance import sap_provenance
from app.domain.enums import SourceMode

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures" / "sap" / "odata"


def _plan() -> ODataAccessPlan:
    return ODataAccessPlan(
        service_name="TestService",
        entity_mappings=[
            EntityMapping("person", "PersonSet", "CandidateProfile"),
            EntityMapping("job", "JobSet", "JobProfile"),
            EntityMapping("qualification", "QualificationSet", "CandidateCapability"),
        ],
    )


def test_metadata_success():
    xml = (FIXTURES / "metadata.xml").read_text(encoding="utf-8")
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = xml

    with patch("httpx.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.get.return_value = mock_resp
        mock_client_cls.return_value = mock_client

        client = SAPODataClient("https://sap.example/odata/v4", access_plan=_plan())
        meta = client.fetch_metadata(use_cache=False)

    assert "PersonSet" in meta.entity_sets
    assert "JobSet" in meta.entity_sets


def test_metadata_failure_404():
    mock_resp = MagicMock()
    mock_resp.status_code = 404

    with patch("httpx.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.get.return_value = mock_resp
        mock_client_cls.return_value = mock_client

        client = SAPODataClient("https://sap.example/odata/v4", access_plan=_plan())
        with pytest.raises(ODataNotFoundError):
            client.fetch_metadata(use_cache=False)


def test_metadata_malformed_xml():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = "not xml"

    with patch("httpx.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.get.return_value = mock_resp
        mock_client_cls.return_value = mock_client

        client = SAPODataClient("https://sap.example/odata/v4", access_plan=_plan())
        with pytest.raises(ODataMalformedError):
            client.fetch_metadata(use_cache=False)


def test_collection_success():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"value": [{"id": "p1", "displayName": "Test"}]}

    with patch("httpx.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.get.return_value = mock_resp
        mock_client_cls.return_value = mock_client

        client = SAPODataClient("https://sap.example/odata/v4", access_plan=_plan())
        result = client.get_collection("PersonSet")

    assert result.count == 1
    assert result.values[0]["displayName"] == "Test"


def test_collection_empty():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"value": []}

    with patch("httpx.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.get.return_value = mock_resp
        mock_client_cls.return_value = mock_client

        client = SAPODataClient("https://sap.example/odata/v4", access_plan=_plan())
        result = client.get_collection("PersonSet")

    assert result.count == 0


def test_collection_malformed():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"unexpected": True}

    with patch("httpx.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.get.return_value = mock_resp
        mock_client_cls.return_value = mock_client

        client = SAPODataClient("https://sap.example/odata/v4", access_plan=_plan())
        with pytest.raises(ODataMalformedError):
            client.get_collection("PersonSet")


def test_unauthorized():
    mock_resp = MagicMock()
    mock_resp.status_code = 401

    with patch("httpx.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.get.return_value = mock_resp
        mock_client_cls.return_value = mock_client

        client = SAPODataClient("https://sap.example/odata/v4", access_plan=_plan())
        with pytest.raises(ODataAuthError):
            client.get_collection("PersonSet")


def test_forbidden():
    mock_resp = MagicMock()
    mock_resp.status_code = 403

    with patch("httpx.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.get.return_value = mock_resp
        mock_client_cls.return_value = mock_client

        client = SAPODataClient("https://sap.example/odata/v4", access_plan=_plan())
        with pytest.raises(ODataAuthError):
            client.get_collection("PersonSet")


def test_timeout():
    with patch("httpx.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.get.side_effect = httpx.TimeoutException("timeout")
        mock_client_cls.return_value = mock_client

        client = SAPODataClient("https://sap.example/odata/v4", access_plan=_plan())
        with pytest.raises(ODataTimeoutError):
            client.get_collection("PersonSet")


def test_entity_not_in_allowlist():
    client = SAPODataClient("https://sap.example/odata/v4", access_plan=_plan())
    with pytest.raises(ValueError, match="allow-list"):
        client.get_collection("ArbitraryEntity")


def test_validate_expected_entities():
    xml = (FIXTURES / "metadata.xml").read_text(encoding="utf-8")
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = xml

    with patch("httpx.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.get.return_value = mock_resp
        mock_client_cls.return_value = mock_client

        client = SAPODataClient("https://sap.example/odata/v4", access_plan=_plan())
        status = client.validate_expected_entities()

    assert status["person"] == "AVAILABLE"
    assert status["job"] == "AVAILABLE"


def test_provenance_fields():
    prov = sap_provenance(
        entity_set="PersonSet",
        object_id="50004318",
        source_mode=SourceMode.LIVE,
        service="TestService",
        mapped_to="CandidateProfile",
    )
    assert prov["source"] == "SAP"
    assert prov["source_mode"] == "LIVE"
    assert prov["entity_set"] == "PersonSet"
    assert prov["object_id"] == "50004318"


def test_mapper_employee_context():
    raw = {"userId": "u1", "displayName": "Ananya", "department": "Analytics"}
    mapped = SAPMapper.map_employee_context(raw, SourceMode.LIVE, entity_set="PersonSet")
    assert mapped["employee_id"] == "u1"
    assert mapped["provenance"]["entity_set"] == "PersonSet"


def test_live_provider_not_connected_without_url():
    from app.adapters.sap.live import LiveSAPProvider

    live = LiveSAPProvider()
    ctx = live.get_context()
    assert ctx.source_mode == SourceMode.NOT_CONNECTED
    assert ctx.source_mode != SourceMode.LIVE
