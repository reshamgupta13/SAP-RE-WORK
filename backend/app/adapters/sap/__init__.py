"""SAP adapter factory with explicit LIVE/SIMULATED switching."""

from app.adapters.sap.provider import SAPProvider
from app.adapters.sap.simulated import SimulatedSAPProvider
from app.core.config import get_settings


def get_sap_provider() -> SAPProvider:
    settings = get_settings()

    if settings.demo_mode:
        return SimulatedSAPProvider()

    if settings.sap_mode.upper() == "LIVE":
        from app.adapters.sap.live import LiveSAPProvider

        return LiveSAPProvider(
            api_url=settings.sap_api_url,
            client_id=settings.sap_client_id,
            client_secret=settings.sap_client_secret,
            company_id=settings.sap_company_id,
        )

    return SimulatedSAPProvider()
