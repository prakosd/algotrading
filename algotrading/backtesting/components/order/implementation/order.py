"""Module of Order Class"""
from copy import copy
import random

from ..api import EIOrder
from ...deal.api import EIDeal
from .....ticker.api import EITick
from .....common.enums import DealType

class Order(EIOrder):
    """Implementation of EIOrder"""

    def get_deals(self, index: int=None) -> list[EIDeal] | EIDeal:
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
        deal = self.mock_deal(EIOrder.IS_MOCK_DEAL)
        self.deals.append(deal)
        if self.sum_deals_volume() < self.volume:
            # execute again if order volume is not fulfilled
            self.execute()

    def get_profit(self, tick: EITick) -> float:
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

    def mock_deal(self, random_deal=False) -> EIDeal:
        """Return deals with randomize value in given range"""
        deal_type = DealType.BUY if self.type.value > 0 else DealType.SELL

        if not random_deal:
            return EIDeal(self.symbol, self.datetime,
                                                deal_type, self.volume, self.price)

        price = self.price + (random.randint(
            EIOrder.SLIPPAGE_POINT.get("min"),
            EIOrder.SLIPPAGE_POINT.get("max")) / 100000)
        volume = random.randint(
            EIOrder.VOLUME_PERCENT.get("min"),
            EIOrder.VOLUME_PERCENT.get("max")) / 100 * self.volume
        sum_vol = self.sum_deals_volume()
        if sum_vol + volume > self.volume:
            volume = self.volume - sum_vol
        return EIDeal(self.symbol, self.datetime,
                                            deal_type, volume, price)

    def as_dict(self) -> dict:
        """Return order as dictionary"""
        return {'id': self.id, 'symbol': self.symbol, 'datetime': self.datetime,
                'type': self.type.name, 'direction': self.direction.name,
                'volume': self.volume, 'price': self.price}
