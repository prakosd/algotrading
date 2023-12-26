"""Module for enums"""
from enum import Enum
from collections import namedtuple

TimeframeTuple = namedtuple('Timeframe', ['id', 'granularity', 'resample', 'description'])

class Timeframe(Enum):
    """List of available timeframe"""
    SECOND_5  = TimeframeTuple(0, "S5", "5S",  "5 Seconds")
    SECOND_15 = TimeframeTuple(1, "S15", "15S", "15 Seconds")
    SECOND_30 = TimeframeTuple(2, "S30", "30S", "30 Seconds")
    MINUTE_1  = TimeframeTuple(3, "M1", "1T",  "1 Minute")
    MINUTE_15 = TimeframeTuple(4, "M15", "15T", "15 Minutes")
    HOUR_1    = TimeframeTuple(5, "H1", "1H",  "1 Hour")
    HOUR_4    = TimeframeTuple(6, "H4", "4H",  "4 Hours")
    DAY_1     = TimeframeTuple(7, "D", "1D",  "1 Day")
