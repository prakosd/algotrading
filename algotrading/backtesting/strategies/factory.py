"""Module of Strategy Factory"""
from datetime import datetime as dt

from ...common.enums import Timeframe
from .buyandhold.implementation import BuyAndHoldStrategy
from ...providers import ProviderFactory
from ..components.account.implementation import Account
from . import BuyAndHoldParams
from ..components.trade.implementation import Trade

class StrategyFactory():
    """Static class to create strategy object"""

    @staticmethod
    def create_buyandhold(provider_name: str, symbol: str, start_date: dt,
                          end_date: dt, timeframe: Timeframe,
                          initial_balance: float, volume: float,
                          force_download_ticker: bool=False) -> BuyAndHoldStrategy:
        """Return new buyandhold object"""
        provider = ProviderFactory.create_provider_by_name(
            provider_name, symbol, start_date, end_date, timeframe)
        if provider is None:
            return None

        ticker = provider.get_ticker(force_download_ticker)
        if ticker is None or ticker.get_length() <= 0:
            return None

        account = Account(ticker.get_data(0).datetime, initial_balance)
        params = BuyAndHoldParams(initial_balance, volume)

        return BuyAndHoldStrategy(Trade(), ticker, account, params)
