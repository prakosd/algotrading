"""Module to trade report data definition"""
from dataclasses import dataclass, field

@dataclass
class PositionReport:
    """Position report data definition"""
    total: int = 0
    won: int = 0
    lost: int = 0

@dataclass
class TradeReport:
    """Trade report data definition"""
    net_profit: float = 0
    gross_profit: float = 0
    gross_loss: float = 0
    all_position: PositionReport = field(default_factory = PositionReport)
    long_position: PositionReport = field(default_factory = PositionReport)
    short_position: PositionReport = field(default_factory= PositionReport)
    total_orders: int = 0
    total_deals: int = 0
    largest_profit: float = 0
    largest_loss: float = 0
    average_profit: float = 0
    average_loss: float = 0
    max_consecutive_wins: [int, float] = field(default_factory = lambda: [0, 0])
    max_consecutive_losses: [int, float] = field(default_factory = lambda: [0, 0])
    avg_consecutive_wins: float = 0
    avg_consecutive_losses: float = 0
