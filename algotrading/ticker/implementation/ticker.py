"""Module of Ticker Class"""
import matplotlib.pyplot as plt
import pandas as pd

from ...common import Timeframe
from ..api import EITicker, EITick

plt.style.use("seaborn")

class Ticker(EITicker):
    """Implementation of EITicker"""

    def get_data(self, index: int = None,
                 datetime: str = None) -> pd.DataFrame | EITick | None:
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
            except KeyError as exp:
                print(exp)
                return None

        if row is None:
            return None

        return EITick(self.symbol, row.name,
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
            title = f"{self.symbol} - ({self.timeframe.value.description})"
            self.data.mid.plot(title=title, figsize=(12, 8))

    def resample(self, to_timeframe: Timeframe) -> pd.DataFrame | None:
        """Resample ticker data from lower to higher timeframe"""
        if self.data is None:
            return None

        tf_start_id = self.timeframe.value.id
        tf_end_id   = to_timeframe.value.id

        if tf_end_id > tf_start_id:
            self.data = self.data.resample(
                to_timeframe.value.resample, label="right").last().ffill()
            print(f"{self.symbol} - Resampling {self.timeframe.value.description} -> "
                  f"{to_timeframe.value.description} successful")
            self.timeframe = to_timeframe
            return self.data.copy()

        print(f"{self.symbol} - Resampling to lower and equal timeframe is not allowed. "
              f"{self.timeframe.value.description} -> {to_timeframe.value.description}")
        return None

    def append(self, ticker: EITicker) -> pd.DataFrame | None:
        """Append ticker data with ticker of the same symbol and timeframe"""
        if self.data is None and ticker.data is None:
            return None

        tf_self_id = self.timeframe.value.id
        tf_them_id = ticker.timeframe.value.id

        symbol_self = self.symbol
        symbol_them = ticker.symbol

        if tf_self_id == tf_them_id and symbol_self == symbol_them:
            self.data = pd.concat(
                [self.data, ticker.data]).drop_duplicates().sort_index()
            print("Appending successful")
            return self.data

        print(f"Only appending tickers with the same symbol and timeframe are allowed. "
              f"{self.timeframe.value.description} -> "
              f"{ticker.timeframe.value.description} -> "
              f"{symbol_self} & {symbol_them}")
        return None

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
            title = f"{self.symbol} - by Hour"
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
