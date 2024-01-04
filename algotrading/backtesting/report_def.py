"""Module to backtesting report data definition"""
from dataclasses import dataclass, field

@dataclass
class SummaryReport:
    """Summary report data definition"""
    ticks: int = 0
    initial_balance: float = 0
    final_balance: float = 0
    net_profit: float = 0
    gross_profit: float = 0
    gross_loss: float = 0

@dataclass
class DrawdownReport:
    """Drawdown report data definition"""
    abs: float = 0
    max: float = 0
    rel: float = 0

@dataclass
class MeasurementReport:
    """Measurement report data definition"""
    profit_factor: float = 0
    recovery_factor: float = 0
    expected_payoff: float = 0
    margin_level: float = 0

@dataclass
class PositionReport:
    """Position report data definition"""
    total: int = 0
    won: int = 0
    lost: int = 0

@dataclass
class TradeReport:
    """Trade report data definition"""
    all_position: PositionReport = field(default_factory = PositionReport)
    long_position: PositionReport = field(default_factory = PositionReport)
    short_position: PositionReport = field(default_factory = PositionReport)
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

@dataclass
class BacktestingReport:
    """Backtesting report data definition"""
    summary: SummaryReport = field(default_factory = SummaryReport)
    balance_drawdown: DrawdownReport = field(default_factory = DrawdownReport)
    equity_drawdown: DrawdownReport = field(default_factory = DrawdownReport)
    measurement: MeasurementReport = field(default_factory = MeasurementReport)
    trade: TradeReport = field(default_factory = TradeReport)
