"""Module for Asset Code Enum"""
from enum import Enum

class AssetCode(Enum):
    """Parent of asset code enum"""
    @classmethod
    def _missing_(cls, value):
        if Currency.has_value(value):
            return Currency(value)
        elif Commodity.has_value(value):
            return Commodity(value)
        elif Index.has_value(value):
            return Index(value)
        elif Stock.has_value(value):
            return Stock(value)

        return super()._missing_(value)

class Currency(AssetCode):
    """List of currency"""
    @classmethod
    def has_value(cls, value):
        """return true if value exist"""
        return value in cls._value2member_map_

    AUD = "AUD"
    CAD = "CAD"
    CHF = "CHF"
    CNH = "CNH"
    CZK = "CZK"
    DKK = "DKK"
    EUR = "EUR"
    GBP = "GBP"
    HKD = "HKD"
    HUF = "HUF"
    JPY = "JPY"
    MXN = "MXN"
    NOK = "NOK"
    NZD = "NZD"
    PLN = "PLN"
    SEK = "SEK"
    SGD = "SGD"
    THB = "THB"
    TRY = "TRY"
    USD = "USD"
    ZAR = "ZAR"

class Commodity(AssetCode):
    """List of commodity"""
    @classmethod
    def has_value(cls, value):
        """return true if value exist"""
        return value in cls._value2member_map_

    BTC = "BTC"
    BCH = "BCH"
    BCO = "BCO"
    XCU = "XCU"
    CORN = "CORN"
    ETH = "ETH"
    XAU = "XAU"
    LTC = "LTC"
    MBTC = "MBTC"
    NATGAS = "NATGAS"
    XPD = "XPD"
    XPT = "XPT"
    XAG = "XAG"
    SOYBN = "SOYBN"
    SUGAR = "SUGAR"
    WTICO = "WTICO"
    WHEAT = "WHEAT"

class Index(AssetCode):
    """List of Index"""
    @classmethod
    def has_value(cls, value):
        """return true if value exist"""
        return value in cls._value2member_map_

    AU200 = "AU200"
    CH20 = "CH20"
    CHINAH = "CHINAH"
    CN50 = "CN50"
    DE10YB = "DE10YB"
    DE30 = "DE30"
    ESPIX = "ESPIX"
    EU50 = "EU50"
    FR40 = "FR40"
    HK33 = "HK33"
    JP225 = "JP225"
    JP225Y = "JP225Y"
    NAS100 = "NAS100"
    NL25 = "NL25"
    SG30 = "SG30"
    SPX500 = "SPX500"
    UK100 = "UK100"
    UK10YB = "UK10YB"
    US2000 = "US2000"
    US30 = "US30"
    USB02Y = "USB02Y"
    USB05Y = "USB05Y"
    USB10Y = "USB10Y"
    USB30Y = "USB30Y"

class Stock(AssetCode):
    """List of Stock"""
    @classmethod
    def has_value(cls, value):
        """return true if value exist"""
        return value in cls._value2member_map_

    AAPL = "AAPL"
    GOOG = "GOOG"
