"""Module of Deal Entity Interface"""
from dataclasses import dataclass, field
from abc import ABC
from typing import ClassVar
from datetime import datetime as dt

from .....common.enums import DealType

@dataclass
class EIDeal(ABC):
    """Deal Entity Interface"""
    _next_id: ClassVar[int] = 0

    id: int = field(init=False)
    symbol: str
    datetime: dt
    type: DealType
    volume: float
    price: float

    @staticmethod
    def reset_id():
        """Reset next id"""
        EIDeal._next_id = 0

    @staticmethod
    def generate_id() -> int:
        """generate next id"""
        new_id = EIDeal._next_id
        EIDeal._next_id += 1
        return new_id

    def __post_init__(self):
        """Post initialization"""
        self.id = EIDeal.generate_id()

    def as_dict(self) -> dict:
        """Return deal as dictionary"""
        return {'id': self.id, 'symbol': self.symbol, 'datetime': self.datetime,
                'type': self.type.name, 'volume': self.volume, 'price': self.price}
