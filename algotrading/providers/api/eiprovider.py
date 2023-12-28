"""Module of Provider Entity Interface"""
from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import ClassVar
from datetime import datetime as dt
import pandas as pd

from ...common import config
from ...common.enums import Timeframe
from ...ticker.api import EITicker

@dataclass
class EIProvider(ABC):
    """Provider Entity Interface"""
    _DATA_DIR: ClassVar[str] = config.provider.data_directory
    _FILE_EXT: ClassVar[str] = config.provider.file_extension
    PROVIDER_OANDA: ClassVar[str] = "OANDA"

    symbol: str
    start: dt
    end: dt
    timeframe: Timeframe

    @staticmethod
    @abstractmethod
    def get_instruments(force_download: bool=False) -> pd.DataFrame:
        """Return available instruments"""

    @abstractmethod
    def get_response(self, force_download: bool=False) -> pd.DataFrame:
        """Return response from provider"""

    @abstractmethod
    def get_filename(self) -> str:
        """Generate and return filename of saved response"""

    @abstractmethod
    def get_ticker(self, force_download: bool=False) -> EITicker:
        """Return response in EITicker object"""
