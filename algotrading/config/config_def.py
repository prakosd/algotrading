"""Module to set config data definition"""
from dataclasses import dataclass

@dataclass
class ProviderConfigData:
    """Provider config data definition"""
    data_directory: str
    file_extension: str
    config_path_oanda: str

@dataclass
class AccountConfigData:
    """Account config data definition"""
    base_currency: str
    leverage: float
    unit_size: int
    margin_call_level: float
    stop_out_level: float

@dataclass
class DealConfigData:
    """Deal config data definition"""
    is_mock_deal: bool
    slippage_point_min: int
    slippage_point_max: int
    volume_percent_min: int
    volume_percent_max: int

@dataclass
class ConfigData:
    """Provider config data definition"""
    provider: ProviderConfigData
    account: AccountConfigData
    deal: DealConfigData
