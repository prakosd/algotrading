"""Module of Account Class"""
from datetime import datetime as dt
import pandas as pd

from ..api import EIAccount
from .....common.trade import TransactionType

class Account(EIAccount):
    """Implementation of EIAccount"""

    def __post_init__(self):
        """Post initialization"""
        self.actual_balance = self.initial_balance
        self.margin = 0
        self.ledger = []
        self.commit_transaction(self.initial_datetime, TransactionType.DEPOSIT,
                                 self.initial_balance, "Initial Deposit")

    def commit_transaction(self, date_time: dt, transaction: TransactionType,
                            amount: float, message: str):
        """Commit transaction to the ledger"""
        record = {'datetime': date_time, 'transaction': transaction.name,
                  'currency': EIAccount.BASE_CURRENCY, 'amount': amount,
                  'balance': self.actual_balance, 'message': message}
        self.ledger.append(record)

    def clear_ledger(self) -> pd.DataFrame:
        """Remove all transaction from the ledge"""
        first_record = self.ledger[0]
        self.ledger.clear()
        self.ledger.append(first_record)
        return pd.DataFrame.from_dict(self.ledger).set_index('datetime')

    def get_ledger(self) -> pd.DataFrame:
        """Return ledger as DataFrame"""
        return pd.DataFrame.from_dict(self.ledger).set_index('datetime')

    def reset_balance(self, datetime: dt, message: str=None) -> float:
        """Reset balance to initial value"""
        amount = self.initial_balance - self.actual_balance
        self.actual_balance = self.initial_balance
        self.commit_transaction(datetime, TransactionType.RESET, amount, message)
        return self.actual_balance

    def deposit(self, datetime: dt, amount: float, message: str=None) -> float:
        """Deposit specified amount into account"""
        self.actual_balance += amount
        self.commit_transaction(datetime, TransactionType.DEPOSIT, amount, message)
        return self.actual_balance

    def withdraw(self, datetime: dt, amount: float, message: str=None) -> float:
        """Withdraw specified amount from account"""
        self.actual_balance -= amount
        self.commit_transaction(datetime, TransactionType.WITHDRAWAL, -amount, message)
        return self.actual_balance

    def margin_lock(self, datetime: dt, amount: float, message: str=None) -> float:
        """Lock balance from opening a position"""
        self.actual_balance -= amount
        self.margin += amount
        self.commit_transaction(datetime, TransactionType.MARGIN_LOCK, -amount, message)
        return self.actual_balance

    def margin_release(self, datetime: dt, amount: float, message: str=None) -> float:
        """Release balance from closing a position"""
        self.actual_balance += amount
        self.margin -= amount
        self.commit_transaction(datetime, TransactionType.MARGIN_RELEASE, amount, message)
        return self.actual_balance

    def close_trade(self, datetime: dt, margin: float, profit: float, message: str=None) -> float:
        """Update account after closing a trade"""
        self.margin_release(datetime, margin, message)

        if profit > 0:
            transaction_type = TransactionType.PROFIT_TRADE
        elif profit < 0:
            transaction_type = TransactionType.LOSS_TRADE
        else:
            return self.actual_balance

        self.actual_balance += profit
        self.commit_transaction(datetime, transaction_type, profit, message)
        return self.actual_balance
