"""Module of Account Entity Interface"""
from datetime import datetime as dt
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from typing import ClassVar
import pandas as pd

from .....common.config import config
from .....common.trade import TransactionType

@dataclass
class EIAccount(ABC):
    """Account Entity Interface"""
    DEPOSIT_CURRENCY: ClassVar[str] = config.account.deposit_currency
    LEVERAGE: ClassVar[int]         = config.account.leverage
    UNIT_SIZE: ClassVar[int]        = config.account.unit_size

    initial_datetime: dt
    initial_balance: float

    actual_balance: float = field(init=False)
    margin: float = field(init=False)
    ledger: list = field(init=False)

    @abstractmethod
    def __post_init__(self):
        """Post initialization"""

    @abstractmethod
    def commit_transaction(self, date_time: dt, transaction: TransactionType,
                            amount: float, message: str):
        """Commit transaction to the ledger"""

    @abstractmethod
    def clear_ledger(self) -> pd.DataFrame:
        """Remove all transaction from the ledge"""

    @abstractmethod
    def get_ledger(self) -> pd.DataFrame:
        """Return ledger as DataFrame"""

    @abstractmethod
    def reset_balance(self, datetime: dt, message: str=None) -> float:
        """Reset balance to initial value"""

    @abstractmethod
    def deposit(self, datetime: dt, amount: float, message: str=None) -> float:
        """Deposit specified amount into account"""

    @abstractmethod
    def withdraw(self, datetime: dt, amount: float, message: str=None) -> float:
        """Withdraw specified amount from account"""

    @abstractmethod
    def margin_lock(self, datetime: dt, amount: float, message: str=None) -> float:
        """Lock balance from opening a position"""

    @abstractmethod
    def margin_release(self, datetime: dt, amount: float, message: str=None) -> float:
        """Release balance from closing a position"""

    @abstractmethod
    def close_trade(self, datetime: dt, margin: float, profit: float, message: str=None) -> float:
        """Update account after closing a trade"""
