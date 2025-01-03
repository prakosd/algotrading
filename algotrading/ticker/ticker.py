"""Module of Ticker Class"""
from dataclasses import dataclass
from datetime import datetime as dt
from typing import ClassVar, Self
import matplotlib.pyplot as plt
import pandas as pd

from ..common.asset import AssetPairCode as Symbol
from ..common.trade import Timeframe
from .tick import Tick

plt.style.use("seaborn-v0_8")

@dataclass(frozen=True)
class Ticker():
    """Ticker Class"""
    _FIGURE_SIZE: ClassVar[tuple[float, float]] = (12, 8)
    _SYMBOL_DELIMITER: ClassVar[str] = "_"

    symbol: Symbol
    start: dt
    end: dt
    timeframe: Timeframe
    data: pd.DataFrame
    reversed: bool = False

    def get_data(self, index: int = None,
                 datetime: str = None) -> pd.DataFrame | Tick | None:
        """Return ticker data"""
        if self.data is None:
            return None

        if index is None and datetime is None:
            return self.data.copy()

        if index is not None:
            row = self.data.iloc[index]

        if datetime is not None:
            try:
                row = self.data.loc[pd.to_datetime(datetime)]
                if row is None:
                    return None
            except KeyError as exp:
                print(exp)
                return None

        return Tick(self.symbol, row.name,
                    row.ask, row.bid, row.mid,
                    int(row.volume), int(row.digit),
                    int(row.spread))

    def get_timezone(self) -> str:
        """Return ticker timezone"""
        if self.data is None:
            return "None"

        return self.data.index.tz

    def get_length(self) -> int:
        """Return number of tick"""
        if self.data is None:
            return 0

        return len(self.data.index)

    def get_digit(self) -> int:
        """Return symbol's decimal place"""
        if self.data is None:
            return 0

        return int(self.data.iloc[0].digit)

    def plot(self):
        """Plot ticker data"""
        if self.data is None:
            print("No data to plot")
        else:
            title = f"{self.symbol.value} - ({self.timeframe.value.description})"
            self.data.mid.plot(title=title, figsize=self._FIGURE_SIZE)

    def resample(self, to_timeframe: Timeframe) -> Self | None:
        """Resample ticker data from lower to higher timeframe"""
        if self.data is None:
            return None

        tf_start_id = self.timeframe.value.id
        tf_end_id   = to_timeframe.value.id

        if tf_end_id > tf_start_id:
            df = self.data.resample(
                to_timeframe.value.resample, label="right").last().ffill()

            print(f"{self.symbol.value} - Resampling {self.timeframe.value.description} -> "
                  f"{to_timeframe.value.description} successful")

            return Ticker(self.symbol, self.start, self.end,
                      to_timeframe, df)

        print(f"{self.symbol.value} - Resampling to lower and equal timeframe is not allowed. "
              f"{self.timeframe.value.description} -> {to_timeframe.value.description}")

        return None

    def append(self, ticker: Self) -> Self | None:
        """Append ticker data with ticker of the same symbol and timeframe"""
        if self.data is None and ticker.data is None:
            return None

        tf_self_id = self.timeframe.value.id
        tf_them_id = ticker.timeframe.value.id

        symbol_self = self.symbol.value
        symbol_them = ticker.symbol.value

        if tf_self_id == tf_them_id and symbol_self == symbol_them:
            df = pd.concat(
                [self.data, ticker.data]).drop_duplicates().sort_index()
            print("Appending successful")

            return Ticker(self.symbol, min(self.start, ticker.start), max(self.end, ticker.end),
                      self.timeframe, df)

        print(f"Only appending tickers with the same symbol and timeframe are allowed. "
              f"{self.timeframe.value.description} -> "
              f"{ticker.timeframe.value.description} -> "
              f"{symbol_self} & {symbol_them}")

        return None

    def reverse(self) -> Self | None:
        """Return the multiplicative inverse (or reciprocal) of 
        the ticker data for the currency pair"""
        if self.data is None:
            return None

        [base, quote] = self.symbol.value.split(self._SYMBOL_DELIMITER)
        print(f"Reversing {self.symbol.value} to {quote}_{base}")

        df = self.data.copy()
        df["ask_temp"] = df.ask
        df.ask = 1 / df.bid
        df.bid = 1 / df.ask_temp
        df.mid = 1 / df.mid
        df = df.drop(columns="ask_temp", axis=1)

        df.ask = df.apply(lambda x: round(x.ask, x.digit.astype(int)), axis=1)
        df.bid = df.apply(lambda x: round(x.bid, x.digit.astype(int)), axis=1)
        df.mid = df.apply(lambda x: round(x.mid, x.digit.astype(int)), axis=1)

        df.spread = round((df.ask - df.bid) * pow(10, df.digit), 0).apply(int)

        return Ticker(self.symbol, self.start, self.end,
                      self.timeframe, df, True)

    def analyze(self, plot_data: bool=True) -> pd.DataFrame:
        """Analyze ticker data and return the result"""
        df = self.data.copy()
        df["hour"] = df.index.hour
        df["change"] = df.mid.diff().fillna(0).abs() * pow(10, df.digit)
        df["change"] = df["change"].apply(int)

        by_hour = df.groupby("hour")[["volume", "spread", "change"]].mean()
        by_hour["mean"] = by_hour["volume"].mean()
        by_hour["cover"] = by_hour["change"] > by_hour["spread"]
        by_hour["color"] = by_hour.apply(self._produce_color, axis=1)

        if plot_data:
            title = f"{self.symbol.value} - by Hour"
            by_hour.volume.plot(kind="bar", title=title,
                                figsize=(12, 8), fontsize=13,
                                color=by_hour["color"])
            plt.xlabel(f"Hour ({self.get_timezone()})", fontsize=10)
            plt.ylabel("Volume", fontsize=10)
            plt.axhline(by_hour["volume"].mean(), color='darkgreen',
                        linestyle='--', linewidth=2, label='Mean')

        return by_hour

    def _produce_color(self, df: pd.DataFrame) -> str:
        if not df["cover"]:
            return "red"
        elif df["cover"] and df["volume"] > df["mean"]:
            return "darkgreen"
        else:
            return "gray"
