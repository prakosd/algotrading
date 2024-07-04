"""Module of Ticker Metadata Definition"""
from dataclasses import dataclass
from datetime import datetime as dt

from ..common.asset import AssetPairCode as Symbol
from ..common.trade import Timeframe

@dataclass(frozen=True)
class TickerMetadata:
    """Ticker Metadata Definition"""
    provider: str
    symbol: Symbol
    start: dt
    end: dt
    timeframe: Timeframe
