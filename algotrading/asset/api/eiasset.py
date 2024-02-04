"""Module of Symbol Entity Interface"""
from dataclasses import dataclass, field
from abc import ABC
from typing import ClassVar
import os.path
import pandas as pd

from ...common.config import config
from ...common.asset import AssetType, AssetEnum

@dataclass
class EIAsset(ABC):
    """Symbol Entity Interface"""
    _DATA_DIR: ClassVar[str] = config.common.data_directory
    _FILE_EXT: ClassVar[str] = config.common.file_extension
    _FILENAME: ClassVar[str] = config.common.asset_filename
    _DATA: ClassVar[pd.DataFrame] = None

    code: AssetEnum
    type: AssetType = field(init=False)
    name: str = field(init=False)

    @staticmethod
    def get_assets(reload: bool=False) -> pd.DataFrame:
        """Return list of asset"""
        if EIAsset._DATA is None or reload:
            directory = EIAsset._DATA_DIR
            filename = EIAsset._FILENAME + EIAsset._FILE_EXT

            if os.path.exists(directory + filename):
                EIAsset._DATA = pd.read_csv(directory + filename)
            else:
                raise FileNotFoundError(f"{directory + filename}")

        return EIAsset._DATA

    def __post_init__(self):
        """Post initialization"""
        df = EIAsset.get_assets()
        try:
            asset_code = df.loc[(df['CODE'] == self.code.value), 'TYPE'].iloc[0]
            self.type = AssetType(asset_code)
            self.name = df.loc[(df['CODE'] == self.code.value), 'NAME'].iloc[0]
        except IndexError as error:
            print("An exception occurred:", error)
            print(f"AssetEnum: {self.code} doesn't exist")
