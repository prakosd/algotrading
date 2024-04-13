"""Module of Asset Pair Entity Interface"""
from dataclasses import dataclass, field
from abc import ABC
from typing import ClassVar
import os.path
import pandas as pd

from ...common.config import config
from .eiasset import EIAsset
from ...common.asset import AssetPairCode, AssetPairType, AssetCode

@dataclass
class EIAssetPair(ABC):
    """Asset Pair Entity Interface"""
    _DATA_DIR: ClassVar[str] = config.common.data_directory
    _FILE_EXT: ClassVar[str] = config.common.file_extension
    _FILENAME: ClassVar[str] = config.common.asset_pair_filename
    _DATA: ClassVar[pd.DataFrame] = None
    _CODE: ClassVar[str] = "CODE"
    _BASE: ClassVar[str] = "BASE"
    _QUOTE: ClassVar[str] = "QUOTE"
    _TYPE: ClassVar[str] = "TYPE"

    code: AssetPairCode
    base: EIAsset = field(init=False)
    quote: EIAsset = field(init=False)
    type: AssetPairType = field(init=False)
    name: str = field(init=False)

    @staticmethod
    def get_asset_pairs(code: AssetPairCode=None, base: AssetCode=None,
                        quote: AssetCode=None, pair_type: AssetPairType=None,
                        reload: bool=False) -> pd.DataFrame:
        """Return list of asset pair"""
        if EIAssetPair._DATA is None or reload:
            directory = EIAssetPair._DATA_DIR
            filename = EIAssetPair._FILENAME + EIAssetPair._FILE_EXT

            if os.path.exists(directory + filename):
                EIAssetPair._DATA = pd.read_csv(directory + filename)
            else:
                raise FileNotFoundError(f"{directory + filename}")

        df = EIAssetPair._DATA.copy()

        if code is not None:
            df = df.loc[(df[EIAssetPair._CODE] == code.value)]

        if base is not None:
            df = df.loc[(df[EIAssetPair._BASE] == base.value)]

        if quote is not None:
            df = df.loc[(df[EIAssetPair._QUOTE] == quote.value)]

        if pair_type is not None:
            df = df.loc[(df[EIAssetPair._TYPE] == pair_type.value)]

        return df

    def __post_init__(self):
        """Post initialization"""
        df = EIAssetPair.get_asset_pairs()
        try:
            (base, quote, pair_type) = df.loc[(df[EIAssetPair._CODE] == self.code.value),
                                              [EIAssetPair._BASE, EIAssetPair._QUOTE,
                                              EIAssetPair._TYPE]].iloc[0]

            (self.base, self.quote, self.type) = (EIAsset(AssetCode(base)),
                                                  EIAsset(AssetCode(quote)),
                                                  AssetPairType(pair_type))
            self.name = self.base.name + ' - ' + self.quote.name

        except IndexError as error:
            print("An exception occurred:", error)
            print(f"Asset Pair: {self.code} doesn't exist")
