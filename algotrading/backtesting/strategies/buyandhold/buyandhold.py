"""Module of Buy and Hold Strategy Class"""
from dataclasses import dataclass

from ..base.implementation import IterativeBase
from ...strategies import BuyAndHoldParams

@dataclass
class BuyAndHoldStrategy(IterativeBase):
    """Implementation of Buy and Hold Strategy"""
    params: BuyAndHoldParams

    def run(self):
        """Start backtesting"""
        if self.data is None:
            return

        super().start(len(self.data.index), self.on_tick)

    def on_tick(self, i: int):
        """on each tick"""
        if i > 0:
            return

        tick = self.ticker.get_data(datetime=self.data.index[i])
        self.long_buy(tick, self.params.volume)
