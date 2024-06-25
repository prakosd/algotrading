"""Module of Contrarian Strategy Class"""
from typing import Optional
from dataclasses import dataclass
import pandas as pd

from ..base.implementation import IterativeBase
from ...strategies import ContrarianParams
from ...strategies.buyandhold import BuyAndHoldStrategy
from ....common.trade import PositionType

@dataclass
class ContrarianStrategy(IterativeBase):
    """Implementation of Contrarian Strategy"""
    params: ContrarianParams
    buyandhold: Optional[BuyAndHoldStrategy] = None

    def run(self):
        """Start backtesting"""
        if self.data is None:
            return

        self.data["rolling_returns"] = self.data["returns"].rolling(
            self.params.window).mean()

        super().start(len(self.data.index), self.on_tick)

        if self.buyandhold:
            self.buyandhold.run()

    def stop(self):
        """Stop Backtesting"""
        super().stop()

        if self.buyandhold:
            self.buyandhold.stop()

    def on_tick(self, i: int):
        """on each tick"""
        tick = self.ticker.get_data(datetime = self.data.index[i])

        pos = self.get_last_open_position()
        if self.data["rolling_returns"].iloc[i] < 0:
            if pos is None:
                self.long_buy(tick, self.params.volume)
            elif pos.type == PositionType.SHORT_SELL:
                self.close_position(pos.id, tick)

        elif self.data["rolling_returns"].iloc[i] > 0:
            if pos is None:
                self.short_sell(tick, self.params.volume)
            elif pos.type == PositionType.LONG_BUY:
                self.close_position(pos.id, tick)

    def get_equity_records(self) -> pd.DataFrame:
        """Return equity and balance history"""
        df_equity = super().get_equity_records()
        if df_equity is None:
            return None

        if self.buyandhold is None:
            return df_equity

        df_buy_hold = self.buyandhold.get_equity_records()
        if df_buy_hold is None:
            return df_equity

        df_buy_hold = df_buy_hold.rename(columns={"equity": "buyHold"})
        return pd.concat([df_equity, df_buy_hold["buyHold"]],
                         axis="columns").ffill().sort_index()

    def plot_equity_records(self):
        """Plot equity and balance history"""
        if self.buyandhold is None:
            super().plot_equity_records()
            return

        color_buyhold = "slategrey"
        color_balance = "red"
        color_equity = "rosybrown"
        report = self.get_report()
        if report and report.summary and report.summary.net_profit > 0:
            color_balance = "green"
            color_equity = "cadetblue"

        title = "Balance vs Equity vs Buy&Hold"
        equity_records = self.get_equity_records()
        equity_records[["buyHold", "equity", "balance"]].plot(
            title=title, figsize=(12, 8),
            color=[color_buyhold, color_equity, color_balance])
