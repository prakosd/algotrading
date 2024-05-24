"""Module of Iterative Base Entity Interface"""
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from typing import ClassVar, Callable
import pandas as pd

from .....common.config import config
from .....common.trade import MarginHealth, PositionType
from ....components.trade import Trade
from ....components.position import Position
from ....components.order import Order
from ....components.deal import Deal
from .....ticker import Ticker, Tick
from ....components.account import Account
from .....backtesting import BacktestingReport

@dataclass
class EIIterativeBase(ABC):
    """Iterative Base Entity Interface"""
    MARGIN_CALL_LEVEL: ClassVar[float] = config.account.margin_call_level
    STOP_OUT_LEVEL: ClassVar[float] = config.account.stop_out_level

    trade: Trade
    ticker: Ticker
    account: Account

    data: pd.DataFrame = field(init=False)
    is_interrupted: bool = field(init=False)
    is_running: bool = field(init=False)
    equity_records: list[dict] = field(init=False)
    report: BacktestingReport = field(init=False)
    tick_count: int = field(init=False)
    min_margin_level: float = field(init=False)

    @abstractmethod
    def __post_init__(self):
        """Post initialization"""
        self.is_interrupted = False
        self.is_running = False
        self.equity_records = []
        self.report = None
        self.tick_count = 0
        self.min_margin_level = None

    @abstractmethod
    def prepare_data(self):
        """Prepare data to test"""

    @abstractmethod
    def print_iteration(self, i: int, length: int):
        """Print iteration progress"""

    @abstractmethod
    def start(self, length: int, callback: Callable):
        """Start the iteration"""

    @abstractmethod
    def stop(self):
        """Stop the iteration"""

    @abstractmethod
    def margin_health(self, tick: Tick) -> MarginHealth:
        """Return margin health on given tick"""

    @abstractmethod
    def margin_used(self) -> float:
        """Return total margin in use"""

    @abstractmethod
    def margin_level(self, tick: Tick) -> float:
        """Return current percentage of margin level"""

    @abstractmethod
    def equity(self, tick: Tick) -> float:
        """Return current equity"""

    @abstractmethod
    def balance(self) -> float:
        """Return current balance"""

    @abstractmethod
    def record_equity(self, tick: Tick):
        """Record equity on a given tick"""

    @abstractmethod
    def floating_profit(self, tick: Tick) -> float:
        """Return current unrealized profit/loss"""

    @abstractmethod
    def realized_net_profit(self) -> float:
        """Return current realized profit/loss"""

    @abstractmethod
    def free_margin(self, tick: Tick) -> float:
        """Return current free margin"""

    @abstractmethod
    def close_all_position(self, tick: Tick) -> bool:
        """Close all open positions"""

    @abstractmethod
    def open_position(self, tick: Tick, position_type: PositionType,
                       volume: float) -> int:
        """Open long/buy or short/sell position and returns position id"""

    @abstractmethod
    def get_last_open_position(self) -> Position:
        """Return the latest opened position"""

    @abstractmethod
    def long_buy(self, tick: Tick, volume: float) -> int:
        """Open long/buy position and returns position id"""

    @abstractmethod
    def short_sell(self, tick: Tick, volume: float) -> int:
        """Open short/sell position and returns position id"""

    @abstractmethod
    def close_position(self, position_id: int, tick: Tick) -> bool:
        """Close a position"""

    @abstractmethod
    def get_data(self) -> pd.DataFrame:
        """Return data"""

    @abstractmethod
    def get_positions(self, as_data_frame: bool=True) -> list[Position] | pd.DataFrame:
        """Return list of position"""

    @abstractmethod
    def get_orders(self, as_data_frame: bool=True) -> list[Order] | pd.DataFrame:
        """Return list of order"""

    @abstractmethod
    def get_deals(self, as_data_frame: bool=True) -> list[Deal] | pd.DataFrame:
        """Return list of deal"""

    @abstractmethod
    def get_equity_records(self) -> pd.DataFrame:
        """Return equity and balance history"""

    @abstractmethod
    def plot_equity_records(self):
        """Plot equity and balance history"""

    @abstractmethod
    def account_ledger(self) -> pd.DataFrame:
        """Return account's transaction history"""

    @abstractmethod
    def print_account_info(self, tick: Tick):
        """Print out account info on a given tick"""

    @abstractmethod
    def print_open_positions(self, tick: Tick):
        """Print out current open positions"""

    @abstractmethod
    def populate_report(self):
        """Populate report data"""

    @abstractmethod
    def get_report(self, do_print: bool=False):
        """Return report data"""
