"""Module of File Manager Class"""
from dataclasses import dataclass
from typing import ClassVar
import os
import pandas as pd

from ..common.config import config

@dataclass
class FileManager():
    """File Manager Class"""
    _DATA: ClassVar[pd.DataFrame] = None
    _NAME: ClassVar[str] = "NAME"
    _EXT: ClassVar[str] = "EXT"

    DATA_DIR: ClassVar[str] = config.file_manager.data_directory
    FILE_EXT: ClassVar[str] = config.file_manager.file_extension

    @classmethod
    def find_files(cls, name: str=None,
                  ext: str=None, reload: bool=False) -> pd.DataFrame:
        """Return list of file"""
        if cls._DATA is None or reload:
            data = []
            if not os.path.exists(cls.DATA_DIR):
                os.mkdir(cls.DATA_DIR)

            for file in sorted(os.listdir(cls.DATA_DIR)):
                basename = os.path.basename(file)
                data.append((basename, os.path.splitext(basename)[1]))

            cls._DATA = pd.DataFrame(data, columns=[cls._NAME, cls._EXT])

        df = cls._DATA.copy()

        if name is not None:
            df = df[df[cls._NAME].str.contains(name, case=False)]

        if ext is not None:
            df = df[df[cls._EXT].str.contains(ext, case=False)]

        return df

    @classmethod
    def exist(cls, name: str, reload: bool=False) -> bool:
        """Return true if file exist"""
        df = cls.find_files(reload=reload)
        df = df[df[cls._NAME] == name]

        if df is None or df.empty:
            return False

        return True

    @classmethod
    def read_csv(cls, name: str, date_index_col: str=None) -> pd.DataFrame:
        """Return data from csv file as DataFrame"""
        if not cls.exist(name, reload=True):
            return None

        if date_index_col is None:
            return pd.read_csv(cls.DATA_DIR + name)

        return pd.read_csv(cls.DATA_DIR + name,
                           parse_dates=[date_index_col],
                           index_col=date_index_col)

    @classmethod
    def write_csv(cls, name: str, data: pd.DataFrame, index: bool=True) -> bool:
        "Return true if writing from DataFrame to csv file successful"
        if cls.exist(name, reload=True):
            raise FileExistsError

        data.to_csv(cls.DATA_DIR + name, index=index)
        if cls.exist(name, reload=True):
            return True

        return False

    @classmethod
    def remove(cls, name: str) -> bool:
        """Return true if deletion successful"""
        if not cls.exist(name, reload=True):
            return False

        os.remove(cls.DATA_DIR + name)
        if not cls.exist(name, reload=True):
            return True

        return False
