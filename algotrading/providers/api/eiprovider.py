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
from ...ticker.api import EITicker

@dataclass
class EIProvider(ABC):
    """Provider Entity Interface"""
    _DATA_DIR: ClassVar[str] = config.provider.data_directory
    _FILE_EXT: ClassVar[str] = config.provider.file_extension
    _SYMBOLS_DATA_DIR: ClassVar[str] = config.common.data_directory
    _SYMBOLS_FILE_EXT: ClassVar[str] = config.common.file_extension
    _SYMBOLS_FILENAME: ClassVar[str] = config.common.provider_symbol_filename
    _SYMBOLS: ClassVar[pd.DataFrame] = None

    PROVIDER_OANDA: ClassVar[str] = "OANDA"

    symbol: Symbol
    start: dt
    end: dt
    timeframe: Timeframe

    @staticmethod
    def get_symbols(reload: bool=False) -> pd.DataFrame:
        """Return list of symbols by provider"""
        if EIProvider._SYMBOLS is None or reload:
            directory = EIProvider._SYMBOLS_DATA_DIR
            filename = EIProvider._SYMBOLS_FILENAME + EIProvider._SYMBOLS_FILE_EXT

            if os.path.exists(directory + filename):
                EIProvider._SYMBOLS = pd.read_csv(directory + filename)
            else:
                raise FileNotFoundError(f"{directory + filename}")

        return EIProvider._SYMBOLS

    @staticmethod
    def translate_symbol(provider: str, symbol: Symbol, reload: bool=False) -> str:
        """Translate system symbol code to provider's symbol code"""
        df = EIProvider.get_symbols(reload)
        return df.loc[(df['PROVIDER'] == provider)
                      & (df['SYMBOL_CODE'] == symbol.value), 'PROVIDER_CODE'].iloc[0]

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
