"""SAP Learning adapter factory."""

from functools import lru_cache

from app.adapters.sap_learning.base import SAPLearningProvider
from app.adapters.sap_learning.simulated import SimulatedSAPLearningProvider
from app.core.config import get_settings


@lru_cache
def get_sap_learning_provider() -> SAPLearningProvider:
    settings = get_settings()
    if settings.demo_mode or not settings.llm_api_key:
        return SimulatedSAPLearningProvider()
    return SimulatedSAPLearningProvider()
