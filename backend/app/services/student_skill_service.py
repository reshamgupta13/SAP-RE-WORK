"""Student skill workspace — SAP CRUD via server-side credentials.

Ports the working logic from skillProject/create_skill_server.py so the
browser never holds SAP passwords or calls SAP directly.
"""

from __future__ import annotations

import base64
import http.cookiejar
import json
import ssl
import urllib.error
import urllib.request
from typing import Any

from app.core.config import get_settings

SSL_CONTEXT = ssl.create_default_context()
SSL_CONTEXT.check_hostname = False
SSL_CONTEXT.verify_mode = ssl.CERT_NONE


def _entity_set_url() -> str:
    settings = get_settings()
    base = (settings.sap_odata_base_url or "").rstrip("/")
    entity_set = settings.sap_entity_skill or "ZREWORK_skillSet"
    if not base:
        raise ValueError("SAP OData base URL is not configured.")
    return f"{base}/{entity_set}"


def _auth_header() -> str:
    settings = get_settings()
    user = settings.sap_username or settings.sap_client_id
    secret = settings.sap_password or settings.sap_client_secret
    if not user or not secret:
        raise ValueError("SAP credentials are not configured.")
    return base64.b64encode(f"{user}:{secret}".encode()).decode()


def _new_opener() -> urllib.request.OpenerDirector:
    cookie_jar = http.cookiejar.CookieJar()
    return urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(cookie_jar),
        urllib.request.HTTPSHandler(context=SSL_CONTEXT),
    )


def _key_url(base_url: str, skill_id: str) -> str:
    escaped = str(skill_id).replace("'", "''")
    return f"{base_url}('{escaped}')"


def _normalize_skill_payload(payload: dict[str, Any], *, for_create: bool = False) -> dict[str, str]:
    skill_id = str(payload.get("SkillId") or "").strip()
    skill_name = str(payload.get("SkillName") or "").strip()
    description = str(payload.get("Description") or "").strip()
    if not skill_id:
        raise ValueError("SkillId is required.")
    if for_create and not skill_name:
        raise ValueError("SkillName is required for create.")
    if for_create and not description:
        raise ValueError("Description is required for create.")
    if len(skill_id) > 100 or len(skill_name) > 100 or len(description) > 100:
        raise ValueError("SkillId, SkillName, and Description must each be 100 characters or fewer.")
    return {"SkillId": skill_id, "SkillName": skill_name, "Description": description}


def _parse_sap_error(detail: str) -> str | None:
    if not detail:
        return None
    try:
        parsed = json.loads(detail)
    except json.JSONDecodeError:
        return detail[:300] if detail else None
    error = parsed.get("error") if isinstance(parsed, dict) else None
    if not isinstance(error, dict):
        return None
    message = error.get("message")
    if isinstance(message, dict) and message.get("value"):
        return str(message["value"])
    if isinstance(message, str):
        return message
    code = error.get("code")
    return str(code) if code else None


