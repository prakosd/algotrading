"""Module of Order Entity Interface"""
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from typing import ClassVar
from datetime import datetime as dt

from .....common.config import config
from .....common.trade import OrderType, OrderDirection
from .....common.asset import AssetPairCode as Symbol
from ...deal import Deal
from .....ticker import Tick

@dataclass
class EIOrder(ABC):
    """Order Entity Interface"""
    IS_MOCK_DEAL: ClassVar[bool] = config.deal.is_mock_deal
    SLIPPAGE_POINT: ClassVar[dict] = {"min": config.deal.slippage_point_min,
                                      "max": config.deal.slippage_point_max}
    VOLUME_PERCENT: ClassVar[dict] = {"min": config.deal.volume_percent_min,
                                      "max": config.deal.volume_percent_max}

    _next_id: ClassVar[int] = 0

    id: int = field(init=False)
    symbol: Symbol
    datetime: dt
    type: OrderType
    direction: OrderDirection
    volume: float
    price: float
    deals: list[Deal] = field(init=False)

    @staticmethod
    def reset_id():
        """Reset next id"""
        EIOrder._next_id = 0

    @staticmethod
    def generate_id() -> int:
        """generate next id"""
        new_id = EIOrder._next_id
        EIOrder._next_id += 1
        return new_id

    def __post_init__(self):
        """Post initialization"""
        self.id = EIOrder.generate_id()
        self.deals = []

    @abstractmethod
    def get_deals(self, index: int=None) -> list[Deal] | Deal:
        """Return list of deals or a deal by index"""

    @abstractmethod
    def deals_length(self) -> int:
        """Return number of executed deals"""

    @abstractmethod
    def clear_deals(self):
        """Remove all deals"""

    @abstractmethod
    def execute(self):
        """Execute order"""

    @abstractmethod
    def get_profit(self, tick: Tick) -> float:
        """Return profit on a given tick"""

    @abstractmethod
    def sum_deals_volume(self) -> float:
        """Return total volume of successful executed deals"""

    @abstractmethod
    def avg_deals_price(self) -> float:
        """Return average price of deals"""

    @abstractmethod
    def mock_deal(self, random_deal=False) -> Deal:
        """Return deals with randomize value in given range"""

    @abstractmethod
    def as_dict(self) -> dict:
        """Return order as dictionary"""
