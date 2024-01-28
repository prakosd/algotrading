"""Module of Position Entity Interface"""
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from typing import ClassVar
from datetime import datetime as dt

from .....common.trade import PositionType, PositionStatus
from .....common.trade import OrderDirection
from .....common.symbol import Symbol
from ...order.api import EIOrder
from .....ticker.api import EITick

@dataclass
class EIPosition(ABC):
    """Position Entity Interface"""
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
    orders: list[EIOrder] = field(init=False)
    _profit: float = field(init=False)

    @staticmethod
    def reset_id():
        """Reset next id"""
        EIPosition._next_id = 0

    @staticmethod
    def generate_id() -> int:
        """generate next id"""
        new_id = EIPosition._next_id
        EIPosition._next_id += 1
        return new_id

    @abstractmethod
    def __post_init__(self):
        """Post initialization"""
        self.id = EIPosition.generate_id()
        self.close_datetime = None
        self.status = PositionStatus.OPEN
        self.orders = []
        self._profit = 0

    @abstractmethod
    def execute_order(self, datetime: dt, direction: OrderDirection, price: float) -> EIOrder:
        """Execute an order"""

    @abstractmethod
    def get_profit(self, tick: EITick=None) -> float:
        """Return realized/floating profit on a given tick"""

    @abstractmethod
    def close(self, tick: EITick) -> float:
        """Close position and return profit"""

    @abstractmethod
    def get_orders(self, index: int=None) -> list[EIOrder] | EIOrder:
        """Return list of orders or an order by index"""

    @abstractmethod
    def orders_length(self) -> int:
        """Return number of executed orders"""

    @abstractmethod
    def get_price_by_order_direction(self, direction: OrderDirection) -> float:
        """Return price by order direction"""

    @abstractmethod
    def open_price(self) -> float:
        """Return open price"""

    @abstractmethod
    def close_price(self) -> float:
        """Return close price"""

    @abstractmethod
    def clear_orders(self):
        """Remove all orders"""

    @abstractmethod
    def as_dict(self) -> dict:
        """Return position as dictionary"""
