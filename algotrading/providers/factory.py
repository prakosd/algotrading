"""Module of Provider Factory"""
from datetime import datetime as dt
from typing import ClassVar

from ..common.trade import Timeframe
from ..common.asset import AssetPairCode as Symbol
from .api import EIProvider
from .implementation import OandaProvider

class ProviderFactory():
    """Static class to create provider object"""
    OANDA: ClassVar[str] = EIProvider.OANDA

    @classmethod
    def create_provider_by_name(cls, name: str, symbol: Symbol,
                                start: dt, end: dt,
                                timeframe: Timeframe) -> EIProvider:
        """Return provider object by name"""
        if name == cls.OANDA:
            return OandaProvider(symbol, start, end, timeframe)

        return None
