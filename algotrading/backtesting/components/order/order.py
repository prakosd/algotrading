"""
Order Module for Backtesting Components.

Provides the Order class for trading order management with execution tracking,
deal management, and profit calculation capabilities.
"""
from dataclasses import dataclass, field
from typing import ClassVar, Optional, Any, Union
from datetime import datetime as dt
from copy import copy
import random
import threading

from ....common.config import config
from ....common.trade import OrderType, OrderDirection
from ....common.asset import AssetPairCode as Symbol
from ....common.trade import DealType
from ..deal import Deal
from ....ticker import Tick

@dataclass
class Order():
    """
    Thread-safe trading order with execution tracking and profit calculation.
    
    Supports deterministic or randomized execution with slippage simulation.
    
    Attributes:
        id (int): Auto-generated unique identifier
        symbol (Symbol): Asset pair symbol
        datetime (dt): Order creation timestamp
        type (OrderType): Order type (MARKET_BUY, MARKET_SELL)
        direction (OrderDirection): Order direction (MARKET_IN, MARKET_OUT)
        volume (float): Total volume to execute
        price (float): Order price
        deals (list[Deal]): Executed deals list
    
    Example:
        >>> order = Order(Symbol.EURUSD, datetime.now(), OrderType.MARKET_BUY,
        ...               OrderDirection.MARKET_IN, 1.0, 1.2345)
        >>> success = order.execute()
    """
    IS_MOCK_DEAL: ClassVar[bool] = config.deal.is_mock_deal
    SLIPPAGE_POINT: ClassVar[dict[str, int]] = {"min": config.deal.slippage_point_min,
                                                 "max": config.deal.slippage_point_max}
    VOLUME_PERCENT: ClassVar[dict[str, int]] = {"min": config.deal.volume_percent_min,
                                                "max": config.deal.volume_percent_max}
    PRICE_DIVISOR: ClassVar[int] = 100000  # For slippage calculation

    _next_id: ClassVar[int] = 0
    _id_lock: ClassVar[threading.Lock] = threading.Lock()

    id: int = field(init=False)
    symbol: Symbol
    datetime: dt
    type: OrderType
    direction: OrderDirection
    volume: float
    price: float
    deals: list[Deal] = field(init=False)

    @classmethod
    def reset_id(cls) -> None:
        """Reset order ID counter to zero (thread-safe)."""
        with cls._id_lock:
            cls._next_id = 0

    @classmethod
    def generate_id(cls) -> int:
        """Generate next unique order ID (thread-safe)."""
        with cls._id_lock:
            new_id = cls._next_id
            cls._next_id += 1
            return new_id

    def __post_init__(self) -> None:
        """Initialize order with auto-generated ID and validation."""
        self.id = self.generate_id()
        self.deals: list[Deal] = []
        self._validate_order_data()

    def _validate_order_data(self) -> None:
        """Validate volume and price are positive."""
        if self.volume <= 0:
            raise ValueError("Volume must be positive")
        if self.price <= 0:
            raise ValueError("Price must be positive")

    def get_deals(self, index: Optional[int] = None) -> Union[list[Deal], Deal]:
        """Get deal by index or all deals (returns copies)."""
        if index is None:
            return self.deals.copy()

        if not 0 <= index < len(self.deals):
            raise IndexError(f"Deal index {index} out of range")
        return copy(self.deals[index])

    def get_all_deals(self) -> list[Deal]:
        """Get copy of all executed deals."""
        return self.deals.copy()

    def get_deal_by_index(self, index: int) -> Deal:
        """Get specific deal by index."""
        if not 0 <= index < len(self.deals):
            raise IndexError(f"Deal index {index} out of range")
        return copy(self.deals[index])

    def deals_length(self) -> int:
        """Get number of executed deals."""
        return len(self.deals)

    def clear_deals(self) -> None:
        """Remove all deals from order."""
        self.deals.clear()

    def execute(self, max_attempts: int = 100, _current_attempt: int = 0) -> bool:
        """Execute order recursively with recursion protection."""
        # Safety check: prevent infinite recursion
        if _current_attempt >= max_attempts:
            raise RuntimeError(f"Order execution failed: Maximum attempts ({max_attempts}) reached")

        # Check if order is already fully executed
        current_volume = self.sum_deals_volume()
        if current_volume >= self.volume:
            return True

        try:
            # Calculate remaining volume to fill
            remaining_volume = self.volume - current_volume
            if remaining_volume <= 0:
                return True

            # Create and execute a deal
            deal = self.mock_deal(self.IS_MOCK_DEAL, remaining_volume)
            self.deals.append(deal)

            # Recursive call to continue execution if needed
            if self.sum_deals_volume() < self.volume:
                return self.execute(max_attempts, _current_attempt + 1)
            else:
                return True

        except Exception as e:
            raise RuntimeError(f"Deal execution failed at attempt {_current_attempt + 1}: {e}") from e

    def get_profit(self, tick: Tick) -> float:
        """Calculate current unrealized profit/loss based on tick prices."""
        if not self.deals:
            return 0.0

        total_profit = 0.0
        for deal in self.deals:
            if deal.type == DealType.BUY:
                profit = (tick.bid - deal.price) * deal.volume
            elif deal.type == DealType.SELL:
                profit = (deal.price - tick.ask) * deal.volume
            else:
                raise ValueError(f"Unrecognized DealType: {deal.type}")

            total_profit += profit

        return total_profit * (10 ** tick.digit)

    def sum_deals_volume(self) -> float:
        """Calculate total volume of all executed deals."""
        return sum(deal.volume for deal in self.deals)

    def avg_deals_price(self) -> float:
        """Calculate volume-weighted average price of all executed deals."""
        if not self.deals:
            return 0.0

        total_deals_volume = self.sum_deals_volume()
        if total_deals_volume == 0:
            raise ValueError("Cannot calculate average price: total deals volume is zero")

        volume_price = sum(deal.volume * deal.price for deal in self.deals)
        return volume_price / total_deals_volume

    def mock_deal(self, random_deal: bool = False, max_volume: Optional[float] = None) -> Deal:
        """Create a mock deal for order execution simulation."""
        deal_type = DealType.BUY if self.type.value > 0 else DealType.SELL

        # Use max_volume if provided, otherwise use full order volume
        target_volume = max_volume if max_volume is not None else self.volume

        if not random_deal:
            return Deal(self.symbol, self.datetime,
                        deal_type, target_volume, self.price)

        # Safe access to config values with defaults
        slippage_min = self.SLIPPAGE_POINT["min"]
        slippage_max = self.SLIPPAGE_POINT["max"]
        volume_min = self.VOLUME_PERCENT["min"] 
        volume_max = self.VOLUME_PERCENT["max"]

        price = self.price + (random.randint(slippage_min, slippage_max) / self.PRICE_DIVISOR)

        volume_percent = random.randint(volume_min, volume_max) / 100
        volume = volume_percent * target_volume

        sum_vol = self.sum_deals_volume()
        if sum_vol + volume > self.volume:
            volume = self.volume - sum_vol

        return Deal(self.symbol, self.datetime, deal_type, volume, price)

    def as_dict(self) -> dict[str, Any]:
        """Convert order to dictionary representation for serialization."""
        return {'id': self.id, 'symbol': self.symbol.value, 'datetime': self.datetime,
                'type': self.type.name, 'direction': self.direction.name,
                'volume': self.volume, 'price': self.price,
                'deals_count': len(self.deals), 'total_deals_volume': self.sum_deals_volume()}
