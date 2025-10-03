"""Comprehensive unit tests for Deal class."""
import time
import gc
from datetime import datetime as dt
from typing import Any, Dict, List
import pytest

from algotrading.backtesting.components.deal.deal import Deal
from algotrading.common.trade import DealType
from algotrading.common.asset import AssetPairCode as Symbol


class TestDeal:
    """Test suite for Deal class covering all functionality from deal_class_test_suite.ipynb."""

    def setup_method(self):
        """Reset Deal ID counter before each test method."""
        Deal.reset_id()

    def test_basic_deal_creation_buy(self):
        """Test basic BUY deal creation with valid parameters."""
        test_datetime = dt(2024, 6, 30, 14, 30, 0)
        
        deal = Deal(
            symbol=Symbol.EUR_USD,
            datetime=test_datetime,
            type=DealType.BUY,
            volume=0.01,
            price=1.0899
        )
        
        assert deal.id == 0
        assert deal.symbol == Symbol.EUR_USD
        assert deal.datetime == test_datetime
        assert deal.type == DealType.BUY
        assert deal.volume == 0.01
        assert deal.price == 1.0899

    def test_basic_deal_creation_sell(self):
        """Test basic SELL deal creation with valid parameters."""
        test_datetime = dt(2024, 6, 30, 14, 30, 0)
        
        deal = Deal(
            symbol=Symbol.GBP_USD,
            datetime=test_datetime,
            type=DealType.SELL,
            volume=0.05,
            price=1.2755
        )
        
        assert deal.id == 0
        assert deal.symbol == Symbol.GBP_USD
        assert deal.datetime == test_datetime
        assert deal.type == DealType.SELL
        assert deal.volume == 0.05
        assert deal.price == 1.2755

    def test_data_types(self):
        """Verify that all deal attributes have correct data types."""
        deal = Deal(
            symbol=Symbol.EUR_USD,
            datetime=dt.now(),
            type=DealType.BUY,
            volume=0.01,
            price=1.0899
        )
        
        assert isinstance(deal.id, int)
        assert isinstance(deal.symbol, Symbol)
        assert isinstance(deal.datetime, dt)
        assert isinstance(deal.type, DealType)
        assert isinstance(deal.volume, float)
        assert isinstance(deal.price, float)

    def test_id_auto_generation(self):
        """Test that each new Deal instance gets a unique, incrementing ID."""
        deals = []
        expected_ids = list(range(10))
        
        for i in range(10):
            deal = Deal(
                symbol=Symbol.EUR_USD,
                datetime=dt.now(),
                type=DealType.BUY if i % 2 == 0 else DealType.SELL,
                volume=0.01 * (i + 1),
                price=1.0800 + (i * 0.001)
            )
            deals.append(deal)
        
        actual_ids = [deal.id for deal in deals]
        assert actual_ids == expected_ids
        assert len(set(actual_ids)) == len(actual_ids)  # All IDs are unique
        
        # Verify sequential increments
        for i in range(1, len(actual_ids)):
            assert actual_ids[i] == actual_ids[i-1] + 1

    def test_generate_id_method(self):
        """Test the generate_id() class method directly."""
        # Create some deals first
        for i in range(5):
            Deal(Symbol.EUR_USD, dt.now(), DealType.BUY, 0.01, 1.08)
        
        next_id = Deal.generate_id()
        assert next_id == 5
        
        # Create another deal and verify it gets the incremented ID
        new_deal = Deal(Symbol.USD_JPY, dt.now(), DealType.BUY, 0.01, 150.50)
        assert new_deal.id == 6

    def test_id_reset_functionality(self):
        """Test the reset_id() class method."""
        # Create some deals to increment the counter
        for i in range(5):
            Deal(Symbol.EUR_USD, dt.now(), DealType.BUY, 0.01, 1.08)
        
        last_deal = Deal(Symbol.EUR_USD, dt.now(), DealType.BUY, 0.01, 1.08)
        assert last_deal.id == 5
        
        # Reset the ID counter
        Deal.reset_id()
        
        # Create new deals after reset
        reset_deals = []
        for i in range(3):
            deal = Deal(Symbol.GBP_USD, dt.now(), DealType.SELL, 0.02, 1.27)
            reset_deals.append(deal)
        
        expected_reset_ids = [0, 1, 2]
        actual_reset_ids = [deal.id for deal in reset_deals]
        assert actual_reset_ids == expected_reset_ids

    def test_multiple_resets(self):
        """Test multiple consecutive resets."""
        for reset_num in range(3):
            Deal.reset_id()
            first_deal_after_reset = Deal(Symbol.USD_CAD, dt.now(), DealType.BUY, 0.01, 1.35)
            assert first_deal_after_reset.id == 0

    def test_as_dict_serialization(self):
        """Test the as_dict() method for proper serialization."""
        test_dt = dt(2024, 10, 2, 15, 30, 45)
        
        deal = Deal(
            symbol=Symbol.EUR_USD,
            datetime=test_dt,
            type=DealType.BUY,
            volume=0.1,
            price=1.0850
        )
        
        deal_dict = deal.as_dict()
        
        # Verify dictionary structure
        expected_keys = {'id', 'symbol', 'datetime', 'type', 'volume', 'price'}
        assert set(deal_dict.keys()) == expected_keys
        
        # Verify each field
        assert deal_dict['id'] == 0
        assert deal_dict['symbol'] == "EUR_USD"
        assert deal_dict['datetime'] == test_dt
        assert deal_dict['type'] == "BUY"
        assert deal_dict['volume'] == 0.1
        assert deal_dict['price'] == 1.0850

    def test_as_dict_data_types(self):
        """Verify data types in serialized dictionary."""
        deal = Deal(Symbol.EUR_USD, dt.now(), DealType.BUY, 0.01, 1.08)
        deal_dict = deal.as_dict()
        
        assert isinstance(deal_dict['id'], int)
        assert isinstance(deal_dict['symbol'], str)
        assert isinstance(deal_dict['datetime'], dt)
        assert isinstance(deal_dict['type'], str)
        assert isinstance(deal_dict['volume'], float)
        assert isinstance(deal_dict['price'], float)

    def test_different_deal_types(self):
        """Test Deal creation with all available DealType values."""
        deal_types = list(DealType)
        
        for i, deal_type in enumerate(deal_types):
            deal = Deal(
                symbol=Symbol.EUR_USD,
                datetime=dt.now(),
                type=deal_type,
                volume=0.01,
                price=1.08
            )
            assert deal.type == deal_type
            assert deal.id == i

    def test_different_symbols(self):
        """Test Deal creation with various Symbol types."""
        test_symbols = [
            Symbol.EUR_USD,    # Major forex pair
            Symbol.GBP_JPY,    # Cross pair
            Symbol.AUD_CAD,    # Another cross pair
            Symbol.USD_CHF,    # Another major
            Symbol.XAG_USD,    # Precious metal
            Symbol.BTC_USD,    # Cryptocurrency
            Symbol.WTICO_USD,  # Commodity
            Symbol.NATGAS_USD  # Another commodity
        ]
        
        for i, symbol in enumerate(test_symbols):
            deal = Deal(
                symbol=symbol,
                datetime=dt.now(),
                type=DealType.BUY,
                volume=0.01,
                price=100.0
            )
            assert deal.symbol == symbol
            assert deal.id == i

    def test_edge_cases_volume_and_price(self):
        """Test edge cases for volume and price values."""
        edge_cases = [
            {"volume": 0.001, "price": 0.01, "desc": "Very small values"},
            {"volume": 1000.0, "price": 50000.0, "desc": "Large values"},
            {"volume": 0.123456789, "price": 1.987654321, "desc": "High precision values"},
            {"volume": 1.0, "price": 1.0, "desc": "Unit values"},
        ]
        
        for i, case in enumerate(edge_cases):
            deal = Deal(
                symbol=Symbol.EUR_USD,
                datetime=dt.now(),
                type=DealType.BUY,
                volume=case["volume"],
                price=case["price"]
            )
            assert deal.volume == case["volume"]
            assert deal.price == case["price"]
            assert deal.id == i

    def test_different_datetime_values(self):
        """Test Deal creation with various datetime values."""
        datetime_cases = [
            dt(2020, 1, 1, 0, 0, 0),        # New Year 2020
            dt(2024, 12, 31, 23, 59, 59),   # End of 2024
            dt(2023, 6, 15, 12, 30, 45),    # Mid-year, mid-day
            dt.now(),                       # Current time
            dt(1970, 1, 1, 0, 0, 1),        # Near Unix epoch
        ]
        
        for i, test_dt in enumerate(datetime_cases):
            deal = Deal(
                symbol=Symbol.EUR_USD,
                datetime=test_dt,
                type=DealType.BUY,
                volume=0.01,
                price=1.08
            )
            assert deal.datetime == test_dt
            assert deal.id == i

    def test_multiple_deal_instances(self):
        """Test creating multiple Deal instances with diverse parameters."""
        test_scenarios = [
            {"symbol": Symbol.EUR_USD, "type": DealType.BUY, "volume": 0.1, "price": 1.0850},
            {"symbol": Symbol.GBP_USD, "type": DealType.SELL, "volume": 0.05, "price": 1.2750},
            {"symbol": Symbol.USD_JPY, "type": DealType.BUY, "volume": 0.2, "price": 150.25},
            {"symbol": Symbol.AUD_USD, "type": DealType.SELL, "volume": 0.15, "price": 0.6750},
            {"symbol": Symbol.USD_CHF, "type": DealType.BUY, "volume": 0.08, "price": 0.9050},
            {"symbol": Symbol.EUR_GBP, "type": DealType.SELL, "volume": 0.12, "price": 0.8650},
            {"symbol": Symbol.CAD_JPY, "type": DealType.BUY, "volume": 0.06, "price": 110.45},
            {"symbol": Symbol.XAG_USD, "type": DealType.BUY, "volume": 1.0, "price": 32.50},
            {"symbol": Symbol.BTC_USD, "type": DealType.SELL, "volume": 0.001, "price": 65000.0},
            {"symbol": Symbol.WTICO_USD, "type": DealType.BUY, "volume": 0.5, "price": 85.75},
        ]
        
        portfolio_deals = []
        base_datetime = dt(2024, 10, 2, 9, 0, 0)
        
        for i, scenario in enumerate(test_scenarios):
            deal_datetime = base_datetime.replace(minute=base_datetime.minute + i)
            
            deal = Deal(
                symbol=scenario["symbol"],
                datetime=deal_datetime,
                type=scenario["type"],
                volume=scenario["volume"],
                price=scenario["price"]
            )
            portfolio_deals.append(deal)
        
        # Verify all IDs are unique and sequential
        deal_ids = [deal.id for deal in portfolio_deals]
        unique_ids = set(deal_ids)
        assert len(unique_ids) == len(portfolio_deals)
        assert deal_ids == list(range(len(portfolio_deals)))
        
        # Verify data integrity for each deal
        for i, (deal, expected) in enumerate(zip(portfolio_deals, test_scenarios)):
            assert deal.symbol == expected["symbol"]
            assert deal.type == expected["type"]
            assert deal.volume == expected["volume"]
            assert deal.price == expected["price"]
            assert deal.id == i

    def test_deal_instance_independence(self):
        """Test that Deal instances are independent of each other."""
        deal1 = Deal(Symbol.EUR_USD, dt.now(), DealType.BUY, 0.1, 1.08)
        deal2 = Deal(Symbol.GBP_USD, dt.now(), DealType.SELL, 0.05, 1.27)
        
        original_price1 = deal1.price
        original_price2 = deal2.price
        
        # Modify one deal
        deal1.price = 999.99
        
        # Ensure the other deal is unchanged
        assert deal2.price == original_price2
        
        # Restore original price
        deal1.price = original_price1
        assert deal1.price == original_price1

    def test_attribute_mutability(self):
        """Test that Deal attributes can be modified after creation."""
        deal = Deal(
            symbol=Symbol.EUR_USD,
            datetime=dt(2024, 10, 2, 14, 30, 45),
            type=DealType.BUY,
            volume=0.125,
            price=1.08567
        )
        
        # Test modifying each attribute
        deal.symbol = Symbol.GBP_USD
        assert deal.symbol == Symbol.GBP_USD
        
        new_datetime = dt(2025, 1, 1, 12, 0, 0)
        deal.datetime = new_datetime
        assert deal.datetime == new_datetime
        
        deal.type = DealType.SELL
        assert deal.type == DealType.SELL
        
        deal.volume = 0.5
        assert deal.volume == 0.5
        
        deal.price = 1.2500
        assert deal.price == 1.2500

    def test_enum_properties(self):
        """Test enum value and name properties."""
        deal = Deal(Symbol.EUR_USD, dt.now(), DealType.BUY, 0.01, 1.08)
        
        assert deal.symbol.value == "EUR_USD"
        assert deal.symbol.name == "EUR_USD"
        assert deal.type.value == 1  # BUY type value
        assert deal.type.name == "BUY"

    def test_datetime_precision(self):
        """Test that datetime preserves microsecond precision."""
        microsecond_datetime = dt(2024, 10, 2, 14, 30, 45, 123456)
        deal = Deal(Symbol.EUR_USD, microsecond_datetime, DealType.BUY, 0.01, 1.08)
        
        assert deal.datetime.microsecond == 123456

    def test_floating_point_precision(self):
        """Test that price preserves floating point precision."""
        precise_price = 1.123456789
        deal = Deal(Symbol.EUR_USD, dt.now(), DealType.BUY, 0.01, precise_price)
        
        assert abs(deal.price - precise_price) < 1e-10

    def test_performance_small_scale(self):
        """Test performance with 100 deals."""
        start_time = time.time()
        
        deals = []
        for i in range(100):
            deal = Deal(
                symbol=Symbol.EUR_USD,
                datetime=dt.now(),
                type=DealType.BUY if i % 2 == 0 else DealType.SELL,
                volume=0.01,
                price=1.08
            )
            deals.append(deal)
        
        creation_time = time.time() - start_time
        
        # Verify ID uniqueness and sequence
        ids = [deal.id for deal in deals]
        assert ids == list(range(100))
        assert len(set(ids)) == 100
        
        # Should complete quickly
        assert creation_time < 1.0  # Less than 1 second

    def test_performance_medium_scale(self):
        """Test performance with 1000 deals."""
        start_time = time.time()
        
        deals = []
        symbols = [Symbol.EUR_USD, Symbol.GBP_USD, Symbol.USD_JPY, Symbol.AUD_USD]
        deal_types = [DealType.BUY, DealType.SELL]
        
        for i in range(1000):
            symbol = symbols[i % len(symbols)]
            deal_type = deal_types[i % len(deal_types)]
            
            deal = Deal(
                symbol=symbol,
                datetime=dt.now(),
                type=deal_type,
                volume=0.01 * (1 + (i % 10)),
                price=1.0 + (i % 1000) * 0.0001
            )
            deals.append(deal)
        
        creation_time = time.time() - start_time
        
        # Verify correctness
        ids = [deal.id for deal in deals]
        assert ids == list(range(1000))
        assert len(set(ids)) == 1000
        
        # Should complete reasonably quickly
        assert creation_time < 5.0  # Less than 5 seconds

    def test_dictionary_serialization_batch(self):
        """Test dictionary serialization for multiple deals."""
        deals = []
        for i in range(50):
            deal = Deal(
                symbol=Symbol.EUR_USD,
                datetime=dt.now(),
                type=DealType.BUY,
                volume=0.01,
                price=1.08
            )
            deals.append(deal)
        
        # Serialize all deals to dictionaries
        deal_dicts = [deal.as_dict() for deal in deals]
        
        # Verify all dictionaries have correct structure
        expected_keys = {'id', 'symbol', 'datetime', 'type', 'volume', 'price'}
        for deal_dict in deal_dicts:
            assert set(deal_dict.keys()) == expected_keys

    def test_portfolio_statistics(self):
        """Test portfolio-like statistics calculations."""
        deals = [
            Deal(Symbol.EUR_USD, dt.now(), DealType.BUY, 0.1, 1.08),
            Deal(Symbol.EUR_USD, dt.now(), DealType.SELL, 0.05, 1.09),
            Deal(Symbol.GBP_USD, dt.now(), DealType.BUY, 0.2, 1.27),
            Deal(Symbol.GBP_USD, dt.now(), DealType.SELL, 0.15, 1.28),
        ]
        
        buy_deals = [d for d in deals if d.type == DealType.BUY]
        sell_deals = [d for d in deals if d.type == DealType.SELL]
        
        assert len(buy_deals) == 2
        assert len(sell_deals) == 2
        
        total_buy_volume = sum(d.volume for d in buy_deals)
        total_sell_volume = sum(d.volume for d in sell_deals)
        
        assert abs(total_buy_volume - 0.3) < 1e-10
        assert abs(total_sell_volume - 0.2) < 1e-10
        
        symbols_used = set(d.symbol for d in deals)
        assert len(symbols_used) == 2
        assert Symbol.EUR_USD in symbols_used
        assert Symbol.GBP_USD in symbols_used

    def test_memory_efficiency_batches(self):
        """Test memory-efficient deal processing in batches."""
        batch_size = 100
        total_processed = 0
        
        for batch in range(3):  # Process 3 batches
            batch_deals = []
            
            for i in range(batch_size):
                deal = Deal(
                    symbol=Symbol.EUR_USD,
                    datetime=dt.now(),
                    type=DealType.BUY,
                    volume=0.01,
                    price=1.08
                )
                batch_deals.append(deal)
            
            # Process the batch (serialize and discard)
            batch_dicts = [deal.as_dict() for deal in batch_deals]
            total_processed += len(batch_deals)
            
            # Clear the batch
            del batch_deals, batch_dicts
            gc.collect()
        
        # Verify final ID counter
        next_id = Deal.generate_id()
        assert next_id == total_processed

    def test_string_representation(self):
        """Test string representation of Deal objects."""
        deal = Deal(Symbol.EUR_USD, dt.now(), DealType.BUY, 0.01, 1.08)
        str_repr = str(deal)
        
        # Should contain key information
        assert "Deal" in str_repr
        assert "EUR_USD" in str_repr
        assert "BUY" in str_repr
        assert "0.01" in str_repr
        assert "1.08" in str_repr

    @pytest.mark.parametrize("symbol,deal_type,volume,price", [
        (Symbol.EUR_USD, DealType.BUY, 0.01, 1.08),
        (Symbol.GBP_USD, DealType.SELL, 0.05, 1.27),
        (Symbol.USD_JPY, DealType.BUY, 0.1, 150.0),
        (Symbol.BTC_USD, DealType.SELL, 0.001, 65000.0),
        (Symbol.XAG_USD, DealType.BUY, 1.0, 32.5),
    ])
    def test_parametrized_deal_creation(self, symbol, deal_type, volume, price):
        """Parametrized test for various deal configurations."""
        deal = Deal(
            symbol=symbol,
            datetime=dt.now(),
            type=deal_type,
            volume=volume,
            price=price
        )
        
        assert deal.symbol == symbol
        assert deal.type == deal_type
        assert deal.volume == volume
        assert deal.price == price
        assert isinstance(deal.id, int)
        assert deal.id >= 0