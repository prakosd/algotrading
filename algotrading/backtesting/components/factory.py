"""Module of Component Factory"""
from datetime import datetime as dt

from .account.api import EIAccount
from .account.implementation import Account

class ComponentFactory():
    """Static class to create component object"""

    @staticmethod
    def create_account(initial_datetime: dt, initial_balance: float) -> EIAccount:
        """Return new account object"""
        return Account(initial_datetime, initial_balance)
