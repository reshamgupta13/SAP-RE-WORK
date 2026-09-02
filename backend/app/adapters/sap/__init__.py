"""SAP adapter factory with explicit LIVE/SIMULATED switching."""

from app.adapters.sap.live import build_live_provider
from app.adapters.sap.provider import SAPProvider
from app.adapters.sap.simulated import SimulatedSAPProvider
from app.core.config import get_settings


def get_sap_provider() -> SAPProvider:
    settings = get_settings()

    if settings.demo_mode:
        return SimulatedSAPProvider()

    if settings.sap_mode.upper() == "LIVE":
        return build_live_provider()

    return SimulatedSAPProvider()


def get_product_sap_provider() -> SAPProvider:
    """Provider for the product catalog — ignores DEMO_MODE fixture switching."""
    settings = get_settings()
    if settings.sap_mode.upper() == "LIVE":
        return build_live_provider()
    return SimulatedSAPProvider()
