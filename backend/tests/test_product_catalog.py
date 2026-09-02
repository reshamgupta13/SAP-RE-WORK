"""Product catalog and seven-table mapping tests — HTTP mocked, no live SAP."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.adapters.sap.mapper import SAPMapper, normalize_proficiency
from app.adapters.sap.odata_client import ODataWriteNotSupportedError, SAPODataClient
from app.adapters.sap.odata_config import EntityMapping, ODataAccessPlan
from app.adapters.sap.seven_table_registry import build_seven_table_registry, match_entity_set
from app.domain.enums import SourceMode
from app.main import app
from app.services.sap_catalog_service import SAPCatalogService

client = TestClient(app)
FIXTURES = Path(__file__).resolve().parents[2] / "fixtures" / "sap" / "odata"


def _plan() -> ODataAccessPlan:
    return ODataAccessPlan(
        service_name="ZREWORK_SRV",
        entity_mappings=[
            EntityMapping("user", "ZREWORK_USERSet", "CandidateProfile"),
            EntityMapping("job", "ZREWORK_JOBSet", "JobProfile"),
        ],
    )


def test_seven_table_job_does_not_match_job_skill():
    discovered = ["ZREWORK_JOBSet", "ZREWORK_JOB_SKILSet", "ZREWORK_SKILLSet", "ZREWORK_PERSKILLSet"]
    registry = build_seven_table_registry(discovered)
    assert registry.binding("job").entity_set == "ZREWORK_JOBSet"
    assert registry.binding("job_skill").entity_set == "ZREWORK_JOB_SKILSet"
    assert registry.binding("skill").entity_set == "ZREWORK_SKILLSet"
    assert registry.binding("person_skill").entity_set == "ZREWORK_PERSKILLSet"


def test_match_entity_set_requires_discovered_name():
    assert match_entity_set(("ZREWORK_USER",), ["PersonSet"]) is None
    assert match_entity_set(("ZREWORK_USER",), ["ZREWORK_USERSet"]) == "ZREWORK_USERSet"


def test_odata_v2_collection():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"d": {"results": [{"USER_ID": "103", "FIRST_NAME": "Priya"}]}}
    mock_resp.content = b"{}"
    mock_resp.headers = {}
    mock_resp.cookies = {}

    with patch("httpx.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.get.return_value = mock_resp
        mock_client_cls.return_value = mock_client
        result = SAPODataClient("https://sap.example/odata/sap/ZSRV", access_plan=_plan()).get_collection(
            "ZREWORK_USERSet"
        )

    assert result.raw_shape == "v2"
    assert result.values[0]["USER_ID"] == "103"


def test_zrework_metadata_keys():
    xml = (FIXTURES / "zrework_metadata.xml").read_text(encoding="utf-8")
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = xml
    mock_resp.headers = {}
    mock_resp.cookies = {}

    with patch("httpx.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.get.return_value = mock_resp
        mock_client_cls.return_value = mock_client
        meta = SAPODataClient("https://sap.example/odata", access_plan=_plan()).fetch_metadata(use_cache=False)

    assert "ZREWORK_USERSet" in meta.entity_sets
    assert meta.keys_for_entity_set("ZREWORK_USERSet") == ["USER_ID"]


def test_csrf_create():
    fetch_resp = MagicMock()
    fetch_resp.status_code = 200
    fetch_resp.headers = {"x-csrf-token": "token-1"}
    fetch_resp.cookies = {}
    fetch_resp.content = b"{}"
    fetch_resp.json.return_value = {}
    fetch_resp.text = ""

    create_resp = MagicMock()
    create_resp.status_code = 201
    create_resp.headers = {}
    create_resp.cookies = {}
    create_resp.content = b"{}"
    create_resp.json.return_value = {"d": {"USER_ID": "201", "FIRST_NAME": "Dev"}}

    with patch("httpx.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.get.return_value = fetch_resp
        mock_client.request.return_value = create_resp
        mock_client_cls.return_value = mock_client
        result = SAPODataClient("https://sap.example/odata", access_plan=_plan()).create_entity(
            "ZREWORK_USERSet",
            {"FIRST_NAME": "Dev"},
        )

    assert result.status_code == 201
    assert result.body["USER_ID"] == "201"


def test_write_not_supported():
    fetch_resp = MagicMock()
    fetch_resp.status_code = 200
    fetch_resp.headers = {"x-csrf-token": "token-1"}
    fetch_resp.cookies = {}
    fetch_resp.content = b"{}"
    fetch_resp.json.return_value = {}
    fetch_resp.text = ""

    write_resp = MagicMock()
    write_resp.status_code = 405
    write_resp.headers = {}
    write_resp.cookies = {}
    write_resp.content = b""
    write_resp.text = ""

    with patch("httpx.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.get.return_value = fetch_resp
        mock_client.request.return_value = write_resp
        mock_client_cls.return_value = mock_client
        with pytest.raises(ODataWriteNotSupportedError):
            SAPODataClient("https://sap.example/odata", access_plan=_plan()).create_entity(
                "ZREWORK_USERSet", {"FIRST_NAME": "X"}
            )


def test_proficiency_normalization():
    assert normalize_proficiency(80) == 0.8
    assert normalize_proficiency("ADVANCED") == 0.8
    assert normalize_proficiency("not-a-score") is None
    assert normalize_proficiency(0.4) == 0.4


def test_mapper_zrework_user():
    raw = {"USER_ID": "103", "FIRST_NAME": "Priya", "LAST_NAME": "Nair", "CURRENT_ROLE": "Analyst"}
    mapped = SAPMapper.map_candidate_record(raw, SourceMode.LIVE)
    assert mapped["user_id"] == "103"
    assert mapped["display_name"] == "Priya Nair"
    assert "Ananya" not in mapped["display_name"]


def test_catalog_empty_without_live():
    data = SAPCatalogService().list_candidates()
    assert data["items"] == []
    assert data["live_verified"] is False
    joined = " ".join(str(v) for v in data.values())
    assert "Ananya" not in joined


def test_catalog_api_does_not_return_ananya():
    r = client.get("/api/catalog/candidates")
    assert r.status_code == 200
    body = r.json()
    assert body["items"] == []
    assert "Ananya" not in r.text
