"""Module of Provider Entity Interface"""
from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import ClassVar
from datetime import datetime as dt
import pandas as pd

from ...config import config
from .enums import Granularity

@dataclass
class EIProvider(ABC):
    """Provider Entity Interface"""
    _DATA_DIR: ClassVar[str] = config.provider.data_directory
    _FILE_EXT: ClassVar[str] = config.provider.file_extension
    PROVIDER_OANDA: ClassVar[str] = "OANDA"

    symbol: str
    start: dt
    end: dt
    granularity: Granularity

    @staticmethod
    @abstractmethod
    def get_instruments(force_download: bool=False) -> pd.DataFrame:
        """Returns available instruments"""

    @abstractmethod
    def get_response(self, force_download: bool=False) -> pd.DataFrame:
        """Returns response from the provider"""

    @abstractmethod
    def get_filename(self) -> str:
        """Return filename of saved response"""
