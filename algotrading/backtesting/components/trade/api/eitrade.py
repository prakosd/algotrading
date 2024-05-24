"""Module of Trade Entity Interface"""
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from datetime import datetime as dt

from ...trade import TradeReport
from ...position import Position
from ...order import Order
from ...deal import Deal
from .....common.trade import PositionType
from .....common.asset import AssetPairCode as Symbol
from .....ticker import Tick

@dataclass
class EITrade(ABC):
    """Trade Entity Interface"""
    report: TradeReport = field(init=False)
    positions: list[Position] = field(init=False)

    def __post_init__(self):
        """Post initialization"""
        self.report = None
        self.positions = []

    @abstractmethod
    def clear_positions(self):
        """Remove all positions"""

    @abstractmethod
    def open_position(self, symbol: Symbol, open_datetime: dt, pos_type: PositionType,
                      volume: float, open_price: float,
                      margin: float, comment: str = None) -> Position:
        """Open and return a new position"""

    @abstractmethod
    def close_position(self, position_id: int, tick: Tick) -> Position:
        """Close and return a position by id"""

    @abstractmethod
    def close_all_position(self, tick: Tick) -> list[Position]:
        """Close all open position and return the list of closed position"""

    @abstractmethod
    def get_position(self, position_id: int) -> Position:
        """Return position by id"""

    @abstractmethod
    def get_positions(self) -> list[Position]:
        """Return a list of all position"""

    @abstractmethod
    def get_orders(self) -> list[Order]:
        """Return a list of all order"""

    @abstractmethod
    def get_deals(self) -> list[Deal]:
        """Return a list of all deal"""

    @abstractmethod
    def get_all_open_position(self) -> list[Position]:
        """Return a list of all open position"""

    @abstractmethod
    def get_last_open_position(self) -> Position:
        """Return the latest open position"""

    @abstractmethod
    def floating_profit(self, tick: Tick) -> float:
        """Return unrealized profit/loss"""

    @abstractmethod
    def realized_net_profit(self) -> float:
        """Return realized net profit"""

    @abstractmethod
    def margin_used(self) -> float:
        """Return margin being used"""

    @abstractmethod
    def get_report(self, do_print: bool=False,
              rerun: bool=False) -> TradeReport:
        """Return report"""
