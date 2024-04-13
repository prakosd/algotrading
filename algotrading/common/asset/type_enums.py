"""Module for Asset Type Enum"""
from enum import Enum

class AssetType(Enum):
    """List of asset type"""
    CURRENCY  = "CURRENCY"
    COMMODITY = "COMMODITY"
    INDEX     = "INDEX"
    BOND      = "BOND"
    STOCK     = "STOCK"

class AssetPairType(Enum):
    """List of asset pair type"""
    FOREX       = "FOREX"
    COMMODITY   = "COMMODITY"
    STOCK       = "STOCK"
