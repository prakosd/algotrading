"""Module of Common Data Manager Class"""
from dataclasses import dataclass
from typing import ClassVar

from ..data.manager import DataManager
from ..common.config import config

@dataclass
class CommonDataManager(DataManager):
    """Common Data Manager Class"""
    DATA_DIR: ClassVar[str] = config.common.data_directory
    FILE_EXT: ClassVar[str] = config.common.file_extension
