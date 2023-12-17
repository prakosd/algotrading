"""Module of Oanda Provider"""
from dataclasses import dataclass
import os.path
import decimal
import pandas as pd
from v20.errors import ResponseNoField
import tpqoa

from ...config import config
from ..api import EIProvider

@dataclass
class Oanda(EIProvider):
    """Implementation of EIProvider Class"""
    _INDEX_COL = "time"
    _PRICE_ASK = "A"
    _PRICE_BID = "B"
    _PRICE_MID = "M"
    _API       = tpqoa.tpqoa(config.provider.config_path_oanda)

    @staticmethod
    def get_instruments(force_download: bool=False) -> pd.DataFrame:
        """Returns available instruments"""
        filename = EIProvider.PROVIDER_OANDA + "_INSTRUMENTS" + EIProvider._FILE_EXT

        if os.path.exists(EIProvider._DATA_DIR + filename) and not force_download:
            return pd.read_csv(EIProvider._DATA_DIR + filename)

        if not os.path.exists(EIProvider._DATA_DIR):
            os.mkdir(EIProvider._DATA_DIR)

        instruments = pd.DataFrame.from_records(Oanda._API.get_instruments(),
                                                columns=["symbol", "instrument"])
        instruments[["symbol", "instrument"]]=instruments[["instrument", "symbol"]]
        instruments.to_csv(EIProvider._DATA_DIR + filename, index=False)

        return instruments

    def get_filename(self) -> str:
        """Retrieve filename of saved response"""
        if self._filename is not None:
            return self._filename

        name = f"OANDA_{self.symbol}_{self.start}_{self.end}_{self.granularity.value}"
        self._filename = name + EIProvider._FILE_EXT

        return self._filename

    def get_response(self, force_download: bool=False) -> pd.DataFrame:
        """Returns response from the provider"""
        if self._response is not None and not force_download:
            return self._response

        self._fetch_data(force_download)
        return self._response

    def _fetch_data(self, force_download: bool=False):
        self.get_filename()

        if os.path.exists(EIProvider._DATA_DIR + self._filename) and not force_download:
            self._response = pd.read_csv(EIProvider._DATA_DIR + self._filename,
                                         parse_dates=[Oanda._INDEX_COL],
                                         index_col=Oanda._INDEX_COL)

        else:
            if not os.path.exists(EIProvider._DATA_DIR):
                os.mkdir(EIProvider._DATA_DIR)

            self._prepare_data()
            if self._response is None:
                return None

            self._response.to_csv(EIProvider._DATA_DIR + self._filename)

    def _prepare_data(self):
        print("(1/3) Fetching data...", flush=True, end="\r")
        try:
            ask = Oanda._API.get_history(instrument=self.symbol,
                                            start=self.start, end=self.end,
                                            granularity=self.granularity.value,
                                            price=Oanda._PRICE_ASK, localize=False)
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
        bid = Oanda._API.get_history(instrument=self.symbol,
                                        start=self.start, end=self.end,
                                        granularity=self.granularity.value,
                                        price=Oanda._PRICE_BID, localize=False)

        bid = bid.dropna()
        bid = bid.loc[bid.complete]
        bid = bid.drop(["o", "h", "l", "complete", "volume"], axis=1)
        bid = bid.rename(columns={"c": "bid"})

        print("(3/3) Fetching data.....", flush=True, end="\r")
        mid = Oanda._API.get_history(instrument=self.symbol,
                                        start=self.start, end=self.end,
                                        granularity=self.granularity.value,
                                        price=Oanda._PRICE_MID, localize=False)

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
        self._response = raw.sort_index()
        print("                        ", flush=True, end="\r")
