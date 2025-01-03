"""Asset Class Test Suite"""
from typing import ClassVar
from unittest.mock import patch, Mock
import numpy as np
import pandas as pd
import pytest

from algotrading.asset.asset import Asset
from algotrading.common.asset import AssetCode, AssetType
from algotrading.common.asset import Currency, Commodity, Index, Stock

class TestAsset():
    """Test suite for Asset class"""
    FILENAME_EXT: ClassVar[str] = "ASSET.csv"
    MOCK_ASSETS_EMPTY: ClassVar[pd.DataFrame] = pd.DataFrame({
            'CODE': [],
            'TYPE': [],
            'NAME': []
        })
    MOCK_ASSETS: ClassVar[pd.DataFrame] = pd.DataFrame({
            'CODE': ['BTC', 'XAU', 'EUR', 'USD', 'AU200', 'UK100'],
            'TYPE': ['COMMODITY', 'COMMODITY', 'CURRENCY', 'CURRENCY', 'INDEX', 'INDEX'],
            'NAME': ['Bitcoin', 'Gold', 'Euro', 'US Dollar', 'Australia 200', 'UK 100']
        })

    MOCK_COMMODITY_BTC: ClassVar[pd.DataFrame] = pd.DataFrame({
            'CODE': ['BTC'],
            'TYPE': ['COMMODITY'],
            'NAME': ['Bitcoin']
        })

    MOCK_COMMODITY_GOLD: ClassVar[pd.DataFrame] = pd.DataFrame({
            'CODE': ['XAU'],
            'TYPE': ['COMMODITY'],
            'NAME': ['Gold']
        })

    MOCK_CURRENCY_USD: ClassVar[pd.DataFrame] = pd.DataFrame({
            'CODE': ['USD'],
            'TYPE': ['CURRENCY'],
            'NAME': ['US Dollar']
        })

    MOCK_INDEX_UK100: ClassVar[pd.DataFrame] = pd.DataFrame({
            'CODE': ['UK100'],
            'TYPE': ['INDEX'],
            'NAME': ['UK 100']
        })

    MOCK_COMMODITY: ClassVar[pd.DataFrame] = pd.DataFrame({
            'CODE': ['BTC', 'XAU'],
            'TYPE': ['COMMODITY', 'COMMODITY'],
            'NAME': ['Bitcoin', 'Gold']
        })

    MOCK_CURRENCY: ClassVar[pd.DataFrame] = pd.DataFrame({
            'CODE': ['EUR', 'USD'],
            'TYPE': ['CURRENCY', 'CURRENCY'],
            'NAME': ['Euro', 'US Dollar']
        })

    MOCK_INDEX: ClassVar[pd.DataFrame] = pd.DataFrame({
            'CODE': ['AU200', 'UK100'],
            'TYPE': ['INDEX', 'INDEX'],
            'NAME': ['Australia 200', 'UK 100']
        })

    @patch('algotrading.common.CommonDataManager.read')
    def test_get_assets_file_not_found(self, mock_read: Mock):
        """Test the get assets method when asset file is not found"""
        mock_read.return_value = None

        with pytest.raises(FileNotFoundError):
            Asset.get_assets()

    @patch('algotrading.common.CommonDataManager.read')
    def test_get_assets_first_time(self, mock_read: Mock):
        """Test the get assets method is called for the first time"""
        mock_read.return_value = self.MOCK_ASSETS

        result = Asset.get_assets()
        pd.testing.assert_frame_equal(result, self.MOCK_ASSETS)
        mock_read.assert_called_once()

    @patch('algotrading.common.CommonDataManager.read')
    def test_get_assets_second_time(self, mock_read: Mock):
        """Test the get assets method is called for the second time"""
        mock_read.return_value = self.MOCK_ASSETS

        result = Asset.get_assets()
        pd.testing.assert_frame_equal(result, self.MOCK_ASSETS)
        mock_read.assert_not_called()

    @patch('algotrading.common.CommonDataManager.read')
    def test_get_assets_reload_true(self, mock_read: Mock):
        """Test the get assets method when reload is true"""
        mock_read.return_value = self.MOCK_ASSETS

        result = Asset.get_assets(reload=True)
        pd.testing.assert_frame_equal(result, self.MOCK_ASSETS)
        mock_read.assert_called_once_with(self.FILENAME_EXT)

    @pytest.mark.parametrize("code, asset_type, expected_output",
                             [(Currency.USD, None, MOCK_CURRENCY_USD),
                              (Commodity.BTC, None, MOCK_COMMODITY_BTC),
                              (Index.UK100, None, MOCK_INDEX_UK100),
                              (None, AssetType.COMMODITY, MOCK_COMMODITY),
                              (None, AssetType.INDEX, MOCK_INDEX),
                              (None, AssetType.CURRENCY, MOCK_CURRENCY),
                              (Commodity.XAU, AssetType.COMMODITY, MOCK_COMMODITY_GOLD),
                              (None, AssetType.STOCK, MOCK_ASSETS_EMPTY),
                              (Index.AU200, AssetType.COMMODITY, MOCK_ASSETS_EMPTY)])
    @patch('algotrading.common.CommonDataManager.read')
    def test_get_assets_variation(self, mock_read: Mock, code: AssetCode,
                                  asset_type: AssetType, expected_output: pd.DataFrame):
        """Test the get_assets method with various asset codes and asset types"""
        mock_read.return_value = self.MOCK_ASSETS

        result = Asset.get_assets(code=code, asset_type=asset_type)
        assert np.array_equal(result, expected_output)

    @pytest.mark.parametrize("code, expected_output",
                             [(Currency.EUR, {
                                 "code": Currency.EUR,
                                 "type": AssetType.CURRENCY,
                                 "name": "Euro"
                                 }),
                              (Commodity.XAU, {
                                  "code": Commodity.XAU,
                                  "type": AssetType.COMMODITY,
                                  "name": "Gold"
                                  }),
                              (Index.AU200, {
                                  "code": Index.AU200,
                                  "type": AssetType.INDEX,
                                  "name": "Australia 200"
                                  }),
                              (Stock.AAPL, {
                                  "code": None,
                                  "type": None,
                                  "name": None
                                  })])
    @patch('algotrading.common.CommonDataManager.read')
    def test_post_init_variation(self, mock_read: Mock, code: AssetCode, expected_output: Asset):
        """Test the initialization of the Asset class with different sets of arguments"""
        mock_read.return_value = self.MOCK_ASSETS

        result = Asset(code)
        assert result.code == expected_output['code']
        assert result.type == expected_output['type']
        assert result.name == expected_output['name']
