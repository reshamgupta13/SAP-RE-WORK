"""SAP OData HTTP client — transport only, no business reasoning.

Supports OData V2 (`d.results`) and V4 (`value`). CSRF tokens stay on the
server-side client. The SAP base URL is configuration-only (no SSRF from callers).
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlencode, urljoin

import httpx

from app.adapters.sap.odata_config import ODataAccessPlan, build_access_plan

_ENTITY_SET_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_.]*$")
_KEY_RE = re.compile(r"^[A-Za-z0-9_.'=, \-]+$")
_SAFE_QUERY = {"$top", "$skip", "$filter", "$select", "$expand", "$orderby", "$format", "$inlinecount"}

READABLE_STATUS: dict[int, str] = {
    400: "SAP rejected the request because the payload was invalid.",
    401: "SAP authentication failed.",
    403: "SAP denied this operation.",
    404: "SAP rejected the request because the record no longer exists.",
    405: "Write operation is not available in the current SAP service.",
    409: "SAP reported a conflict. Refresh the record and try again.",
    412: "The record changed since it was loaded. Refresh before saving.",
    429: "SAP is rate-limiting requests. Try again shortly.",
    501: "Write operation is not available in the current SAP service.",
}


class ODataError(Exception):
    """Base OData client error."""

    def __init__(self, message: str, status_code: int | None = None, *, user_message: str | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.user_message = user_message or (READABLE_STATUS.get(status_code or 0) if status_code else message)


class ODataAuthError(ODataError):
    """401/403 authentication or authorization failure."""


class ODataNotFoundError(ODataError):
    """404 — service or entity not found."""


class ODataTimeoutError(ODataError):
    """Request timed out."""


class ODataMalformedError(ODataError):
    """Malformed JSON/XML response."""


class ODataConflictError(ODataError):
    """409 / 412 stale or conflicting data."""


class ODataWriteNotSupportedError(ODataError):
    """405 / 501 — mutation not exposed by the service."""


@dataclass
class ODataEntityType:
    name: str
    keys: list[str] = field(default_factory=list)
    properties: dict[str, str] = field(default_factory=dict)


@dataclass
class ODataMetadata:
    """Parsed metadata summary."""

    entity_sets: list[str] = field(default_factory=list)
    entity_set_types: dict[str, str] = field(default_factory=dict)
    entity_types: dict[str, ODataEntityType] = field(default_factory=dict)
    raw_xml: str | None = None
    retrieved_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def keys_for_entity_set(self, entity_set: str) -> list[str]:
        type_name = self.entity_set_types.get(entity_set)
        if not type_name:
            return []
        short = type_name.split(".")[-1]
        et = self.entity_types.get(type_name) or self.entity_types.get(short)
        return list(et.keys) if et else []


@dataclass
class ODataCollectionResult:
    """Result of a collection GET."""

    entity_set: str
    values: list[dict[str, Any]]
    count: int
    retrieved_at: datetime
    raw_shape: str = "v4"


@dataclass
class ODataMutationResult:
    entity_set: str
    operation: str
    status_code: int
    body: dict[str, Any] | None
    retrieved_at: datetime


def format_odata_key(key: str | dict[str, Any]) -> str:
    """Build a Gateway-safe key predicate. Does not invent property names."""
    if isinstance(key, dict):
        parts: list[str] = []
        for name, value in key.items():
            if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", str(name)):
                raise ValueError(f"Invalid OData key field: {name}")
            parts.append(f"{name}={_literal(value)}")
        return ",".join(parts)
    return str(key)


def _literal(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return str(value)
    text = str(value).replace("'", "''")
    if text.isdigit():
        return text
    return f"'{text}'"


def unwrap_odata_entity(body: Any) -> dict[str, Any]:
    if not isinstance(body, dict):
        raise ODataMalformedError("Expected JSON object for entity")
    if isinstance(body.get("d"), dict) and "results" not in body["d"]:
        return {k: v for k, v in body["d"].items() if not str(k).startswith("__")}
    return {k: v for k, v in body.items() if k not in {"d", "@odata.context"} and not str(k).startswith("__")}


def unwrap_odata_collection(body: Any) -> tuple[list[dict[str, Any]], str]:
    if not isinstance(body, dict):
        raise ODataMalformedError("Expected JSON object for collection")
    if isinstance(body.get("value"), list):
        values = [v for v in body["value"] if isinstance(v, dict)]
        return values, "v4"
    inner = body.get("d")
    if isinstance(inner, dict) and isinstance(inner.get("results"), list):
        values = [v for v in inner["results"] if isinstance(v, dict)]
        return values, "v2"
    if isinstance(inner, list):
        values = [v for v in inner if isinstance(v, dict)]
        return values, "v2"
    raise ODataMalformedError("Expected 'value' array or OData V2 d.results")


class SAPODataClient:
    """OData client with allow-list enforcement, CSRF, and query safety."""

    def __init__(
        self,
        base_url: str,
        *,
        metadata_url: str | None = None,
        timeout_seconds: float = 15.0,
        auth_headers: dict[str, str] | None = None,
        access_plan: ODataAccessPlan | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._metadata_url = metadata_url or f"{self._base_url}/$metadata"
        self._timeout = timeout_seconds
        self._auth_headers = auth_headers or {}
        self._access_plan = access_plan or build_access_plan()
        self._metadata_cache: ODataMetadata | None = None
        self._metadata_cached_at: datetime | None = None
        self._cookies = httpx.Cookies()
        self._csrf_token: str | None = None

    @property
    def base_url(self) -> str:
        return self._base_url

    @property
    def metadata_url(self) -> str:
        return self._metadata_url

    def _client(self, extra_headers: dict[str, str] | None = None) -> httpx.Client:
        headers = {
            **self._auth_headers,
            "Accept": "application/json",
            **(extra_headers or {}),
        }
        return httpx.Client(
            timeout=self._timeout,
            headers=headers,
            cookies=self._cookies,
            follow_redirects=True,
        )

    def _remember_cookies(self, resp: httpx.Response) -> None:
        try:
            self._cookies.update(resp.cookies)
        except Exception:
            pass
        token = resp.headers.get("x-csrf-token") or resp.headers.get("X-CSRF-Token")
        if token and token.lower() != "required":
            self._csrf_token = token

    def _raise_for_status(self, resp: httpx.Response, *, write: bool = False) -> None:
        code = resp.status_code
        user = READABLE_STATUS.get(code)
        if code in {401, 403}:
            raise ODataAuthError(f"SAP OData auth failed ({code})", code, user_message=user)
        if code == 404:
            raise ODataNotFoundError(
                f"SAP OData not found ({code})",
                code,
                user_message=user or "SAP rejected the request because the record no longer exists.",
            )
        if code in {409, 412}:
            raise ODataConflictError(f"SAP OData conflict ({code})", code, user_message=user)
        if write and code in {405, 501}:
            raise ODataWriteNotSupportedError(
                f"SAP OData write not supported ({code})",
                code,
                user_message=READABLE_STATUS[405],
            )
        if code == 429:
            raise ODataError(f"SAP OData rate limited ({code})", code, user_message=user)
        if code >= 500:
            raise ODataError(
                f"SAP OData server error ({code})",
                code,
                user_message="SAP encountered a server error.",
            )
        if code >= 400:
            raise ODataError(
                f"SAP OData request failed ({code})",
                code,
                user_message=user or "SAP rejected the request.",
            )

    def _handle_response(self, resp: httpx.Response, *, write: bool = False) -> dict[str, Any]:
        self._remember_cookies(resp)
        self._raise_for_status(resp, write=write)
        if resp.status_code in {204, 202} or not resp.content:
            return {}
        try:
            return resp.json()
        except Exception as exc:
            raise ODataMalformedError(f"Malformed JSON response: {exc}") from exc

    def _validate_entity_set(self, entity_set: str) -> None:
        if not _ENTITY_SET_RE.match(entity_set):
            raise ValueError(f"Invalid entity set name: {entity_set}")
        allowed = self._access_plan.allowed_entity_sets()
        if allowed and entity_set not in allowed:
            raise ValueError(f"Entity set not in allow-list: {entity_set}")

    def _validate_key(self, key: str) -> None:
        if not _KEY_RE.match(key):
            raise ValueError(f"Invalid OData key: {key}")

    def _build_url(self, entity_set: str, key: str | None = None, params: dict[str, str] | None = None) -> str:
        self._validate_entity_set(entity_set)
        if key:
            formatted = format_odata_key(key) if not isinstance(key, str) else key
            self._validate_key(formatted)
            path = f"{entity_set}({formatted})"
        else:
            path = entity_set
        url = urljoin(f"{self._base_url}/", path)
        if params:
            safe = {k: v for k, v in params.items() if k in _SAFE_QUERY}
            if safe:
                url = f"{url}?{urlencode(safe)}"
        return url

    def fetch_metadata(self, *, use_cache: bool = True) -> ODataMetadata:
        if use_cache and self._metadata_cache and self._metadata_cached_at:
            age = (datetime.now(timezone.utc) - self._metadata_cached_at).total_seconds()
            if age < 300:
                return self._metadata_cache

        try:
            with self._client({"Accept": "application/xml"}) as client:
                resp = client.get(self._metadata_url)
        except httpx.TimeoutException as exc:
            raise ODataTimeoutError("Metadata request timed out") from exc
        except httpx.HTTPError as exc:
            raise ODataError(f"Metadata network error: {exc}") from exc

        self._remember_cookies(resp)
        if resp.status_code == 401 or resp.status_code == 403:
            raise ODataAuthError(f"Metadata auth failed ({resp.status_code})", resp.status_code)
        if resp.status_code == 404:
            raise ODataNotFoundError(f"Metadata not found ({resp.status_code})", resp.status_code)
        if resp.status_code >= 400:
            raise ODataError(f"Metadata request failed ({resp.status_code})", resp.status_code)

        raw = resp.text
        meta = self._parse_metadata(raw)
        self._metadata_cache = meta
        self._metadata_cached_at = datetime.now(timezone.utc)
        return meta

    @classmethod
    def _parse_metadata(cls, xml_text: str) -> ODataMetadata:
        try:
            root = ET.fromstring(xml_text)
        except ET.ParseError as exc:
            raise ODataMalformedError(f"Malformed metadata XML: {exc}") from exc

        entity_types: dict[str, ODataEntityType] = {}
        entity_sets: list[str] = []
        entity_set_types: dict[str, str] = {}

        for elem in root.iter():
            tag = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
            if tag == "EntityType":
                name = elem.get("Name")
                if not name:
                    continue
                keys: list[str] = []
                props: dict[str, str] = {}
                for child in elem.iter():
                    ctag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
                    if ctag == "PropertyRef":
                        ref = child.get("Name")
                        if ref:
                            keys.append(ref)
                    if ctag == "Property":
                        pname = child.get("Name")
                        if pname:
                            props[pname] = child.get("Type") or "Edm.String"
                entity_types[name] = ODataEntityType(name=name, keys=keys, properties=props)
            if tag == "EntitySet":
                name = elem.get("Name")
                if name:
                    entity_sets.append(name)
                    etype = elem.get("EntityType")
                    if etype:
                        entity_set_types[name] = etype

        return ODataMetadata(
            entity_sets=sorted(set(entity_sets)),
            entity_set_types=entity_set_types,
            entity_types=entity_types,
            raw_xml=xml_text,
        )

    def get_collection(
        self,
        entity_set: str,
        *,
        params: dict[str, str] | None = None,
        max_top: int = 100,
    ) -> ODataCollectionResult:
        safe_params = dict(params or {})
        if "$top" in safe_params:
            try:
                top = min(int(safe_params["$top"]), max_top)
                safe_params["$top"] = str(top)
            except ValueError:
                safe_params["$top"] = str(max_top)
        else:
            safe_params["$top"] = str(max_top)

        url = self._build_url(entity_set, params=safe_params)
        try:
            with self._client() as client:
                resp = client.get(url)
        except httpx.TimeoutException as exc:
            raise ODataTimeoutError(f"Collection read timed out: {entity_set}") from exc
        except httpx.HTTPError as exc:
            raise ODataError(f"Collection network error: {exc}") from exc

        body = self._handle_response(resp)
        values, shape = unwrap_odata_collection(body)
        return ODataCollectionResult(
            entity_set=entity_set,
            values=values,
            count=len(values),
            retrieved_at=datetime.now(timezone.utc),
            raw_shape=shape,
        )

    def get_by_key(self, entity_set: str, key: str | dict[str, Any]) -> dict[str, Any]:
        formatted = format_odata_key(key)
        url = self._build_url(entity_set, key=formatted)
        try:
            with self._client() as client:
                resp = client.get(url)
        except httpx.TimeoutException as exc:
            raise ODataTimeoutError(f"Entity read timed out: {entity_set}({formatted})") from exc
        except httpx.HTTPError as exc:
            raise ODataError(f"Entity network error: {exc}") from exc

        body = self._handle_response(resp)
        return unwrap_odata_entity(body)

    def fetch_csrf_token(self, *, force: bool = False) -> str:
        if self._csrf_token and not force:
            return self._csrf_token
        headers = {"X-CSRF-Token": "Fetch", "Accept": "application/json"}
        try:
            with self._client(headers) as client:
                resp = client.get(self._base_url)
                self._remember_cookies(resp)
                if not self._csrf_token:
                    resp = client.get(self._metadata_url, headers={**headers, "Accept": "application/xml"})
                    self._remember_cookies(resp)
        except httpx.TimeoutException as exc:
            raise ODataTimeoutError("CSRF token request timed out") from exc
        except httpx.HTTPError as exc:
            raise ODataError(f"CSRF token network error: {exc}") from exc

        if not self._csrf_token:
            raise ODataAuthError(
                "SAP CSRF token was not returned",
                403,
                user_message="SAP denied this operation.",
            )
        return self._csrf_token

    def _mutate(
        self,
        method: str,
        entity_set: str,
        *,
        key: str | dict[str, Any] | None = None,
        payload: dict[str, Any] | None = None,
        merge: bool = False,
    ) -> ODataMutationResult:
        formatted = format_odata_key(key) if key is not None else None
        url = self._build_url(entity_set, key=formatted)
        token = self.fetch_csrf_token()
        headers = {
            "X-CSRF-Token": token,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if merge and method.upper() == "POST":
            headers["X-HTTP-Method"] = "MERGE"
        if merge and method.upper() in {"PATCH", "PUT", "MERGE"}:
            headers["X-HTTP-Method"] = "MERGE"

        http_method = "POST" if method.upper() == "MERGE" else method.upper()

        def _send() -> httpx.Response:
            with self._client(headers) as client:
                return client.request(http_method, url, json=payload if payload is not None else None)

        try:
            resp = _send()
        except httpx.TimeoutException as exc:
            raise ODataTimeoutError(f"{method} timed out: {entity_set}") from exc
        except httpx.HTTPError as exc:
            raise ODataError(f"{method} network error: {exc}") from exc

        if resp.status_code == 403 and "csrf" in (resp.text or "").lower():
            token = self.fetch_csrf_token(force=True)
            headers["X-CSRF-Token"] = token
            try:
                resp = _send()
            except httpx.TimeoutException as exc:
                raise ODataTimeoutError(f"{method} timed out: {entity_set}") from exc

        body = self._handle_response(resp, write=True)
        entity = unwrap_odata_entity(body) if body else {}
        return ODataMutationResult(
            entity_set=entity_set,
            operation=method.upper(),
            status_code=resp.status_code,
            body=entity or None,
            retrieved_at=datetime.now(timezone.utc),
        )

    def create_entity(self, entity_set: str, payload: dict[str, Any]) -> ODataMutationResult:
        return self._mutate("POST", entity_set, payload=payload)

    def update_entity(
        self,
        entity_set: str,
        key: str | dict[str, Any],
        payload: dict[str, Any],
        *,
        merge: bool = True,
    ) -> ODataMutationResult:
        method = "MERGE" if merge else "PUT"
        return self._mutate(method, entity_set, key=key, payload=payload, merge=merge)

    def delete_entity(self, entity_set: str, key: str | dict[str, Any]) -> ODataMutationResult:
        return self._mutate("DELETE", entity_set, key=key)

    def validate_expected_entities(self) -> dict[str, str]:
        """Check which configured entity sets exist in metadata."""
        meta = self.fetch_metadata()
        discovered = set(meta.entity_sets)
        result: dict[str, str] = {}
        for mapping in self._access_plan.entity_mappings:
            if not mapping.entity_set:
                result[mapping.domain] = "PENDING_OFFICIAL_ODATA_METADATA"
            elif mapping.entity_set in discovered:
                result[mapping.domain] = "AVAILABLE"
            else:
                result[mapping.domain] = "MISSING"
        return result
