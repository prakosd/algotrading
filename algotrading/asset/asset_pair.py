"""Module of Asset Pair Class"""
from dataclasses import dataclass, field
from typing import ClassVar
import os.path
import pandas as pd

from ..common.config import config
from .asset import Asset
from ..common.asset import AssetPairCode, AssetPairType, AssetCode

@dataclass
class AssetPair():
    """Asset Pair Class"""
    _DATA_DIR: ClassVar[str] = config.common.data_directory
    _FILE_EXT: ClassVar[str] = config.common.file_extension
    _FILENAME: ClassVar[str] = config.common.asset_pair_filename
    _DATA: ClassVar[pd.DataFrame] = None
    _CODE: ClassVar[str] = "CODE"
    _BASE: ClassVar[str] = "BASE"
    _QUOTE: ClassVar[str] = "QUOTE"
    _TYPE: ClassVar[str] = "TYPE"

    code: AssetPairCode
    base: Asset = field(init=False)
    quote: Asset = field(init=False)
    type: AssetPairType = field(init=False)
    name: str = field(init=False)

    @classmethod
    def get_asset_pairs(cls, code: AssetPairCode=None, base: AssetCode=None,
                        quote: AssetCode=None, pair_type: AssetPairType=None,
                        reload: bool=False) -> pd.DataFrame:
        """Return list of asset pair"""
        if cls._DATA is None or reload:
            directory = cls._DATA_DIR
            filename = cls._FILENAME + cls._FILE_EXT

            if os.path.exists(directory + filename):
                cls._DATA = pd.read_csv(directory + filename)
            else:
                raise FileNotFoundError(f"{directory + filename}")

        df = cls._DATA.copy()

        if code is not None:
            df = df.loc[(df[cls._CODE] == code.value)]

        if base is not None:
            df = df.loc[(df[cls._BASE] == base.value)]

        if quote is not None:
            df = df.loc[(df[cls._QUOTE] == quote.value)]

        if pair_type is not None:
            df = df.loc[(df[cls._TYPE] == pair_type.value)]

        return df

    def __post_init__(self):
        """Post initialization"""
        df = self.get_asset_pairs()
        try:
            (base, quote, pair_type) = df.loc[(df[self._CODE] == self.code.value),
                                              [self._BASE, self._QUOTE,
                                              self._TYPE]].iloc[0]

            (self.base, self.quote, self.type) = (Asset(AssetCode.by_value(base)),
                                                  Asset(AssetCode.by_value(quote)),
                                                  AssetPairType(pair_type))
            self.name = self.base.name + ' - ' + self.quote.name

        except IndexError as error:
            print("An exception occurred:", error)
            print(f"Asset Pair: {self.code} doesn't exist")
