"""Module of Oanda Provider Class"""
import os.path
import decimal
import pandas as pd
from v20.errors import ResponseNoField
import tpqoa

from ...config import config
from ..api import EIProvider
from ...ticker import EITicker, Ticker

class OandaProvider(EIProvider):
    """Implementation of EIProvider"""
    _INDEX_COL = "time"
    _PRICE_ASK = "A"
    _PRICE_BID = "B"
    _PRICE_MID = "M"
    _API       = tpqoa.tpqoa(config.provider.config_path_oanda)

    @staticmethod
    def get_instruments(force_download: bool=False) -> pd.DataFrame:
        """Return available instruments"""
        filename = EIProvider.PROVIDER_OANDA + "_INSTRUMENTS" + EIProvider._FILE_EXT

        if os.path.exists(EIProvider._DATA_DIR + filename) and not force_download:
            return pd.read_csv(EIProvider._DATA_DIR + filename)

        if not os.path.exists(EIProvider._DATA_DIR):
            os.mkdir(EIProvider._DATA_DIR)

        instruments = pd.DataFrame.from_records(OandaProvider._API.get_instruments(),
                                                columns=["symbol", "instrument"])
        instruments[["symbol", "instrument"]]=instruments[["instrument", "symbol"]]
        instruments.to_csv(EIProvider._DATA_DIR + filename, index=False)

        return instruments

    def get_filename(self) -> str:
        """Generate and return filename of saved response"""
        name = f"OANDA_{self.symbol}_{self.start}_{self.end}_{self.timeframe.value.description}"
        filename = name + EIProvider._FILE_EXT

        return filename

    def get_response(self, force_download: bool=False) -> pd.DataFrame:
        """Return response from provider"""
        return self._fetch_data(force_download)

    def _fetch_data(self, force_download: bool=False) -> pd.DataFrame:
        filename = self.get_filename()

        if os.path.exists(EIProvider._DATA_DIR + filename) and not force_download:
            response = pd.read_csv(EIProvider._DATA_DIR + filename,
                                         parse_dates=[OandaProvider._INDEX_COL],
                                         index_col=OandaProvider._INDEX_COL)

        else:
            if not os.path.exists(EIProvider._DATA_DIR):
                os.mkdir(EIProvider._DATA_DIR)

            response = self._prepare_data()
            if response is not None:
                response.to_csv(EIProvider._DATA_DIR + filename)

        return response

    def _prepare_data(self) -> pd.DataFrame:
        print("(1/3) Fetching data...", flush=True, end="\r")
        try:
            ask = OandaProvider._API.get_history(instrument=self.symbol,
                                            start=self.start, end=self.end,
                                            granularity=self.timeframe.value.granularity,
                                            price=OandaProvider._PRICE_ASK, localize=False)
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
        bid = OandaProvider._API.get_history(instrument=self.symbol,
                                        start=self.start, end=self.end,
                                        granularity=self.timeframe.value.granularity,
                                        price=OandaProvider._PRICE_BID, localize=False)

        bid = bid.dropna()
        bid = bid.loc[bid.complete]
        bid = bid.drop(["o", "h", "l", "complete", "volume"], axis=1)
        bid = bid.rename(columns={"c": "bid"})

        print("(3/3) Fetching data.....", flush=True, end="\r")
        mid = OandaProvider._API.get_history(instrument=self.symbol,
                                        start=self.start, end=self.end,
                                        granularity=self.timeframe.value.granularity,
                                        price=OandaProvider._PRICE_MID, localize=False)

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

    def get_ticker(self, force_download: bool=False) -> EITicker:
        """Return response in EITicker object"""

        return Ticker(self.symbol, self.start, self.end,
                      self.timeframe, self._fetch_data(force_download))
