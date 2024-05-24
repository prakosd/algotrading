"""Module of Component Factory"""
from datetime import datetime as dt

from ...common.trade import DealType, OrderType
from ...common.trade import OrderDirection, PositionType
from ...common.asset import AssetPairCode as Symbol
from .account import Account
from .deal import Deal
from .order import Order
from .position import Position
from .trade import Trade

class ComponentFactory():
    """Static class to create component object"""

    @staticmethod
    def create_account(initial_datetime: dt, initial_balance: float) -> Account:
        """Return new account object"""
        return Account(initial_datetime, initial_balance)

    @staticmethod
    def create_deal(symbol: Symbol, datetime: dt, deal_type: DealType,
                    volume: float, price: float) -> Deal:
        """Return new deal object"""
        return Deal(symbol, datetime, deal_type, volume, price)

    @staticmethod
    def create_order(symbol: Symbol, datetime: dt, order_type: OrderType,
                     direction: OrderDirection, volume: float, price: float) -> Order:
        """Return new order object"""
        return Order(symbol, datetime, order_type, direction, volume, price)

    @staticmethod
    def create_position(symbol: Symbol, open_datetime: dt, pos_type: PositionType,
                        volume: float, price: float, margin: float, comment: str) -> Position:
        """Return new position object"""
        return Position(symbol, open_datetime, pos_type, volume, price, margin, comment)

    @staticmethod
    def create_trade() -> Trade:
        """Return new trade object"""
        return Trade()
