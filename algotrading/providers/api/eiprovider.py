"""Module of Provider Entity Interface"""
from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import ClassVar
from datetime import datetime as dt
import os.path
import pandas as pd

from ...common.config import config
from ...common.trade import Timeframe
from ...common.asset import AssetPairCode as Symbol
from ...ticker import Ticker

@dataclass
class EIProvider(ABC):
    """Provider Entity Interface"""
    _COMMON_DATA_DIR: ClassVar[str] = config.common.data_directory
    _COMMON_FILE_EXT: ClassVar[str] = config.common.file_extension
    _SYMBOL_FILENAME: ClassVar[str] = config.common.asset_pair_provider_filename
    _SYMBOLS: ClassVar[pd.DataFrame] = None

    OANDA: ClassVar[str] = "OANDA"

    symbol: Symbol
    start: dt
    end: dt
    timeframe: Timeframe

    @classmethod
    def get_symbols(cls, reload: bool=False) -> pd.DataFrame:
        """Return list of symbols by provider"""
        if cls._SYMBOLS is None or reload:
            directory = cls._COMMON_DATA_DIR
            filename = cls._SYMBOL_FILENAME + cls._COMMON_FILE_EXT

            if os.path.exists(directory + filename):
                cls._SYMBOLS = pd.read_csv(directory + filename)
            else:
                raise FileNotFoundError(f"{directory + filename}")

        return cls._SYMBOLS

    @classmethod
    def translate_symbol(cls, provider: str, symbol: Symbol, reload: bool=False) -> str:
        """Translate system symbol code to provider's symbol code"""
        df = cls.get_symbols(reload)
        return df.loc[(df['PROVIDER'] == provider)
                      & (df['SYSTEM_CODE'] == symbol.value), 'PROVIDER_CODE'].iloc[0]

    @classmethod
    @abstractmethod
    def get_instruments(cls, force_download: bool=False) -> pd.DataFrame:
        """Return available instruments"""

    @abstractmethod
    def get_response(self, force_download: bool=False) -> pd.DataFrame:
        """Return response from provider"""

    @abstractmethod
    def get_filename(self) -> str:
        """Generate and return filename of saved response"""

    @abstractmethod
    def get_ticker(self, force_download: bool=False) -> Ticker:
        """Return response in Ticker object"""
