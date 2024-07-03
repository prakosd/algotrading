"""Module of Oanda Provider Class"""
import decimal
import pandas as pd
from v20.errors import ResponseNoField
import tpqoa

from ...common.config import config
from ..api import EIProvider
from ...ticker import Ticker
from ...ticker import TickerManager, TickerMetadata

class OandaProvider(EIProvider):
    """Implementation of EIProvider"""
    _PRICE_ASK = "A"
    _PRICE_BID = "B"
    _PRICE_MID = "M"
    _API       = tpqoa.tpqoa(config.provider.oanda_config_path)

    @classmethod
    def get_instruments(cls, force_download: bool=False) -> pd.DataFrame:
        """Return available instruments"""
        filename = cls.OANDA + "_INSTRUMENTS" + TickerManager.FILE_EXT

        if not force_download:
            df = TickerManager.read(filename)
            if df is not None and not df.empty:
                return df

        df = pd.DataFrame.from_records(cls._API.get_instruments(),
                                                columns=["symbol", "instrument"])
        df[["symbol", "instrument"]] = df[["instrument", "symbol"]]

        if TickerManager.write(filename, df):
            return df

        return None

    def get_filename(self) -> str:
        """Generate and return filename of saved response"""
        return TickerManager.generate_filename(TickerMetadata(
            provider=self.OANDA,
            symbol=self.symbol,
            start=self.start,
            end=self.end,
            timeframe=self.timeframe
        ))

    def get_response(self, force_download: bool=False) -> pd.DataFrame:
        """Return response from provider"""
        return self._fetch_data(force_download)

    def _fetch_data(self, force_download: bool=False) -> pd.DataFrame:
        filename = self.get_filename()

        if not force_download:
            result = TickerManager.find_by_filename(filename)
            if isinstance(result, Ticker):
                return result.get_data()

        df = self._prepare_data()
        if TickerManager.write(filename, df):
            return df

        return None

    def _prepare_data(self) -> pd.DataFrame:
        print("(1/3) Fetching data...", flush=True, end="\r")
        symbol_oanda = self.translate_symbol(self.OANDA, self.symbol)
        try:
            ask = self._API.get_history(instrument=symbol_oanda,
                                            start=self.start, end=self.end,
                                            granularity=self.timeframe.value.granularity,
                                            price=self._PRICE_ASK, localize=False)
        except ResponseNoField as exp:
            print(f"ERROR ResponseNoField: {exp}")
            return
        except KeyError as exp:
            print(f"ERROR KeyError: {exp}")
            return

        ask = ask.dropna()
        ask = ask.loc[ask.complete]
        ask = ask.drop(["o", "h", "l", "complete", "volume"], axis=1)
        ask = ask.rename(columns={"c": "ask"})

        print("(2/3) Fetching data....", flush=True, end="\r")
        bid = self._API.get_history(instrument=symbol_oanda,
                                        start=self.start, end=self.end,
                                        granularity=self.timeframe.value.granularity,
                                        price=self._PRICE_BID, localize=False)

        bid = bid.dropna()
        bid = bid.loc[bid.complete]
        bid = bid.drop(["o", "h", "l", "complete", "volume"], axis=1)
        bid = bid.rename(columns={"c": "bid"})

        print("(3/3) Fetching data.....", flush=True, end="\r")
        mid = self._API.get_history(instrument=symbol_oanda,
                                        start=self.start, end=self.end,
                                        granularity=self.timeframe.value.granularity,
                                        price=self._PRICE_MID, localize=False)

        mid = mid.dropna()
        mid = mid.loc[mid.complete]
        mid = mid.drop(["o", "h", "l", "complete"], axis=1)
        mid = mid.rename(columns={"c": "mid"})

        raw = pd.concat([ask, bid, mid], axis="columns")

        print("Finalizing......", flush=True, end="\r")
        raw["digit"] = raw.apply(lambda row :
                                 (abs(decimal.Decimal(str(row.ask)).as_tuple().exponent)),
                                 axis=1).max()
        raw["spread"] = round((raw.ask - raw.bid) * pow(10, raw.digit), 0).apply(int)

        raw = raw.loc[~raw.index.duplicated(keep='first')]
        response = raw.sort_index()
        print("                        ", flush=True, end="\r")

        return response

    def get_ticker(self, force_download: bool=False) -> Ticker:
        """Return response as Ticker object"""
        df = self._fetch_data()
        if df is None or len(df) == 0:
            return None

        return Ticker(self.symbol, self.start, self.end,
                      self.timeframe, df)
