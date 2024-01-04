"""Module to strategy parameter set data definition"""
from dataclasses import dataclass

@dataclass
class BuyAndHoldParams:
    """Buy and hold strategy parameter set"""
    balance: float = 10000
    volume: float  = 1.0

@dataclass
class ContrarianParams(BuyAndHoldParams):
    """Contrarian strategy parameter set"""
    window: int = 1
