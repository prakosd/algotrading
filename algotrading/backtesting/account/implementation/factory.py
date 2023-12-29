"""Module of Account Factory"""
from datetime import datetime as dt

from ..api.eiaccount import EIAccount
from .account import Account

class AccountFactory():
    """Static class to create account object"""

    @staticmethod
    def create_account(initial_datetime: dt, initial_balance: float) -> EIAccount:
        """Return new account object"""
        return Account(initial_datetime, initial_balance)
