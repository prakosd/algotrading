"""Module of Ticker Manager Class"""
from dataclasses import dataclass
from typing import ClassVar
from datetime import datetime as dt
import pandas as pd
import numpy as np

from ..data import DataManager
from .metadata import TickerMetadata
from ..common.asset import AssetPairCode as Symbol
from ..common.trade import Timeframe
from .ticker import Ticker

@dataclass
class TickerManager(DataManager):
    """Ticker Manager Class"""
    _TICKER_DATA: ClassVar[pd.DataFrame] = None
    _SEPARATOR: ClassVar[str] = "_"
    _DATE_FORMAT = "%Y-%m-%d"
    _PROVIDER: ClassVar[str] = "PROVIDER"
    _SYMBOL: ClassVar[str] = "SYMBOL"
    _TIMEFRAME: ClassVar[str] = "TIMEFRAME"
    _START: ClassVar[str] = "START"
    _END: ClassVar[str] = "END"
    _INDEX_COL: ClassVar[str] = "time"

    @classmethod
    def find(cls, name: str=None, ext: str=None, reload: bool=False) -> pd.DataFrame:
        """Return list of ticker data"""
        if cls._TICKER_DATA is None or reload:
            cls._TICKER_DATA = super().find(name=name, ext=ext, reload=reload)
            cls.populate()

        return cls._TICKER_DATA.copy()

    @classmethod
    def find_by_metadata(cls, metadata: TickerMetadata,
                         reload: bool=False) -> pd.DataFrame | Ticker:
        """Return locally saved ticker"""
        if not cls.validate_metadata(metadata):
            return None

        df = cls.find(reload=reload)
        df = df.dropna(subset=[cls._PROVIDER, cls._SYMBOL, cls._START, cls._END, cls._TIMEFRAME])

        if df is None or len(df) == 0:
            return None

        if metadata.provider is not None:
            df = df[df[cls._PROVIDER].str.contains(metadata.provider, case=False)]

        if metadata.symbol is not None:
            df = df[df[cls._SYMBOL].str.contains(metadata.symbol.value, case=False)]

        if metadata.timeframe is not None:
            df = df[df[cls._TIMEFRAME].str.contains(metadata.timeframe.name, case=False)]

        mask = (df[cls._START] <= metadata.start) & (df[cls._END] >= metadata.end)
        df = df.loc[mask]

        if len(df) == 0:
            return None

        df = df.sort_values(by=[cls._SIZE])

        filename = df[cls._NAME].iloc[0]
        ticker_metadata = cls.generate_metadata(filename)
        ticker_data = cls.read(filename, cls._INDEX_COL)

        if ticker_metadata.start == metadata.start and ticker_metadata.end == metadata.end:
            return Ticker(
                symbol    = ticker_metadata.symbol,
                start     = ticker_metadata.start,
                end       = ticker_metadata.end,
                timeframe = ticker_metadata.timeframe,
                data      = ticker_data
            )

        tz = pd.Timestamp(ticker_data.index[0]).tzinfo
        return Ticker(
                symbol    = ticker_metadata.symbol,
                start     = metadata.start,
                end       = metadata.end,
                timeframe = ticker_metadata.timeframe,
                data      = ticker_data.loc[
                    pd.Timestamp(metadata.start, tz=tz):pd.Timestamp(metadata.end, tz=tz)]
            )

    @classmethod
    def find_by_filename(cls, filename: str,
                         reload: bool=False) -> pd.DataFrame | Ticker:
        """Return locally saved ticker"""
        return cls.find_by_metadata(
            metadata = cls.generate_metadata(filename),
            reload   = reload
        )

    @classmethod
    def populate(cls):
        """Populate metadata"""
        providers = []
        symbols = []
        starts = []
        ends = []
        timeframes = []

        for value in cls._TICKER_DATA.loc[:, cls._NAME]:
            metadata = cls.generate_metadata(value)
            if metadata is None:
                providers.append(np.nan)
                symbols.append(np.nan)
                starts.append(np.nan)
                ends.append(np.nan)
                timeframes.append(np.nan)
            else:
                providers.append(metadata.provider)
                symbols.append(metadata.symbol.name)
                starts.append(metadata.start)
                ends.append(metadata.end)
                timeframes.append(metadata.timeframe.name)

        cls._TICKER_DATA.loc[:, cls._PROVIDER] = providers
        cls._TICKER_DATA.loc[:, cls._SYMBOL] = symbols
        cls._TICKER_DATA.loc[:, cls._TIMEFRAME] = timeframes
        cls._TICKER_DATA.loc[:, cls._START] = starts
        cls._TICKER_DATA.loc[:, cls._END] = ends

        cls._TICKER_DATA.sort_values([cls._PROVIDER, cls._SYMBOL,
                                      cls._TIMEFRAME, cls._START, cls._END], inplace=True)

    @classmethod
    def validate_metadata(cls, metadata: TickerMetadata) -> bool:
        """Validate metadata"""
        if metadata.provider == "":
            return False

        if not metadata.symbol:
            return False

        if not metadata.timeframe:
            return False

        if not metadata.start:
            return False

        if not metadata.end:
            return False

        if metadata.start > metadata.end:
            return False

        return True

    @classmethod
    def generate_metadata(cls, filename: str) -> TickerMetadata:
        """Generate metadata from file name"""
        filename = filename.split(".")[0]
        arr = filename.split(cls._SEPARATOR)

        if len(arr) != 5:
            return None

        metadata = TickerMetadata(
            provider  = arr[0],
            symbol    = Symbol[arr[1].replace("-", "_")],
            start     = dt.strptime(arr[2], cls._DATE_FORMAT),
            end       = dt.strptime(arr[3], cls._DATE_FORMAT),
            timeframe = Timeframe[arr[4].replace("-", "_")]
        )

        if not cls.validate_metadata(metadata):
            return None

        return metadata

    @classmethod
    def generate_filename(cls, metadata: TickerMetadata) -> str:
        """Generate filename from the metadata"""
        symbol = metadata.symbol.value.replace("_", "-")
        timeframe = metadata.timeframe.name.replace("_", "-")
        return (f"{metadata.provider}_{symbol}_"
                f"{metadata.start}_{metadata.end}_{timeframe}"
                f"{cls.FILE_EXT}")
