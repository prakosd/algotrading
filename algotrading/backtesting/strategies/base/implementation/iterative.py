"""Module of IterativeBase Class"""
import time
from abc import ABC
from typing import Callable
import numpy as np
import pandas as pd

from ..api import EIIterativeBase
from ....components.account.api import EIAccount
from ....components.position.api import EIPosition
from ....components.order.api import EIOrder
from ....components.deal.api import EIDeal
from .....common.trade import MarginHealth, PositionType
from .....ticker import Tick
from .....backtesting import BacktestingReport

class IterativeBase(EIIterativeBase, ABC):
    """Implementation of EIIterativeBase"""

    def __post_init__(self):
        """Post initialization"""
        super().__post_init__()
        self.prepare_data()

    def prepare_data(self):
        """Prepare data to test"""
        raw = self.ticker.get_data()

        if raw is None:
            return

        raw["returns"] = np.log(raw.mid / raw.mid.shift(1))
        # raw["creturns"] = raw["returns"].cumsum().apply(np.exp)
        self.data = raw

    def print_iteration(self, i: int, length: int):
        """Print iteration progress"""
        print(f"Iteration: {i} of {length} ({int(round(i / length * 100, 0))}%)    ",
              flush=True, end="\r")

    def start(self, length: int, callback: Callable):
        """Start the iteration"""
        self.tick_count = 0
        if self.is_running or length <= 0:
            return

        self.is_running = True
        last_time = time.time()
        margin_health = MarginHealth.OK
        self.print_iteration(0, length)
        for i in range(length - 1):
            if self.is_interrupted:
                self.is_interrupted = False
                self.is_running = False
                self.populate_report()
                return

            # print every second
            if time.time() - last_time >= 0.5:
                last_time = time.time()
                self.print_iteration(i+1, length)

            self.tick_count += 1
            callback(i)
            tick = self.ticker.get_data(datetime=self.data.index[i])
            self.record_equity(tick)

            margin_health = self.margin_health(tick)
            if margin_health == MarginHealth.STOP_OUT:
                self.close_all_position(tick)
                self.record_equity(tick)
                # self.print_account_info(tick)
                break

        # close all position on the last tick
        self.tick_count += 1
        if margin_health != MarginHealth.STOP_OUT:
            last_index = length - 1
            last_tick = self.ticker.get_data(
                datetime=self.data.index[last_index])
            self.close_all_position(last_tick)
            self.record_equity(last_tick)
            # self.print_account_info(last_tick)

        self.is_running = False
        self.print_iteration(length, length)
        self.populate_report()

    def stop(self):
        """Stop the iteration"""
        if self.is_running:
            self.is_interrupted = True

    def margin_health(self, tick: Tick) -> MarginHealth:
        """Return margin health on given tick"""
        if self.margin_used() > 0:
            margin_level = self.margin_level(tick)

            if self.min_margin_level is None or self.min_margin_level > margin_level:
                self.min_margin_level = margin_level

            if margin_level <= EIIterativeBase.STOP_OUT_LEVEL:
                return MarginHealth.STOP_OUT
            elif margin_level <= EIIterativeBase.MARGIN_CALL_LEVEL:
                return MarginHealth.MARGIN_CALL
            else:
                return MarginHealth.OK
        else:
            return MarginHealth.OK

    def margin_used(self) -> float:
        """Return total margin in use"""
        return self.trade.margin_used()

    def margin_level(self, tick: Tick) -> float:
        """Return current percentage of margin level"""
        margin_used = self.margin_used()
        if margin_used <= 0:
            return 0
        else:
            return (self.equity(tick) / margin_used) * 100

    def equity(self, tick: Tick) -> float:
        """Return current equity"""
        return self.balance() + self.trade.floating_profit(tick)

    def balance(self) -> float:
        """Return current balance"""
        return self.account.actual_balance + self.margin_used()

    def record_equity(self, tick: Tick):
        """Record equity on a given tick"""
        record = {'datetime': tick.datetime,
                  'balance': self.balance(),
                  'rProfit': self.realized_net_profit(),
                  'equity': self.equity(tick),
                  'fProfit': self.floating_profit(tick),
                  'marginUsed': self.margin_used(),
                  'freeMargin': self.free_margin(tick),
                  'marginLevel': self.margin_level(tick),
                  'marginHealth': self.margin_health(tick).name}
        self.equity_records.append(record)

    def floating_profit(self, tick: Tick) -> float:
        """Return current unrealized profit/loss"""
        return self.trade.floating_profit(tick)

    def realized_net_profit(self) -> float:
        """Return current realized profit/loss"""
        return self.trade.realized_net_profit()

    def free_margin(self, tick: Tick) -> float:
        """Return current free margin"""
        return self.equity(tick) - self.margin_used()

    def close_all_position(self, tick: Tick) -> bool:
        """Close all open positions"""
        open_pos_before = len(self.trade.get_all_open_position())
        positions = self.trade.close_all_position(tick)
        for pos in positions:
            self.account.close_trade(
                tick.datetime, pos.margin, pos.get_profit())

        open_pos_after = len(self.trade.get_all_open_position())

        return open_pos_before == open_pos_after

    def open_position(self, tick: Tick, position_type: PositionType,
                       volume: float) -> int:
        """Open long/buy or short/sell position and returns position id"""
        if self.margin_health(tick) == MarginHealth.MARGIN_CALL:
            return 0

        if position_type == PositionType.LONG_BUY:
            price = tick.ask
        elif position_type == PositionType.SHORT_SELL:
            price = tick.bid
        else:
            return 0

        margin_req = price * volume * EIAccount.UNIT_SIZE / EIAccount.LEVERAGE
        free_margin = self.free_margin(tick)

        if margin_req > free_margin:
            # print(f"Not enough free margin. free margin: {free_margin}, margin_req: {margin_req}")
            return 0

        self.account.margin_lock(tick.datetime, margin_req)
        pos = self.trade.open_position(tick.symbol, tick.datetime,
                                        position_type, volume, price, margin_req)
        # self.print_account_info(tick)

        return pos.id

    def get_last_open_position(self) -> EIPosition:
        """Return the latest opened position"""
        return self.trade.get_last_open_position()

    def long_buy(self, tick: Tick, volume: float) -> int:
        """Open long/buy position and returns position id"""
        return self.open_position(tick, PositionType.LONG_BUY, volume)

    def short_sell(self, tick: Tick, volume: float) -> int:
        """Open short/sell position and returns position id"""
        return self.open_position(tick, PositionType.SHORT_SELL, volume)

    def close_position(self, position_id: int, tick: Tick) -> bool:
        """Close a position"""
        pos = self.trade.close_position(position_id, tick)

        if pos is None:
            return False

        self.account.close_trade(tick.datetime, pos.margin, pos.get_profit())
        return True

    def get_data(self) -> pd.DataFrame:
        """Return data"""
        if self.data is None:
            return None

        return self.data.copy()

    def get_positions(self, as_data_frame: bool=True) -> list[EIPosition] | pd.DataFrame:
        """Return list of position"""
        if len(self.trade.get_positions()) <= 0:
            return None

        if as_data_frame:
            return pd.DataFrame([pos.as_dict()
                                 for pos in self.trade.get_positions()]).set_index("id")
        else:
            return self.trade.get_positions().copy()

    def get_orders(self, as_data_frame: bool=True) -> list[EIOrder] | pd.DataFrame:
        """Return list of order"""
        if len(self.trade.get_orders()) <= 0:
            return None

        if as_data_frame:
            return pd.DataFrame([order.as_dict()
                                 for order in self.trade.get_orders()]).set_index("id")
        else:
            return self.trade.get_orders().copy()

    def get_deals(self, as_data_frame: bool=True) -> list[EIDeal] | pd.DataFrame:
        """Return list of deal"""
        if len(self.trade.get_deals()) <= 0:
            return None

        if as_data_frame:
            return pd.DataFrame([deal.as_dict()
                                 for deal in self.trade.get_deals()]).set_index("id")
        else:
            return self.trade.get_deals().copy()

    def get_equity_records(self) -> pd.DataFrame:
        """Return equity and balance history"""
        if len(self.equity_records) <= 0:
            return None

        df = pd.DataFrame.from_dict(self.equity_records).set_index(
            "datetime")
        df = df.loc[~df.index.duplicated(keep='first')]

        return df.sort_index()

    def plot_equity_records(self):
        """Plot equity and balance history"""
        title = "Balance vs Equity"
        equity_records = self.get_equity_records()
        equity_records[["balance", "equity"]].plot(
            title=title, figsize=(12, 8))

    def account_ledger(self) -> pd.DataFrame:
        """Return account's transaction history"""
        return self.account.get_ledger()

    def print_account_info(self, tick: Tick):
        """Print out account info on a given tick"""
        print(f"balance: {self.balance()}, "
              f"equity: {self.equity(tick)}, "
              f"margin: {self.margin_used()}, freeMargin: {self.free_margin(tick)}, "
              f"marginLevel: {self.margin_level(tick)}%, "
              f"gain: {self.realized_net_profit()}, fProfit: {self.floating_profit(tick)}")

    def print_open_positions(self, tick: Tick):
        """Print out current open positions"""
        positions = self.trade.get_all_open_position()
        for pos in positions:
            if pos.type == PositionType.LONG_BUY:
                current_price = tick.bid
            elif pos.type == PositionType.SHORT_SELL:
                current_price = tick.ask
            else:
                current_price = 0

            print(f"symbol: {pos.symbol.value}, id: {pos.id}, "
                  f"time: {pos.open_datetime}, type: {pos.type}, "
                  f"volume: {pos.volume}, openPrice: {pos.open_price()}, "
                  f"currentPrice: {current_price}, profit: {pos.get_profit()}")

    def populate_report(self):
        """Populate report data"""
        trade = self.trade.get_report()
        report = BacktestingReport()

        report.summary.ticks = self.tick_count
        report.summary.initial_balance = self.account.initial_balance
        report.summary.final_balance = self.account.actual_balance
        report.summary.net_profit = trade.net_profit
        report.summary.gross_profit = trade.gross_profit
        report.summary.gross_loss = trade.gross_loss

        self.calculate_drawdown(report)

        report.measurement.profit_factor = trade.gross_profit / \
            abs(trade.gross_loss) if trade.gross_loss != 0 else 0
        report.measurement.recovery_factor = trade.net_profit / \
            report.equity_drawdown.max if report.equity_drawdown.max != 0 else 0
        report.measurement.expected_payoff = trade.net_profit / \
            trade.all_position.total if trade.all_position.total != 0 else 0
        report.measurement.margin_level = self.min_margin_level

        report.trade.all_position.total = trade.all_position.total
        report.trade.all_position.won = trade.all_position.won
        report.trade.all_position.lost = trade.all_position.lost

        report.trade.long_position.total = trade.long_position.total
        report.trade.long_position.won = trade.long_position.won
        report.trade.long_position.lost = trade.long_position.lost

        report.trade.short_position.total = trade.short_position.total
        report.trade.short_position.won = trade.short_position.won
        report.trade.short_position.lost = trade.short_position.lost

        report.trade.total_orders = trade.total_orders
        report.trade.total_deals = trade.total_deals
        report.trade.largest_profit = trade.largest_profit
        report.trade.largest_loss = trade.largest_loss
        report.trade.average_profit = trade.average_profit
        report.trade.average_loss = trade.average_loss

        report.trade.max_consecutive_wins = trade.max_consecutive_wins
        report.trade.max_consecutive_losses = trade.max_consecutive_losses

        report.trade.avg_consecutive_wins = trade.avg_consecutive_wins
        report.trade.avg_consecutive_losses = trade.avg_consecutive_losses

        self.report = report

    def calculate_drawdown(self, report: BacktestingReport):
        """Calculate balance and equity drawdown"""
        initial = {"balance": self.account.initial_balance,
                   "equity": self.account.initial_balance}
        lowest = initial.copy()
        highest = initial.copy()
        current_drawdown = {"balance": 0, "equity": 0}
        max_drawdown = current_drawdown.copy()

        for record in self.equity_records:
            if record["balance"] > highest["balance"]:
                highest["balance"] = record["balance"]

            if record["balance"] < lowest["balance"]:
                lowest["balance"] = record["balance"]

            if record["equity"] > highest["equity"]:
                highest["equity"] = record["equity"]

            if record["equity"] < lowest["equity"]:
                lowest["equity"] = record["equity"]

            current_drawdown["balance"] = highest["balance"] - \
                record["balance"]
            current_drawdown["equity"] = highest["equity"] - \
                record["equity"]

            if current_drawdown["balance"] > max_drawdown["balance"]:
                max_drawdown["balance"] = current_drawdown["balance"]

            if current_drawdown["equity"] > max_drawdown["equity"]:
                max_drawdown["equity"] = current_drawdown["equity"]

            report.balance_drawdown.abs = initial["balance"] - \
                lowest["balance"]
            report.balance_drawdown.max = max_drawdown["balance"]
            report.balance_drawdown.rel = max_drawdown["balance"] / \
                highest["balance"] * 100

            report.equity_drawdown.abs = initial["equity"] - \
                lowest["equity"]
            report.equity_drawdown.max = max_drawdown["equity"]
            report.equity_drawdown.rel = max_drawdown["equity"] / \
                highest["equity"] * 100

    def get_report(self, do_print: bool=False):
        """Return report data"""
        if do_print:
            lf = "\n"
            rep = self.report
            print(f"BACKTESTING REPORT{lf}"
                  f"1. Summary{lf}"
                  f"    ◦ Ticks: {rep.summary.ticks}{lf}"
                  f"    ◦ Initial Balance: {rep.summary.initial_balance}{lf}"
                  f"    ◦ Final Balance: {round(rep.summary.final_balance, 2)}{lf}"
                  f"    ◦ Net Profit: {round(rep.summary.net_profit, 2)}{lf}"
                  f"    ◦ Gross Profit: {round(rep.summary.gross_profit, 2)}{lf}"
                  f"    ◦ Gross Loss: {round(rep.summary.gross_loss, 2)}{lf}"
                  f"2. Drawdown{lf}"
                  f"   Balance Drawdown{lf}"
                  f"    ◦ Abs: {round(rep.balance_drawdown.abs, 2)}, "
                  f"Max: {round(rep.balance_drawdown.max, 2)}, "
                  f"Rel: {round(rep.balance_drawdown.rel, 2)}{lf}"
                  f"   Equity Drawdown{lf}"
                  f"    ◦ Abs: {round(rep.equity_drawdown.abs, 2)}, "
                  f"Max: {round(rep.equity_drawdown.max, 2)}, "
                  f"Rel: {round(rep.equity_drawdown.rel, 2)}{lf}"
                  f"3. Measurement{lf}"
                  f"    ◦ Profit Factor: {round(rep.measurement.profit_factor, 2)}{lf}"
                  f"    ◦ Recovery Factor: {round(rep.measurement.recovery_factor, 2)}{lf}"
                  f"    ◦ Expected Payoff: {round(rep.measurement.expected_payoff, 2)}{lf}"
                  f"    ◦ Margin Level: {round(rep.measurement.margin_level, 2)}{lf}"
                  f"4. Trade{lf}"
                  f"    ◦ All Position:{lf}"
                  f"       ◦ Total: {rep.trade.all_position.total}, "
                  f"Won: {rep.trade.all_position.won}, "
                  f"Lost: {rep.trade.all_position.lost}{lf}"
                  f"    ◦ Long Position:{lf}"
                  f"       ◦ Total: {rep.trade.long_position.total}, "
                  f"Won: {rep.trade.long_position.won}, "
                  f"Lost: {rep.trade.long_position.lost}{lf}"
                  f"    ◦ Short Position:{lf}"
                  f"       ◦ Total: {rep.trade.short_position.total}, "
                  f"Won: {rep.trade.short_position.won}, "
                  f"Lost: {rep.trade.short_position.lost}{lf}"
                  f"    ◦ Total Orders: {rep.trade.total_orders}{lf}"
                  f"    ◦ Total Deals: {rep.trade.total_deals}{lf}"
                  f"    ◦ Largest Profit: {round(rep.trade.largest_profit, 2)}{lf}"
                  f"    ◦ Largest Loss: {round(rep.trade.largest_loss, 2)}{lf}"
                  f"    ◦ Average Profit: {round(rep.trade.average_profit, 2)}{lf}"
                  f"    ◦ Average Loss: {round(rep.trade.average_loss, 2)}{lf}"
                  f"    ◦ Max Consecutive Wins:{lf}"
                  f"       ◦ Total: {rep.trade.max_consecutive_wins[0]}, "
                  f"Profit: {round(rep.trade.max_consecutive_wins[1], 2)}{lf}"
                  f"       ◦ Average: {round(rep.trade.avg_consecutive_wins, 2)}{lf}"
                  f"    ◦ Max Consecutive Losses:{lf}"
                  f"       ◦ Total: {rep.trade.max_consecutive_losses[0]}, "
                  f"Profit: {round(rep.trade.max_consecutive_losses[1], 2)}{lf}"
                  f"       ◦ Average: {round(rep.trade.avg_consecutive_losses, 2)}{lf}")

        return self.report
