"""Module of Order Class"""
from dataclasses import dataclass, field
from typing import ClassVar
from datetime import datetime as dt
from copy import copy
import random

from ....common.config import config
from ....common.trade import OrderType, OrderDirection
from ....common.asset import AssetPairCode as Symbol
from ....common.trade import DealType
from ..deal import Deal
from ....ticker import Tick

@dataclass
class Order():
    """Order Class"""
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
        self.deals = []

    def get_deals(self, index: int=None) -> list[Deal] | Deal:
        """Return list of deals or a deal by index"""
        if index is None:
            return self.deals.copy()

        return copy(self.deals[index])

    def deals_length(self) -> int:
        """Return number of executed deals"""
        return len(self.deals)

    def clear_deals(self):
        """Remove all deals"""
        self.deals.clear()

    def execute(self):
        """Execute order"""
        deal = self.mock_deal(self.IS_MOCK_DEAL)
        self.deals.append(deal)
        if self.sum_deals_volume() < self.volume:
            # execute again if order volume is not fulfilled
            self.execute()

    def get_profit(self, tick: Tick) -> float:
        """Return profit on a given tick"""
        point = 0
        for deal in self.deals:
            if deal.type == DealType.BUY:
                point += (tick.bid - deal.price) * deal.volume
            elif deal.type == DealType.SELL:
                point += (tick.ask - deal.price) * -deal.volume
            else:
                raise ValueError("Unrecognized DealType")

        return point * pow(10, tick.digit)

    def sum_deals_volume(self) -> float:
        """Return total volume of successful executed deals"""
        volume = 0
        for deal in self.deals:
            volume += deal.volume

        return volume

    def avg_deals_price(self) -> float:
        """Return average price of deals"""
        volume_price = 0
        for deal in self.deals:
            volume_price += deal.volume * deal.price

        return volume_price / self.volume

    def mock_deal(self, random_deal=False) -> Deal:
        """Return deals with randomize value in given range"""
        deal_type = DealType.BUY if self.type.value > 0 else DealType.SELL

        if not random_deal:
            return Deal(self.symbol, self.datetime,
                        deal_type, self.volume, self.price)

        price = self.price + (random.randint(
            self.SLIPPAGE_POINT.get("min"),
            self.SLIPPAGE_POINT.get("max")) / 100000)
        volume = random.randint(
            self.VOLUME_PERCENT.get("min"),
            self.VOLUME_PERCENT.get("max")) / 100 * self.volume
        sum_vol = self.sum_deals_volume()
        if sum_vol + volume > self.volume:
            volume = self.volume - sum_vol
        return Deal(self.symbol, self.datetime,
                    deal_type, volume, price)

    def as_dict(self) -> dict:
        """Return order as dictionary"""
        return {'id': self.id, 'symbol': self.symbol.value, 'datetime': self.datetime,
                'type': self.type.name, 'direction': self.direction.name,
                'volume': self.volume, 'price': self.price}
