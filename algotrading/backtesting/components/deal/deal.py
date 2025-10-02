"""Deal component for backtesting operations."""
from dataclasses import dataclass, field
from typing import ClassVar, Any
from datetime import datetime as dt

from ....common.trade import DealType
from ....common.asset import AssetPairCode as Symbol

@dataclass
class Deal():
    """
    Represents a trading deal with auto-generated ID and conversion capabilities.
    
    A deal captures the execution of a trade including symbol, timing, type,
    volume, and price information for backtesting analysis.
    """
    _next_id: ClassVar[int] = 0

    id: int = field(init=False)
    symbol: Symbol
    datetime: dt
    type: DealType
    volume: float
    price: float

    @classmethod
    def reset_id(cls) -> None:
        """Reset the next ID counter to 0."""
        cls._next_id = 0

    @classmethod
    def generate_id(cls) -> int:
        """Generate and return the next available ID."""
        new_id = cls._next_id
        cls._next_id += 1
        return new_id

    def __post_init__(self) -> None:
        """Initialize the deal ID after object creation."""
        self.id = self.generate_id()

    def as_dict(self) -> dict[str, Any]:
        """Convert deal to dictionary format for serialization or analysis."""
        return {'id': self.id, 'symbol': self.symbol.value, 'datetime': self.datetime,
                'type': self.type.name, 'volume': self.volume, 'price': self.price}
