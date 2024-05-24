"""Module of Trade Class"""
from datetime import datetime as dt

from ..api import EITrade
from .....ticker import Tick
from ...position.api import EIPosition
from ...order.api import EIOrder
from ...deal import Deal
from ...position.implementation import Position
from .....common.trade import PositionType, PositionStatus
from .....common.asset import AssetPairCode as Symbol
from ...trade import TradeReport

class Trade(EITrade):
    """Implementation of EITrade"""

    def clear_positions(self):
        """Remove all positions"""
        for pos in self.positions:
            pos.clear_orders()

        self.positions.clear()

    def open_position(self, symbol: Symbol, open_datetime: dt, pos_type: PositionType,
                      volume: float, open_price: float,
                      margin: float, comment: str = None) -> EIPosition:
        """Open and return a new position"""
        pos = Position(symbol, open_datetime, pos_type,
                       volume, open_price, margin, comment)
        self.positions.insert(0, pos)
        return pos

    def close_position(self, position_id: int, tick: Tick) -> EIPosition:
        """Close and return a position by id"""
        for pos in self.positions:
            if pos.status == PositionStatus.OPEN and pos.id == position_id:
                pos.close(tick)
                return pos

        return None

    def close_all_position(self, tick: Tick) -> list[EIPosition]:
        """Close all open position and return the list of closed position"""
        result = []
        for pos in self.positions:
            if pos.status == PositionStatus.OPEN:
                pos.close(tick)
                result.insert(0, pos)

        return result

    def get_position(self, position_id: int) -> EIPosition:
        """Return position by id"""
        for pos in self.positions:
            if pos.id == position_id:
                return pos

        return None

    def get_positions(self) -> list[EIPosition]:
        """Return a list of all position"""
        return self.positions

    def get_orders(self) -> list[EIOrder]:
        """Return a list of all order"""
        orders = []
        for pos in self.positions:
            orders.extend(pos.get_orders())

        return orders

    def get_deals(self) -> list[Deal]:
        """Return a list of all deal"""
        deals = []
        for pos in self.positions:
            for order in pos.get_orders():
                deals.extend(order.get_deals())

        return deals

    def get_all_open_position(self) -> list[EIPosition]:
        """Return a list of all open position"""
        return list(filter(lambda pos: pos.status ==
                           PositionStatus.OPEN, self.positions))

    def get_last_open_position(self) -> EIPosition:
        """Return the latest open position"""
        self.positions.sort(key=lambda pos: pos.open_datetime, reverse=True)
        for pos in self.positions:
            if pos.status == PositionStatus.OPEN:
                return pos

        return None

    def floating_profit(self, tick: Tick) -> float:
        """Return unrealized profit/loss"""
        profit = 0
        for pos in self.positions:
            if pos.status == PositionStatus.OPEN:
                profit += pos.get_profit(tick)

        return profit

    def realized_net_profit(self) -> float:
        """Return realized net profit"""
        net_profit = 0
        for pos in self.positions:
            net_profit += pos.get_profit()

        return net_profit

    def margin_used(self) -> float:
        """Return margin being used"""
        margin = 0
        for pos in self.positions:
            if pos.status == PositionStatus.OPEN:
                margin += pos.margin

        return margin

    def get_report(self, do_print: bool=False,
              rerun: bool=False) -> TradeReport:
        """Return report"""
        if self.report is None or rerun:
            self._run_report()

        if do_print:
            self._print_report()

        return self.report

    def _run_report(self):
        """Summarize trade"""
        report = TradeReport()
        max_consecutive_wins = [0, 0]
        max_consecutive_losses = [0, 0]
        consecutive_wins = []
        consecutive_losses = []

        for pos in self.positions:
            profit = pos.get_profit()
            is_long_pos = pos.type == PositionType.LONG_BUY
            report.net_profit += profit
            report.all_position.total += 1

            report.total_orders += pos.orders_length()
            for order in pos.orders:
                report.total_deals += order.deals_length()

            if is_long_pos:
                report.long_position.total += 1
            else:
                report.short_position.total += 1

            if profit > 0:  # won
                report.gross_profit += profit
                report.all_position.won += 1

                max_consecutive_wins[0] += 1
                max_consecutive_wins[1] += profit
                if max_consecutive_losses != [0, 0]:
                    consecutive_losses.append(max_consecutive_losses[0])
                    max_consecutive_losses[0] = 0
                    max_consecutive_losses[1] = 0

                if is_long_pos:
                    report.long_position.won += 1
                else:
                    report.short_position.won += 1

                if profit > report.largest_profit:
                    report.largest_profit = profit

            elif profit < 0:  # lost
                report.gross_loss += profit
                report.all_position.lost += 1

                max_consecutive_losses[0] += 1
                max_consecutive_losses[1] += profit
                if max_consecutive_wins != [0, 0]:
                    consecutive_wins.append(max_consecutive_wins[0])
                    max_consecutive_wins[0] = 0
                    max_consecutive_wins[1] = 0

                if is_long_pos:
                    report.long_position.lost += 1
                else:
                    report.short_position.lost += 1

                if profit < report.largest_loss:
                    report.largest_loss = profit

            if max_consecutive_wins[0] > report.max_consecutive_wins[0]:
                report.max_consecutive_wins = max_consecutive_wins.copy()

            if max_consecutive_losses[0] > report.max_consecutive_losses[0]:
                report.max_consecutive_losses = max_consecutive_losses.copy()

        if max_consecutive_wins != [0, 0]:
            consecutive_wins.append(max_consecutive_wins[0])
            max_consecutive_wins[0] = 0
            max_consecutive_wins[1] = 0

        if max_consecutive_losses != [0, 0]:
            consecutive_losses.append(max_consecutive_losses[0])
            max_consecutive_losses[0] = 0
            max_consecutive_losses[1] = 0

        if report.all_position.won > 0:
            report.average_profit = report.gross_profit / report.all_position.won
        if report.all_position.lost > 0:
            report.average_loss = report.gross_loss / report.all_position.lost

        if len(consecutive_wins) > 0:
            report.avg_consecutive_wins = sum(consecutive_wins) / len(consecutive_wins)
        if len(consecutive_losses) > 0:
            report.avg_consecutive_losses = sum(consecutive_losses) / len(consecutive_losses)

        self.report = report

    def _print_report(self):
        rep = self.report
        lf = "\n"
        print(f"--- TRADE RECAP ---{lf}"
              f"Net Profit: {rep.net_profit}{lf}"
              f"Gross Profit: {rep.gross_profit}{lf}"
              f"Gross Loss: {rep.gross_loss}{lf}"
              f"All Position:{lf}"
              f" - Total: {rep.all_position.total}, "
              f"Won: {rep.all_position.won}, "
              f"Lost: {rep.all_position.lost}{lf}"
              f"Long Position:{lf}"
              f" - Total: {rep.long_position.total}, "
              f"Won: {rep.long_position.won}, "
              f"Lost: {rep.long_position.lost}{lf}"
              f"Short Position:{lf}"
              f" - Total: {rep.short_position.total}, "
              f"Won: {rep.short_position.won}, "
              f"Lost: {rep.short_position.lost}{lf}"
              f"Total Orders: {rep.total_orders}{lf}"
              f"Total Deals: {rep.total_deals}{lf}"
              f"Largest Profit: {rep.largest_profit}{lf}"
              f"Largest Loss: {rep.largest_loss}{lf}"
              f"Average Profit: {rep.average_profit}{lf}"
              f"Average Loss: {rep.average_loss}{lf}"
              f"Max Consecutive Wins:{lf}"
              f" - Total: {rep.max_consecutive_wins[0]}, "
              f"Profit: {rep.max_consecutive_wins[1]}{lf}"
              f" - Average: {rep.avg_consecutive_wins}{lf}"
              f"Max Consecutive Losses:{lf}"
              f" - Total: {rep.max_consecutive_losses[0]}, "
              f"Profit: {rep.max_consecutive_losses[1]}{lf}"
              f" - Average: {rep.avg_consecutive_losses}{lf}")
