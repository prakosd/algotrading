"""Module of Position Class"""
from dataclasses import dataclass, field
from typing import ClassVar
from datetime import datetime as dt
from copy import copy

from ....common.trade import PositionType, PositionStatus
from ....common.trade import OrderDirection, OrderType
from ....common.asset import AssetPairCode as Symbol
from ..order import Order
from ....ticker import Tick

@dataclass
class Position():
    """Position Class"""
    _next_id: ClassVar[int] = 0

    id: int = field(init=False)
    symbol: Symbol
    open_datetime: dt
    close_datetime: dt = field(init=False)
    type: PositionType
    volume: float
    price: float
    margin: float
    comment: str
    status: PositionStatus = field(init=False)
    orders: list[Order] = field(init=False)
    _profit: float = field(init=False)

    @classmethod
    def reset_id(cls):
        """Reset next id"""
        cls._next_id = 0

    @classmethod
    def generate_id(cls) -> int:
        """generate next id"""
        new_id = cls._next_id
        cls._next_id += 1
        return new_id

    def __post_init__(self):
        """Post initialization"""
        self.id = self.generate_id()
        self.close_datetime = None
        self.status = PositionStatus.OPEN
        self.orders = []
        self._profit = 0

        self.orders.append(
            self.execute_order(self.open_datetime,
                               OrderDirection.MARKET_IN, self.price)
        )

    def execute_order(self, datetime: dt, direction: OrderDirection, price: float) -> Order:
        """Execute an order"""
        if direction == OrderDirection.MARKET_IN:
            if self.type == PositionType.LONG_BUY:
                order_type = OrderType.MARKET_BUY
            elif self.type == PositionType.SHORT_SELL:
                order_type =  OrderType.MARKET_SELL
            else:
                raise ValueError("Unrecognized PositionType")
        elif direction == OrderDirection.MARKET_OUT:
            if self.type == PositionType.LONG_BUY:
                order_type = OrderType.MARKET_SELL
            elif self.type == PositionType.SHORT_SELL:
                order_type =  OrderType.MARKET_BUY
            else:
                raise ValueError("Unrecognized PositionType")
        else:
            raise ValueError("Unrecognized OrderDirection")

        order = Order(self.symbol, datetime, order_type,
                        direction, self.volume, price)
        order.execute()
        return order

    def get_profit(self, tick: Tick=None) -> float:
        """Return realized/floating profit on a given tick"""
        if self.status == PositionStatus.CLOSE or tick is None:
            return self._profit

        profit = 0
        for order in self.orders:
            if order.direction == OrderDirection.MARKET_IN:
                profit += order.get_profit(tick)

        return profit

    def close(self, tick: Tick) -> float:
        """Close position and return profit"""
        if self.status == PositionStatus.CLOSE:
            return self._profit

        price = 0
        if self.type == PositionType.LONG_BUY:
            price = tick.bid
        elif self.type == PositionType.SHORT_SELL:
            price = tick.ask
        else:
            raise ValueError("Unrecognized PositionType")

        self.orders.append(self.execute_order(
            tick.datetime, OrderDirection.MARKET_OUT, price))
        self._profit   = self.get_profit(tick)
        self.close_datetime = tick.datetime
        self.status   = PositionStatus.CLOSE

        return self._profit

    def get_orders(self, index: int=None) -> list[Order] | Order:
        """Return list of orders or an order by index"""
        if index is None:
            return self.orders.copy()

        return copy(self.orders[index])


    def orders_length(self) -> int:
        """Return number of executed orders"""
        return len(self.orders)

    def get_price_by_order_direction(self, direction: OrderDirection) -> float:
        """Return price by order direction"""
        volume_total = 0
        volume_price = 0
        for order in self.orders:
            if order.direction == direction:
                volume_total += order.volume
                volume_price += order.avg_deals_price() * order.volume

        return volume_price / volume_total if volume_total > 0 else 0

    def open_price(self) -> float:
        """Return open price"""
        return self.get_price_by_order_direction(OrderDirection.MARKET_IN)

    def close_price(self) -> float:
        """Return close price"""
        return self.get_price_by_order_direction(OrderDirection.MARKET_OUT)

    def clear_orders(self):
        """Remove all orders"""
        for order in self.orders:
            order.clear_deals()
        self.orders.clear()

    def as_dict(self) -> dict:
        """Return position as dictionary"""
        return {'id': self.id, 'symbol': self.symbol.value, 'openDatetime': self.open_datetime,
                'closeDatetime': self.close_datetime, 'type': self.type.name,
                'volume': self.volume, 'comment': self.comment,
                'status': self.status.name, 'margin': self.margin, 'profit': self._profit}
