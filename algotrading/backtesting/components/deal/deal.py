"""Module of Deal Class"""
from dataclasses import dataclass, field
from typing import ClassVar
from datetime import datetime as dt

from ....common.trade import DealType
from ....common.asset import AssetPairCode as Symbol

@dataclass
class Deal():
    """Deal Class"""
    _next_id: ClassVar[int] = 0

    id: int = field(init=False)
    symbol: Symbol
    datetime: dt
    type: DealType
    volume: float
    price: float

    @classmethod
    def reset_id(cls):
        """Reset next id"""
        cls._next_id = 0

    @classmethod
    def generate_id(cls) -> int:
        """generate next id"""
        new_id = cls._next_id
        cls._next_id += 1
        return new_id

    def __post_init__(self):
        """Post initialization"""
        self.id = self.generate_id()

    def as_dict(self) -> dict:
        """Return deal as dictionary"""
        return {'id': self.id, 'symbol': self.symbol.value, 'datetime': self.datetime,
                'type': self.type.name, 'volume': self.volume, 'price': self.price}
