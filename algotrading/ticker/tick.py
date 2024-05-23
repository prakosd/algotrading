"""Module of Tick Class"""
from dataclasses import dataclass
from datetime import datetime as dt

from ..common.asset import AssetPairCode as Symbol

@dataclass
class Tick():
    """Tick Class"""
    symbol: Symbol
    datetime: dt
    ask: float
    bid: float
    mid: float
    volume: int
    digit: int
    spread: int
