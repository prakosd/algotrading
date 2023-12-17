"""Module for enums"""
from enum import Enum

class Granularity(Enum):
    """List of available granularity"""
    SECOND_5  = "S5"
    SECOND_15 = "S15"
    SECOND_30 = "S30"
    MINUTE_1  = "M1"
    MINUTE_15 = "M15"
    HOUR_1    = "H1"
    HOUR_4    = "H4"
    DAY_1     = "D"
