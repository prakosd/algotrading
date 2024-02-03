"""Module of Component Factory"""
from datetime import datetime as dt

from ...common.trade import DealType, OrderType
from ...common.trade import OrderDirection, PositionType
from ...common.symbol import Symbol
from .account.api import EIAccount
from .account.implementation import Account
from .deal.api import EIDeal
from .deal.implementation import Deal
from .order.api import EIOrder
from .order.implementation import Order
from .position.api import EIPosition
from .position.implementation import Position
from .trade.api import EITrade
from .trade.implementation import Trade

class ComponentFactory():
    """Static class to create component object"""

    @staticmethod
    def create_account(initial_datetime: dt, initial_balance: float) -> EIAccount:
        """Return new account object"""
        return Account(initial_datetime, initial_balance)

    @staticmethod
    def create_deal(symbol: Symbol, datetime: dt, deal_type: DealType,
                    volume: float, price: float) -> EIDeal:
        """Return new deal object"""
        return Deal(symbol, datetime, deal_type, volume, price)

    @staticmethod
    def create_order(symbol: Symbol, datetime: dt, order_type: OrderType,
                     direction: OrderDirection, volume: float, price: float) -> EIOrder:
        """Return new order object"""
        return Order(symbol, datetime, order_type, direction, volume, price)

    @staticmethod
    def create_position(symbol: Symbol, open_datetime: dt, pos_type: PositionType,
                        volume: float, price: float, margin: float, comment: str) -> EIPosition:
        """Return new position object"""
        return Position(symbol, open_datetime, pos_type, volume, price, margin, comment)

    @staticmethod
    def create_trade() -> EITrade:
        """Return new trade object"""
        return Trade()
