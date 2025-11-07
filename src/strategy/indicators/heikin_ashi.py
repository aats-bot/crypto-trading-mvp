from __future__ import annotations
import pandas as pd

class HeikinAshiIndicator:
    """
    Gera candles Heikin-Ashi a partir de OHLC.
    Uso:
        ind = HeikinAshiIndicator(open, high, low, close)
        df = ind.heikin_ashi()
    """
    def __init__(self, open: pd.Series, high: pd.Series, low: pd.Series, close: pd.Series):
        self.open = open.astype(float)
        self.high = high.astype(float)
        self.low = low.astype(float)
        self.close = close.astype(float)

    def heikin_ashi(self) -> pd.DataFrame:
        ha_close = (self.open + self.high + self.low + self.close) / 4.0

        ha_open = pd.Series(index=self.open.index, dtype=float)
        if len(self.open) > 0:
            ha_open.iloc[0] = (self.open.iloc[0] + self.close.iloc[0]) / 2.0
        for i in range(1, len(self.open)):
            ha_open.iloc[i] = (ha_open.iloc[i-1] + ha_close.iloc[i-1]) / 2.0

        ha_high = pd.concat([self.high, ha_open, ha_close], axis=1).max(axis=1)
        ha_low  = pd.concat([self.low, ha_open, ha_close], axis=1).min(axis=1)

        return pd.DataFrame(
            {"open": ha_open, "high": ha_high, "low": ha_low, "close": ha_close},
            index=self.open.index,
        )
