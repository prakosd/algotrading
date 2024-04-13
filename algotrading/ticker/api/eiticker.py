"""Module of Ticker Entity Interface"""
from dataclasses import dataclass
from abc import ABC, abstractmethod
from datetime import datetime as dt
from typing import Self
import pandas as pd

from ...common.trade import Timeframe
from ...common.asset import AssetPairCode as Symbol
from .eitick import EITick

@dataclass
class EITicker(ABC):
    """Ticker Entity Interface"""
    symbol: Symbol
    start: dt
    end: dt
    timeframe: Timeframe
    data: pd.DataFrame

    @abstractmethod
    def get_data(self, index: int = None,
                 datetime: str = None) -> pd.DataFrame | EITick | None:
        """Return ticker data"""

    @abstractmethod
    def get_timezone(self) -> str:
        """Return ticker timezone"""

    @abstractmethod
    def get_length(self) -> int:
        """Return number of tick"""

    @abstractmethod
    def get_digit(self) -> int:
        """Return symbol's decimal place"""

    @abstractmethod
    def plot(self):
        """Plot ticker data"""

    @abstractmethod
    def resample(self, to_timeframe: Timeframe) -> pd.DataFrame | None:
        """Resample ticker data from lower to higher timeframe"""

    @abstractmethod
    def append(self, ticker: Self) -> pd.DataFrame | None:
        """Append ticker data with ticker of the same symbol and timeframe"""

    @abstractmethod
    def analyze(self, plot_data: bool=True) -> pd.DataFrame:
        """Analyze ticker data and return the result"""
