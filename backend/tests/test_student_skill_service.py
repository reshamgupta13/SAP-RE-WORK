"""Tests for student skill workspace service."""

from unittest.mock import MagicMock, patch

from app.services.student_skill_service import StudentSkillService


def test_connection_info_configured():
    with patch("app.services.student_skill_service.get_settings") as mock_settings:
        mock_settings.return_value = MagicMock(
            sap_mode="LIVE",
            sap_odata_base_url="https://sap.example/odata/sap/ZREWORK_SKILL_SRV",
            sap_odata_service="ZREWORK_SKILL_SRV",
            sap_entity_skill="ZREWORK_skillSet",
        )
        info = StudentSkillService().connection_info()
    assert info["configured"] is True
    assert "ZREWORK_skillSet" in info["entity_set_url"]


def test_get_all_parses_results():
    body = '{"d":{"results":[{"SkillId":"SKILL0001","SkillName":"JAVA","Description":"JAVA"}]}}'
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.read.return_value = body.encode()
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)

    with patch("app.services.student_skill_service.get_settings") as mock_settings, patch(
        "app.services.student_skill_service._auth_header", return_value="auth"
    ), patch("app.services.student_skill_service._entity_set_url", return_value="https://sap.example/set"), patch(
        "urllib.request.OpenerDirector.open", return_value=mock_resp
    ):
        mock_settings.return_value = MagicMock()
        result = StudentSkillService().get_all()

    assert result["ok"] is True
    assert result["item"]["records"][0]["SkillName"] == "JAVA"
