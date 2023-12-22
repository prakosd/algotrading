"""Module of Tick Entity Interface"""
from dataclasses import dataclass
from abc import ABC
from datetime import datetime as dt

@dataclass
class EITick(ABC):
    """Tick Entity Interface"""
    symbol: str
    datetime: dt
    ask: float
    bid: float
    mid: float
    volume: int
    digit: int
    spread: int
