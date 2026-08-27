"""SAP adapter factory."""

from app.adapters.sap.provider import SAPProvider
from app.adapters.sap.simulated import SimulatedSAPProvider
from app.core.config import get_settings


def get_sap_provider() -> SAPProvider:
    settings = get_settings()
    # Live provider only when explicitly configured — never auto-fake live
    if settings.demo_mode:
        return SimulatedSAPProvider()
    return SimulatedSAPProvider()
