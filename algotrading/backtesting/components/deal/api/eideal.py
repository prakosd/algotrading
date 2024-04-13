"""Module of Deal Entity Interface"""
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from typing import ClassVar
from datetime import datetime as dt

from .....common.trade import DealType
from .....common.asset import AssetPairCode as Symbol

@dataclass
class EIDeal(ABC):
    """Deal Entity Interface"""
    _next_id: ClassVar[int] = 0

    id: int = field(init=False)
    symbol: Symbol
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

    @abstractmethod
    def as_dict(self) -> dict:
        """Return deal as dictionary"""
