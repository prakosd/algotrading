"""Module of Strategy Factory"""
import copy
from typing import ClassVar

from ...ticker.ticker import Ticker
from .buyandhold.implementation import BuyAndHoldStrategy
from .contrarian.implementation import ContrarianStrategy
from ...providers import ProviderFactory
from ..components.account import Account
from . import BuyAndHoldParams, ContrarianParams

class StrategyFactory():
    """Static class to create strategy object"""
    PROVIDER_OANDA: ClassVar[str] = ProviderFactory.OANDA

    @staticmethod
    def create_buyandhold(ticker: Ticker, params: BuyAndHoldParams) -> BuyAndHoldStrategy:
        """Return new buyandhold strategy object"""
        if ticker is None or ticker.get_length() <= 0:
            return None

        account = Account(ticker.get_data(0).datetime, params.balance)

        return BuyAndHoldStrategy(ticker, account, params)

    @staticmethod
    def create_contrarian(ticker: Ticker,
                             params: ContrarianParams,
                             include_buyandhold: bool=True) -> ContrarianStrategy:
        """Return new contrarian strategy object"""
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
