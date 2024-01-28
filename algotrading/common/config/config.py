"""Module to load config"""
from dataclasses import dataclass
from typing import ClassVar
from os import path
import configparser
import ast

from .config_def import ConfigData
from .config_def import CommonConfigData, ProviderConfigData
from .config_def import AccountConfigData, DealConfigData

@dataclass
class Config:
    """Class to load config"""
    _instance: ClassVar[ConfigData] = None
    _CONF_FILE: ClassVar[str] = path.relpath(
        path.join(
            path.dirname(
                path.relpath(__file__)), '../../config/global.cfg'))

    @staticmethod
    def get_instance(reload: bool=False) -> ConfigData:
        """Retrieve config instance as singleton"""
        if Config._instance is not None and not reload:
            return Config._instance

        parser = configparser.ConfigParser()
        parser.read(Config._CONF_FILE)

        common = CommonConfigData(
            data_directory    = parser['common']['data_directory'],
            file_extension    = parser['common']['file_extension'],
        )

        provider = ProviderConfigData(
            data_directory    = parser['resources']['data_directory'],
            file_extension    = parser['resources']['file_extension'],
            config_path_oanda = parser['oanda']['config_path']
        )

        account = AccountConfigData(
            base_currency     = parser['account']['base_currency'],
            leverage          = int(parser['account']['leverage']),
            unit_size         = int(parser['account']['unit_size']),
            margin_call_level = float(parser['account']['margin_call_level']),
            stop_out_level    = float(parser['account']['stop_out_level'])
        )

        deal = DealConfigData(
            is_mock_deal       = ast.literal_eval(parser['deal']['is_mock_deal']),
            slippage_point_min = int(parser['deal']['slippage_point_min']),
            slippage_point_max = int(parser['deal']['slippage_point_max']),
            volume_percent_min = int(parser['deal']['volume_percent_min']),
            volume_percent_max = int(parser['deal']['volume_percent_max'])
        )

        Config._instance = ConfigData(common, provider, account, deal)
        return Config._instance

config: ConfigData = Config.get_instance()
