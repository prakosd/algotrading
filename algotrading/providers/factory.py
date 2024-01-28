"""Module of Provider Factory"""
from datetime import datetime as dt

from ..common.trade import Timeframe
from ..common.symbol import Symbol
from .api import EIProvider
from .implementation import OandaProvider

class ProviderFactory():
    """Static class to create provider object"""

    @staticmethod
    def create_provider_by_name(name: str, symbol: Symbol,
                                start: dt, end: dt,
                                timeframe: Timeframe) -> EIProvider:
        """Return provider object by name"""
        if name == EIProvider.PROVIDER_OANDA:
            return OandaProvider(symbol, start, end, timeframe)

        return None
