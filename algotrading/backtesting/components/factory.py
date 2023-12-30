"""Module of Component Factory"""
from datetime import datetime as dt

from ...common.enums import DealType, OrderType, OrderDirection
from .account.api import EIAccount
from .account.implementation import Account
from .deal.api import EIDeal
from .order.api import EIOrder
from .order.implementation import Order

class ComponentFactory():
    """Static class to create component object"""

    @staticmethod
    def create_account(initial_datetime: dt, initial_balance: float) -> EIAccount:
        """Return new account object"""
        return Account(initial_datetime, initial_balance)

    @staticmethod
    def create_deal(symbol: str, datetime: dt, deal_type: DealType,
                    volume: float, price: float) -> EIDeal:
        """Return new deal object"""
        return EIDeal(symbol, datetime, deal_type, volume, price)

    @staticmethod
    def create_order(symbol: str, datetime: dt, order_type: OrderType,
                     direction: OrderDirection, volume: float, price: float) -> EIOrder:
        """Return new order object"""
        return Order(symbol, datetime, order_type, direction, volume, price)
