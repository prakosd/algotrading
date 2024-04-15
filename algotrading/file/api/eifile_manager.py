"""Module of File Manager Entity Interface"""
from dataclasses import dataclass
from typing import ClassVar
from abc import ABC
import os
import pandas as pd

from ...common.config import config

@dataclass
class EIFileManager(ABC):
    """File Manager Entity Interface"""
    _DATA_DIR: ClassVar[str] = config.file_manager.data_directory
    _DATA: ClassVar[pd.DataFrame] = None
    _NAME: ClassVar[str] = "NAME"
    _EXT: ClassVar[str] = "EXT"

    @staticmethod
    def find_files(name: str=None,
                  ext: str=None, reload: bool=False) -> pd.DataFrame:
        """Return list of file"""
        if EIFileManager._DATA is None or reload:
            data = []
            for file in sorted(os.listdir(EIFileManager._DATA_DIR)):
                basename = os.path.basename(file)
                data.append((basename, os.path.splitext(basename)[1][1:]))

            EIFileManager._DATA = pd.DataFrame(data,
                                               columns=[EIFileManager._NAME,
                                                        EIFileManager._EXT])

        df = EIFileManager._DATA.copy()

        if name is not None:
            df = df[df[EIFileManager._NAME].str.contains(name, case=False)]

        if ext is not None:
            df = df[df[EIFileManager._EXT].str.contains(ext, case=False)]

        return df

    @staticmethod
    def exist(name: str, reload: bool=False) -> bool:
        """Return true if file exist"""
        df = EIFileManager.find_files(reload=reload)
        df = df[df[EIFileManager._NAME] == name]

        if len(df) == 0:
            return False

        return True

    @staticmethod
    def read_csv(name: str) -> pd.DataFrame:
        """Return data from csv file as DataFrame"""
        if not EIFileManager.exist(name, reload=True):
            return None

        return pd.read_csv(EIFileManager._DATA_DIR + name)

    @staticmethod
    def write_csv(name: str, data: pd.DataFrame) -> bool:
        "Return true if writing from DataFrame to csv file successful"
        if EIFileManager.exist(name, reload=True):
            raise FileExistsError

        data.to_csv(EIFileManager._DATA_DIR + name, index=False)
        if EIFileManager.exist(name, reload=True):
            return True

        return False

    @staticmethod
    def remove(name: str) -> bool:
        """Return true if deletion successful"""
        if not EIFileManager.exist(name, reload=True):
            return False

        os.remove(EIFileManager._DATA_DIR + name)
        if not EIFileManager.exist(name, reload=True):
            return True

        return False
