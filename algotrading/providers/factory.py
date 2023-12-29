"""Module of Provider Factory"""
from datetime import datetime as dt

from ..common.enums import Timeframe
from .api import EIProvider
from .implementation import OandaProvider

class ProviderFactory():
    """Static class to create provider object"""

    @staticmethod
    def create_provider_by_name(name: str, symbol: str,
                                start: dt, end: dt,
                                timeframe: Timeframe) -> EIProvider | None:
        """Return provider object by name"""
        if name == EIProvider.PROVIDER_OANDA:
            return OandaProvider(symbol, start, end, timeframe)

        return None
