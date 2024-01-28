"""Module to set config data definition"""
from dataclasses import dataclass

@dataclass(frozen=True)
class CommonConfigData:
    """Common config data definition"""
    data_directory: str
    file_extension: str

@dataclass(frozen=True)
class ProviderConfigData:
    """Provider config data definition"""
    data_directory: str
    file_extension: str
    config_path_oanda: str

@dataclass(frozen=True)
class AccountConfigData:
    """Account config data definition"""
    base_currency: str
    leverage: int
    unit_size: int
    margin_call_level: float
    stop_out_level: float

@dataclass(frozen=True)
class DealConfigData:
    """Deal config data definition"""
    is_mock_deal: bool
    slippage_point_min: int
    slippage_point_max: int
    volume_percent_min: int
    volume_percent_max: int

@dataclass(frozen=True)
class ConfigData:
    """Provider config data definition"""
    common: CommonConfigData
    provider: ProviderConfigData
    account: AccountConfigData
    deal: DealConfigData
