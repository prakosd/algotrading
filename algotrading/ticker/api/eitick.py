"""Module of Tick Entity Interface"""
from dataclasses import dataclass
from abc import ABC
from datetime import datetime as dt

from ...common.symbol import Symbol

@dataclass
class EITick(ABC):
    """Tick Entity Interface"""
    symbol: Symbol
    datetime: dt
    ask: float
    bid: float
    mid: float
    volume: int
    digit: int
    spread: int
