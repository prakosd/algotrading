"""
Deal Component for Backtesting Operations.

Provides the Deal class representing completed trading deals with thread-safe
ID generation, execution tracking, and serialization capabilities.
"""
from dataclasses import dataclass, field
from typing import ClassVar, Any
from datetime import datetime as dt
import threading

from ....common.trade import DealType
from ....common.asset import AssetPairCode as Symbol

@dataclass
class Deal():
    """
    Thread-safe trading deal with auto-generated ID and serialization.
    
    Represents a completed trade execution with symbol, timestamp, type (BUY/SELL),
    volume, and price. Features thread-safe ID generation for concurrent environments.
    
    Attributes:
        id (int): Auto-generated unique identifier
        symbol (Symbol): Asset pair symbol
        datetime (dt): Execution timestamp
        type (DealType): Deal type (BUY or SELL)
        volume (float): Executed volume
        price (float): Execution price
        
    Example:
        >>> deal = Deal(Symbol.EURUSD, datetime.now(), DealType.BUY, 1.0, 1.2345)
        >>> print(f"Deal {deal.id}: {deal.type.name} {deal.volume}")
    """
    _next_id: ClassVar[int] = 0
    _id_lock: ClassVar[threading.Lock] = threading.Lock()

    id: int = field(init=False)
    symbol: Symbol
    datetime: dt
    type: DealType
    volume: float
    price: float

    @classmethod
    def reset_id(cls) -> None:
        """Reset deal ID counter to zero (thread-safe)."""
        with cls._id_lock:
            cls._next_id = 0

    @classmethod
    def generate_id(cls) -> int:
        """Generate next unique deal ID (thread-safe)."""
        with cls._id_lock:
            new_id = cls._next_id
            cls._next_id += 1
            return new_id

    def __post_init__(self) -> None:
        """Initialize deal with auto-generated unique ID."""
        self.id = self.generate_id()

    def as_dict(self) -> dict[str, Any]:
        """Convert deal to dictionary for serialization."""
        return {'id': self.id, 'symbol': self.symbol.value, 'datetime': self.datetime,
                'type': self.type.name, 'volume': self.volume, 'price': self.price}
