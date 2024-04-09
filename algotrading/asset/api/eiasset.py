"""Module of Asset Entity Interface"""
from dataclasses import dataclass, field
from abc import ABC
from typing import ClassVar
import os.path
import pandas as pd

from ...common.config import config
from ...common.asset import AssetType, AssetEnum

@dataclass
class EIAsset(ABC):
    """Asset Entity Interface"""
    _DATA_DIR: ClassVar[str] = config.common.data_directory
    _FILE_EXT: ClassVar[str] = config.common.file_extension
    _FILENAME: ClassVar[str] = config.common.asset_filename
    _DATA: ClassVar[pd.DataFrame] = None
    _CODE: ClassVar[str] = "CODE"
    _TYPE: ClassVar[str] = "TYPE"
    _NAME: ClassVar[str] = "NAME"

    code: AssetEnum
    type: AssetType = field(init=False)
    name: str = field(init=False)

    @staticmethod
    def get_assets(code: AssetEnum=None, asset_type: AssetType=None,
                   reload: bool=False) -> pd.DataFrame:
        """Return list of asset"""
        if EIAsset._DATA is None or reload:
            directory = EIAsset._DATA_DIR
            filename = EIAsset._FILENAME + EIAsset._FILE_EXT

            if os.path.exists(directory + filename):
                EIAsset._DATA = pd.read_csv(directory + filename)
            else:
                raise FileNotFoundError(f"{directory + filename}")

        df = EIAsset._DATA.copy()

        if code is not None:
            df = df.loc[(df[EIAsset._CODE] == code.value)]

        if asset_type is not None:
            df = df.loc[(df[EIAsset._TYPE] == asset_type.value)]

        return df

    def __post_init__(self):
        """Post initialization"""
        df = EIAsset.get_assets()
        try:
            asset_type = df.loc[(df[EIAsset._CODE] == self.code.value), EIAsset._TYPE].iloc[0]
            self.type = AssetType(asset_type)
            self.name = df.loc[(df[EIAsset._CODE] == self.code.value), EIAsset._NAME].iloc[0]
        except IndexError as error:
            print("An exception occurred:", error)
            print(f"AssetEnum: {self.code} doesn't exist")
