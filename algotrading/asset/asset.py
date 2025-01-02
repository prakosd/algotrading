"""Module of Asset Class"""
from dataclasses import dataclass, field
from typing import ClassVar
import pandas as pd

from ..common.config import config
from ..common.asset import AssetType, AssetCode
from ..common.manager import CommonDataManager

@dataclass
class Asset():
    """Asset Class"""
    _FILE_EXT: ClassVar[str] = config.common.file_extension
    _FILENAME: ClassVar[str] = config.common.asset_filename
    _DATA: ClassVar[pd.DataFrame] = None
    _CODE: ClassVar[str] = "CODE"
    _TYPE: ClassVar[str] = "TYPE"
    _NAME: ClassVar[str] = "NAME"

    code: AssetCode
    type: AssetType = field(init=False)
    name: str = field(init=False)

    @classmethod
    def get_assets(cls, code: AssetCode=None, asset_type: AssetType=None,
                   reload: bool=False) -> pd.DataFrame:
        """Return list of asset"""
        if cls._DATA is None or reload:
            cls._DATA = CommonDataManager.read(cls._FILENAME + cls._FILE_EXT)

            if cls._DATA is None:
                raise FileNotFoundError(cls._FILENAME + cls._FILE_EXT)

        df = cls._DATA.copy()

        if code is not None:
            df = df.loc[(df[cls._CODE] == code.value)]

        if asset_type is not None:
            df = df.loc[(df[cls._TYPE] == asset_type.value)]

        return df

    def __post_init__(self):
        """Post initialization"""
        df = self.get_assets()
        try:
            asset_type = df.loc[(df[self._CODE] == self.code.value), self._TYPE].iloc[0]
            self.type = AssetType(asset_type)
            self.name = df.loc[(df[self._CODE] == self.code.value), self._NAME].iloc[0]
        except IndexError as error:
            print("An exception occurred:", error)
            print(f"AssetEnum: {self.code} doesn't exist")
