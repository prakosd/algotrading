"""Module of Strategy Factory"""
import copy
from datetime import datetime as dt
from typing import ClassVar

from ...common.trade import Timeframe
from ...common.asset import AssetPairCode as Symbol
from .buyandhold.implementation import BuyAndHoldStrategy
from .contrarian.implementation import ContrarianStrategy
from ...providers import ProviderFactory
from ..components.account import Account
from . import BuyAndHoldParams, ContrarianParams

class StrategyFactory():
    """Static class to create strategy object"""
    PROVIDER_OANDA: ClassVar[str] = ProviderFactory.OANDA

    @staticmethod
    def create_buyandhold(provider_name: str, symbol: Symbol, start_date: dt,
                          end_date: dt, timeframe: Timeframe,
                          params: BuyAndHoldParams,
                          force_download_ticker: bool=False) -> BuyAndHoldStrategy:
        """Return new buyandhold strategy object"""
        provider = ProviderFactory.create_provider_by_name(
            provider_name, symbol, start_date, end_date, timeframe)
        if provider is None:
            return None

        ticker = provider.get_ticker(force_download_ticker)
        if ticker is None or ticker.get_length() <= 0:
            return None

        account = Account(ticker.get_data(0).datetime, params.balance)

        return BuyAndHoldStrategy(ticker, account, params)

    @staticmethod
    def create_contrarian(provider_name: str, symbol: Symbol, start_date: dt,
                          end_date: dt, timeframe: Timeframe,
                          params: ContrarianParams,
                          include_buyandhold: bool=True,
                          force_download_ticker: bool=False) -> ContrarianStrategy:
        """Return new contrarian strategy object"""
        provider = ProviderFactory.create_provider_by_name(
            provider_name, symbol, start_date, end_date, timeframe)
        if provider is None:
            return None

        ticker = provider.get_ticker(force_download_ticker)
        if ticker is None or ticker.get_length() <= 0:
            return None

        account = Account(ticker.get_data(0).datetime, params.balance)

        if include_buyandhold:
            return ContrarianStrategy(ticker, account, params,
                                      BuyAndHoldStrategy(
                                          copy.deepcopy(ticker),
                                          copy.deepcopy(account), params))
        else:
            return ContrarianStrategy(ticker, account, params)
