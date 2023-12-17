"""Module of Provider Factory"""
from datetime import datetime as dt

from ..api import EIProvider, Granularity
from .oanda import Oanda

class ProviderFactory():
    """Static class to create provider object"""

    @staticmethod
    def create_provider_by_name(name: str, symbol: str,
                                start: dt, end: dt,
                                granularity: Granularity) -> EIProvider | None:
        """Return provider object by name"""
        if name == EIProvider.PROVIDER_OANDA:
            return Oanda(symbol, start, end, granularity)

        return None
