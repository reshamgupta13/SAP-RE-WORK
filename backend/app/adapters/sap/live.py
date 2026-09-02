"""Live SAP provider — OData-backed when verified; never fakes LIVE."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import httpx

from app.adapters.sap.mapper import SAPMapper
from app.adapters.sap.odata_client import (
    ODataAuthError,
    ODataError,
    ODataNotFoundError,
    ODataTimeoutError,
    ODataWriteNotSupportedError,
    SAPODataClient,
)
from app.adapters.sap.odata_config import build_access_plan
from app.adapters.sap.provider import SAPProvider
from app.adapters.sap.provenance import sap_provenance
from app.adapters.sap.seven_table_registry import build_seven_table_registry
from app.core.config import get_settings
from app.domain.candidate import CandidateCapability
from app.domain.enums import IntegrationStatus, SourceMode
from app.domain.job import JobProfile
from app.domain.pathway import LearningItem, Opportunity
from app.domain.sap import SAPContext


class LiveSAPProvider(SAPProvider):
    """
    Live SAP integration via OData.
    LIVE is only reported after metadata verification AND at least one data GET.
    """

    def __init__(
        self,
        api_url: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
        company_id: str | None = None,
        odata_base_url: str | None = None,
        odata_metadata_url: str | None = None,
        timeout_seconds: float = 15.0,
        auth_mode: str = "NONE",
        username: str | None = None,
        password: str | None = None,
    ) -> None:
        self._api_url = (api_url or "").rstrip("/")
        self._client_id = client_id
        self._client_secret = client_secret
        self._company_id = company_id
        self._username = username
        self._password = password
        self._odata_base_url = (odata_base_url or api_url or "").rstrip("/")
        self._odata_metadata_url = odata_metadata_url
        self._timeout = timeout_seconds
        self._auth_mode = (auth_mode or "NONE").upper()
        self._mapper = SAPMapper()
        self._access_plan = build_access_plan()
        self._client: SAPODataClient | None = None
        self._verified = False
        self._data_verified = False
        self._last_sync: datetime | None = None
        self._entity_status: dict[str, str] = {}
        self._entity_counts: dict[str, int] = {}
        self._last_error: str | None = None
        self._write_available: bool | None = None
        self._write_reason: str | None = None
        self._traces: list[dict[str, Any]] = []

    def _failure_source_mode(self, exc: Exception) -> SourceMode:
        if isinstance(exc, (ConnectionError, NotImplementedError, ODataAuthError)):
            return SourceMode.NOT_CONNECTED
        if isinstance(exc, (ODataTimeoutError, ODataNotFoundError)):
            return SourceMode.NOT_CONNECTED
        return SourceMode.ERROR

    def _auth_headers(self) -> dict[str, str]:
        if self._auth_mode == "OAUTH2":
            token = self._authenticate_oauth()
            return {"Authorization": f"Bearer {token}"}
        if self._auth_mode == "BASIC":
            user = self._username or self._client_id
            secret = self._password or self._client_secret
            if not user or not secret:
                return {}
            import base64

            creds = base64.b64encode(f"{user}:{secret}".encode()).decode()
            return {"Authorization": f"Basic {creds}"}
        return {}

    def _authenticate_oauth(self) -> str:
        if not self._api_url or not self._client_id or not self._client_secret:
            raise NotImplementedError("OAuth credentials incomplete.")
        token_url = f"{self._api_url}/oauth/token"
        try:
            with httpx.Client(timeout=self._timeout) as client:
                resp = client.post(
                    token_url,
                    data={
                        "grant_type": "client_credentials",
                        "client_id": self._client_id,
                        "client_secret": self._client_secret,
                    },
                )
                if resp.status_code == 200:
                    token = resp.json().get("access_token")
                    if token:
                        return token
        except httpx.HTTPError as exc:
            raise ConnectionError("SAP authentication failed.") from exc
        raise ConnectionError("SAP authentication failed — no verified connection.")

    def _get_client(self) -> SAPODataClient:
        if not self._odata_base_url:
            raise NotImplementedError("SAP OData base URL not configured.")
        if self._client is None:
            self._client = SAPODataClient(
                self._odata_base_url,
                metadata_url=self._odata_metadata_url,
                timeout_seconds=self._timeout,
                auth_headers=self._auth_headers() if self._auth_mode != "NONE" else None,
                access_plan=self._access_plan,
            )
        return self._client

    def _record_trace(
        self,
        *,
        sap_table: str,
        entity_set: str | None,
        operation: str,
        key: str | None,
        result: str,
        mapped_to: str,
    ) -> None:
        self._traces.append(
            {
                "sap_table": sap_table,
                "odata_entity": entity_set,
                "operation": operation,
                "key": key,
                "result": result,
                "mapped_to": mapped_to,
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
            }
        )
        if len(self._traces) > 50:
            self._traces = self._traces[-50:]

    def verify_connection(self) -> bool:
        """Verify metadata then at least one intended entity GET. Sets LIVE only then."""
        client = self._get_client()
        meta = client.fetch_metadata()
        registry = build_seven_table_registry(
            meta.entity_sets,
            entity_keys={name: meta.keys_for_entity_set(name) for name in meta.entity_sets},
        )
        self._access_plan = build_access_plan(meta.entity_sets)
        client._access_plan = self._access_plan  # keep allow-list in sync after discovery
        self._entity_status = {b.domain: b.status for b in registry.bindings}

        data_ok = False
        for binding in registry.bindings:
            if not binding.entity_set or binding.status != "AVAILABLE":
                continue
            try:
                result = client.get_collection(binding.entity_set, params={"$top": "1"})
                self._entity_counts[binding.domain] = result.count
                self._record_trace(
                    sap_table=binding.sap_table,
                    entity_set=binding.entity_set,
                    operation="GET_ENTITYSET",
                    key=None,
                    result=f"{result.count} record(s)",
                    mapped_to=binding.canonical_target,
                )
                data_ok = True
                break
            except Exception as exc:
                self._entity_status[binding.domain] = "ERROR"
                self._last_error = str(exc)
                continue

        self._verified = True
        self._data_verified = data_ok
        self._last_sync = datetime.now(timezone.utc)
        if data_ok:
            self._last_error = None
        elif not self._last_error:
            self._last_error = "Metadata reachable but no seven-table entity set returned data."
        return data_ok

    def is_live_verified(self) -> bool:
        return self._verified and self._data_verified

    def source_mode(self) -> SourceMode:
        if not self._odata_base_url:
            return SourceMode.NOT_CONNECTED
        if self.is_live_verified():
            return SourceMode.LIVE
        if self._last_error:
            return SourceMode.ERROR if self._verified else SourceMode.NOT_CONNECTED
        return SourceMode.NOT_CONNECTED

    def get_context(self) -> SAPContext:
        if not self._odata_base_url:
            return self._mapper.map_context(
                system_name="SAP (not configured)",
                source_mode=SourceMode.NOT_CONNECTED,
                modules=[],
                status=IntegrationStatus.UNAVAILABLE,
                message="SAP OData base URL not configured.",
            )

        try:
            live = self.verify_connection()
            domains = [m.domain for m in self._access_plan.entity_mappings if m.sap_table]
            if not domains:
                domains = [m.domain for m in self._access_plan.entity_mappings]
            if live:
                return self._mapper.map_context(
                    system_name=self._odata_base_url,
                    source_mode=SourceMode.LIVE,
                    modules=domains,
                    status=IntegrationStatus.AVAILABLE,
                    message="Live SAP OData verified — metadata and data retrieval succeeded.",
                    entity_status=self._entity_status,
                    entity_counts=self._entity_counts,
                    service=self._access_plan.service_name,
                    last_retrieval=self._last_sync,
                )
            return self._mapper.map_context(
                system_name=self._odata_base_url,
                source_mode=SourceMode.ERROR if self._verified else SourceMode.NOT_CONNECTED,
                modules=domains,
                status=IntegrationStatus.UNAVAILABLE,
                message=self._last_error or "SAP metadata reached but data retrieval did not succeed.",
                entity_status=self._entity_status,
                entity_counts=self._entity_counts,
                service=self._access_plan.service_name,
                last_retrieval=self._last_sync,
            )
        except Exception as exc:
            self._verified = False
            self._data_verified = False
            self._last_error = str(exc)
            return self._mapper.map_context(
                system_name="SAP (connection failed)",
                source_mode=self._failure_source_mode(exc),
                modules=[],
                status=IntegrationStatus.UNAVAILABLE,
                message=str(exc),
            )

    def _read_entity(
        self,
        domain: str,
        *,
        key: str | None = None,
        filter_field: str | None = None,
        filter_value: str | None = None,
    ) -> list[dict[str, Any]]:
        if not self._verified:
            self.verify_connection()

        mapping = self._access_plan.mapping_for_domain(domain)
        if not mapping or not mapping.entity_set:
            raise NotImplementedError(
                f"Entity mapping for {domain} is PENDING_OFFICIAL_ODATA_METADATA."
            )

        client = self._get_client()
        params: dict[str, str] = {}
        if filter_field and filter_value:
            safe_val = str(filter_value).replace("'", "''")
            params["$filter"] = f"{filter_field} eq '{safe_val}'"

        if key:
            raw = client.get_by_key(mapping.entity_set, key)
            records = [raw]
            operation = "GET_ENTITY"
        else:
            result = client.get_collection(mapping.entity_set, params=params or None)
            records = result.values
            operation = "GET_ENTITYSET"

        self._entity_counts[domain] = len(records)
        self._last_sync = datetime.now(timezone.utc)
        self._record_trace(
            sap_table=mapping.sap_table or domain,
            entity_set=mapping.entity_set,
            operation=operation,
            key=str(key) if key else (params.get("$filter") if params else None),
            result=f"{len(records)} record(s)",
            mapped_to=mapping.canonical_target,
        )
        return records

    def list_domain(self, domain: str, *, filter_field: str | None = None, filter_value: str | None = None) -> list[dict[str, Any]]:
        return self._read_entity(domain, filter_field=filter_field, filter_value=filter_value)

    def get_domain_by_key(self, domain: str, key: str) -> dict[str, Any] | None:
        records = self._read_entity(domain, key=key)
        return records[0] if records else None

    def create_domain(self, domain: str, payload: dict[str, Any]) -> dict[str, Any]:
        mapping = self._require_mapped(domain)
        try:
            result = self._get_client().create_entity(mapping.entity_set, payload)
        except ODataWriteNotSupportedError as exc:
            self._write_available = False
            self._write_reason = exc.user_message
            raise
        self._write_available = True
        self._record_trace(
            sap_table=mapping.sap_table or domain,
            entity_set=mapping.entity_set,
            operation="CREATE_ENTITY",
            key=None,
            result="created",
            mapped_to=mapping.canonical_target,
        )
        return result.body or {}

    def update_domain(self, domain: str, key: str, payload: dict[str, Any]) -> dict[str, Any]:
        mapping = self._require_mapped(domain)
        try:
            current = self._get_client().get_by_key(mapping.entity_set, key)
        except ODataNotFoundError:
            raise
        if not current:
            raise ODataNotFoundError("SAP rejected the update because the record no longer exists.", 404)
        try:
            result = self._get_client().update_entity(mapping.entity_set, key, payload, merge=True)
        except ODataWriteNotSupportedError as exc:
            self._write_available = False
            self._write_reason = exc.user_message
            raise
        self._write_available = True
        self._record_trace(
            sap_table=mapping.sap_table or domain,
            entity_set=mapping.entity_set,
            operation="UPDATE_ENTITY",
            key=str(key),
            result="updated",
            mapped_to=mapping.canonical_target,
        )
        return result.body or {}

    def delete_domain(self, domain: str, key: str) -> dict[str, Any]:
        mapping = self._require_mapped(domain)
        current = self._get_client().get_by_key(mapping.entity_set, key)
        if not current:
            raise ODataNotFoundError("SAP rejected the update because the record no longer exists.", 404)
        result = self._get_client().delete_entity(mapping.entity_set, key)
        self._record_trace(
            sap_table=mapping.sap_table or domain,
            entity_set=mapping.entity_set,
            operation="DELETE_ENTITY",
            key=str(key),
            result="deleted",
            mapped_to=mapping.canonical_target,
        )
        return {"deleted": True, "status_code": result.status_code}

    def _require_mapped(self, domain: str):
        if not self._verified:
            self.verify_connection()
        mapping = self._access_plan.mapping_for_domain(domain)
        if not mapping or not mapping.entity_set:
            raise NotImplementedError(
                f"Entity mapping for {domain} is PENDING_OFFICIAL_ODATA_METADATA."
            )
        return mapping

    def get_candidate_context(self, candidate_id: str) -> dict[str, Any]:
        domain = "user" if self._access_plan.mapping_for_domain("user") else "person"
        try:
            records = self._read_entity(domain, filter_field="USER_ID", filter_value=candidate_id)
        except Exception:
            records = []
        if not records:
            try:
                records = self._read_entity(domain, key=candidate_id)
            except Exception:
                records = []
        if not records:
            return {
                "candidate_id": candidate_id,
                "status": "NOT_FOUND",
                "provenance": sap_provenance(
                    entity_set=domain,
                    object_id=candidate_id,
                    source_mode=self.source_mode(),
                    service=self._access_plan.service_name,
                    mapped_to="CandidateProfile",
                ),
            }
        mapping = self._access_plan.mapping_for_domain(domain)
        return self._mapper.map_employee_context(
            records[0],
            SourceMode.LIVE if self.is_live_verified() else self.source_mode(),
            entity_set=mapping.entity_set if mapping else domain,
            service=self._access_plan.service_name,
        )

    def get_employee_skills(self, candidate_id: str) -> list[CandidateCapability]:
        domain = "person_skill" if self._access_plan.mapping_for_domain("person_skill") else "qualification"
        try:
            records = self._read_entity(domain, filter_field="USER_ID", filter_value=candidate_id)
        except Exception:
            records = []
        mapping = self._access_plan.mapping_for_domain(domain)
        entity_set = mapping.entity_set if mapping else domain
        caps: list[CandidateCapability] = []
        for r in records:
            mapped = self._mapper.map_skill(
                r,
                candidate_id,
                SourceMode.LIVE if self.is_live_verified() else self.source_mode(),
                entity_set=entity_set,
                service=self._access_plan.service_name,
            )
            if mapped:
                caps.append(mapped)
        return caps

    def get_role_context(self, job_id: str) -> JobProfile | None:
        try:
            records = self._read_entity("job", key=job_id)
        except Exception:
            records = []
        if not records:
            try:
                records = self._read_entity("job", filter_field="JOB_ID", filter_value=job_id)
            except Exception:
                records = []
        if not records:
            return None
        mapping = self._access_plan.mapping_for_domain("job")
        return self._mapper.map_job(
            records[0],
            SourceMode.LIVE if self.is_live_verified() else self.source_mode(),
            entity_set=mapping.entity_set if mapping else "job",
            service=self._access_plan.service_name,
        )

    def get_learning_items(self) -> list[LearningItem]:
        try:
            records = self._read_entity("learning")
        except Exception:
            return []
        mapping = self._access_plan.mapping_for_domain("learning")
        entity_set = mapping.entity_set if mapping else "Learning"
        return [
            self._mapper.map_learning_item(
                r,
                SourceMode.LIVE if self.is_live_verified() else self.source_mode(),
                entity_set=entity_set,
                service=self._access_plan.service_name,
            )
            for r in records
        ]

    def get_opportunities(self) -> list[Opportunity]:
        try:
            records = self._read_entity("opportunity")
        except Exception:
            records = []
        if not records:
            try:
                jobs = self._read_entity("job")
                return [
                    self._mapper.map_opportunity(
                        r,
                        SourceMode.LIVE if self.is_live_verified() else self.source_mode(),
                    )
                    for r in jobs
                ]
            except Exception:
                return []
        mapping = self._access_plan.mapping_for_domain("opportunity")
        entity_set = mapping.entity_set if mapping else "Opportunity"
        return [
            self._mapper.map_opportunity(
                r,
                SourceMode.LIVE if self.is_live_verified() else self.source_mode(),
                entity_set=entity_set,
                service=self._access_plan.service_name,
            )
            for r in records
        ]

    def update_skill_progress(
        self,
        candidate_id: str,
        skill_id: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        raise NotImplementedError("SAP write-back is exposed through catalog mutations, not this method.")

    def get_diagnostics(self) -> dict[str, Any]:
        plan = self._access_plan.to_dict()
        return {
            "odata_base_url_configured": bool(self._odata_base_url),
            "metadata_url": self._odata_metadata_url,
            "auth_mode": self._auth_mode,
            "verified": self._verified,
            "data_verified": self._data_verified,
            "live_verified": self.is_live_verified(),
            "last_sync": self._last_sync.isoformat() if self._last_sync else None,
            "entity_status": self._entity_status,
            "entity_counts": self._entity_counts,
            "access_plan": plan,
            "last_error": self._last_error,
            "write_available": self._write_available,
            "write_reason": self._write_reason,
            "traces": list(self._traces),
        }


def build_live_provider() -> LiveSAPProvider:
    settings = get_settings()
    return LiveSAPProvider(
        api_url=settings.sap_api_url,
        client_id=settings.sap_client_id,
        client_secret=settings.sap_client_secret,
        company_id=settings.sap_company_id,
        odata_base_url=settings.sap_odata_base_url or settings.sap_api_url,
        odata_metadata_url=settings.sap_odata_metadata_url,
        timeout_seconds=settings.sap_timeout_seconds,
        auth_mode=settings.sap_auth_mode,
        username=settings.sap_username,
        password=settings.sap_password,
    )