def _result(
    ok: bool,
    log: list[str],
    detail: str = "",
    item: dict[str, Any] | None = None,
    *,
    sap_message: str | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {"ok": ok, "log": log, "detail": detail}
    if item is not None:
        payload["item"] = item
    if sap_message:
        payload["sap_message"] = sap_message
    return payload


def _fail(log: list[str], action: str, exc: urllib.error.HTTPError) -> dict[str, Any]:
    detail = exc.read().decode(errors="replace")
    sap_message = _parse_sap_error(detail)
    lines = log + [f"{action} failed: HTTP {exc.code} {exc.reason}"]
    if sap_message:
        lines.append(f"SAP message: {sap_message}")
        if exc.code == 400:
            lines.append("Tip: SkillId may already exist — try Get all, then use a new ID like SKILL0010.")
    return _result(False, lines, detail, sap_message=sap_message)


def _get_csrf_token(
    opener: urllib.request.OpenerDirector,
    base_url: str,
    auth: str,
    log: list[str],
) -> tuple[str | None, list[str], str | None]:
    log.append(f"Step 1: GET {base_url}?$format=json")
    req = urllib.request.Request(
        base_url + "?$format=json",
        headers={
            "X-CSRF-Token": "Fetch",
            "Accept": "application/json",
            "Authorization": f"Basic {auth}",
        },
    )
    try:
        with opener.open(req, timeout=20) as resp:
            token = resp.headers.get("x-csrf-token")
            status = resp.status
    except urllib.error.HTTPError as exc:
        return None, log + [f"Token request failed: HTTP {exc.code} {exc.reason}"], exc.read().decode(errors="replace")
    except Exception as exc:
        return None, log + [f"Token request failed: {exc}"], ""

    log.append(f"Response status: {status}")
    if not token:
        return None, log + ["No X-CSRF-Token header came back in the response."], ""
    log.append(f"Token received: {token}")
    return token, log, None


class StudentSkillService:
    def connection_info(self) -> dict[str, Any]:
        settings = get_settings()
        try:
            url = _entity_set_url()
            configured = bool(url and settings.sap_username and settings.sap_password)
            return {
                "configured": configured,
                "entity_set_url": url,
                "service": settings.sap_odata_service,
                "entity_set": settings.sap_entity_skill,
                "note": "Student SAP lab uses OData credentials directly; independent of product catalog SAP_MODE.",
            }
        except ValueError as exc:
            return {"configured": False, "message": str(exc)}

    def get_all(self) -> dict[str, Any]:
        base_url = _entity_set_url()
        auth = _auth_header()
        opener = _new_opener()
        url = f"{base_url}?$format=json"
        log = [f"GET {url}"]
        req = urllib.request.Request(
            url,
            headers={"Accept": "application/json", "Authorization": f"Basic {auth}"},
        )
        try:
            with opener.open(req, timeout=20) as resp:
                body = resp.read().decode(errors="replace")
                log.append(f"Response status: {resp.status}")
                parsed = json.loads(body)
                records = (parsed.get("d") or {}).get("results") if isinstance(parsed.get("d"), dict) else []
                if not isinstance(records, list):
                    records = []
                items = [
                    {
                        "SkillId": r.get("SkillId"),
                        "SkillName": r.get("SkillName"),
                        "Description": r.get("Description"),
                    }
                    for r in records
                    if isinstance(r, dict)
                ]
                return _result(True, log + [f"Received {len(items)} record(s)."], body, item={"records": items})
        except urllib.error.HTTPError as exc:
            return _fail(log, "Get all", exc)
        except Exception as exc:
            return _result(False, log + [f"Get all failed: {exc}"], "")

    def get_one(self, skill_id: str) -> dict[str, Any]:
        if not skill_id:
            return _result(False, ["Payload is missing SkillId — can't build the entity key URL."], "")
        base_url = _entity_set_url()
        auth = _auth_header()
        opener = _new_opener()
        url = _key_url(base_url, skill_id) + "?$format=json"
        log = [f"GET {url}"]
        req = urllib.request.Request(
            url,
            headers={"Accept": "application/json", "Authorization": f"Basic {auth}"},
        )
        try:
            with opener.open(req, timeout=20) as resp:
                body = resp.read().decode(errors="replace")
                log.append(f"Response status: {resp.status}")
                parsed = json.loads(body)
                record = parsed.get("d") if isinstance(parsed.get("d"), dict) else parsed
                return _result(True, log, body, item=record if isinstance(record, dict) else None)
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                detail = exc.read().decode(errors="replace")
                return _result(False, log + [f"Skill {skill_id} not found."], detail)
            return _fail(log, "Get", exc)
        except Exception as exc:
            return _result(False, log + [f"Get failed: {exc}"], "")

    def create(self, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            normalized = _normalize_skill_payload(payload, for_create=True)
        except ValueError as exc:
            return _result(False, [str(exc)], sap_message=str(exc))

        existing = self.get_one(normalized["SkillId"])
        if existing.get("ok") and existing.get("item"):
            msg = f"SkillId {normalized['SkillId']} already exists. Use Update or pick a new ID."
            return _result(False, [msg], sap_message=msg)

        base_url = _entity_set_url()
        auth = _auth_header()
        opener = _new_opener()
        log: list[str] = []
        token, log, err_detail = _get_csrf_token(opener, base_url, auth, log)
        if not token:
            return _result(False, log, err_detail or "")

        body_bytes = json.dumps(normalized).encode()
        log.append(f"Step 2: POST {base_url}")
        log.append(json.dumps(normalized, indent=2))
        req = urllib.request.Request(
            base_url,
            data=body_bytes,
            method="POST",
            headers={
                "X-CSRF-Token": token,
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Basic {auth}",
            },
        )
        try:
            with opener.open(req, timeout=20) as resp:
                resp_body = resp.read().decode(errors="replace")
                return _result(True, log + [f"Response status: {resp.status}", "Skill created successfully."], resp_body)
        except urllib.error.HTTPError as exc:
            return _fail(log, "Create", exc)
        except Exception as exc:
            return _result(False, log + [f"Create failed: {exc}"], "")

    def update(self, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            normalized = _normalize_skill_payload(payload)
        except ValueError as exc:
            return _result(False, [str(exc)], sap_message=str(exc))

        skill_id = normalized["SkillId"]
        base_url = _entity_set_url()
        auth = _auth_header()
        opener = _new_opener()
        log: list[str] = []
        token, log, err_detail = _get_csrf_token(opener, base_url, auth, log)
        if not token:
            return _result(False, log, err_detail or "")

        url = _key_url(base_url, skill_id)
        body_bytes = json.dumps(normalized).encode()
        log.append(f"Step 2: PUT {url}")
        log.append(json.dumps(normalized, indent=2))
        req = urllib.request.Request(
            url,
            data=body_bytes,
            method="PUT",
            headers={
                "X-CSRF-Token": token,
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Basic {auth}",
            },
        )
        try:
            with opener.open(req, timeout=20) as resp:
                resp_body = resp.read().decode(errors="replace") if resp.status != 204 else ""
                return _result(True, log + [f"Response status: {resp.status}", "Skill updated successfully."], resp_body)
        except urllib.error.HTTPError as exc:
            return _fail(log, "Update", exc)
        except Exception as exc:
            return _result(False, log + [f"Update failed: {exc}"], "")

    def delete(self, skill_id: str) -> dict[str, Any]:
        if not skill_id:
            return _result(False, ["Payload is missing SkillId — can't build the entity key URL."], "")
        base_url = _entity_set_url()
        auth = _auth_header()
        opener = _new_opener()
        log: list[str] = []
        token, log, err_detail = _get_csrf_token(opener, base_url, auth, log)
        if not token:
            return _result(False, log, err_detail or "")

        url = _key_url(base_url, skill_id)
        log.append(f"Step 2: DELETE {url}")
        req = urllib.request.Request(
            url,
            method="DELETE",
            headers={
                "X-CSRF-Token": token,
                "Accept": "application/json",
                "Authorization": f"Basic {auth}",
            },
        )
        try:
            with opener.open(req, timeout=20) as resp:
                return _result(True, log + [f"Response status: {resp.status}", f"Skill {skill_id} deleted successfully."], "")
        except urllib.error.HTTPError as exc:
            return _fail(log, "Delete", exc)
        except Exception as exc:
            return _result(False, log + [f"Delete failed: {exc}"], "")
