from __future__ import annotations
import pandas as pd

class ATRIndicator:
    def __init__(self, high: pd.Series, low: pd.Series, close: pd.Series, window: int = 14):
        self.high = high
        self.low = low
        self.close = close
        self.window = window

    def _true_range(self) -> pd.Series:
        prev_close = self.close.shift(1)
        tr1 = self.high - self.low
        tr2 = (self.high - prev_close).abs()
        tr3 = (self.low - prev_close).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        return tr

    def atr(self) -> pd.Series:
        tr = self._true_range()
        # Wilder smoothing = EMA com alpha = 1/window e adjust=False
        return tr.ewm(alpha=1 / self.window, adjust=False).mean()

# Wrapper compatível (caso os testes chamem .calculate())
class ATR:
    def __init__(self, high: pd.Series, low: pd.Series, close: pd.Series, window: int = 14):
        self._impl = ATRIndicator(high, low, close, window)

    def calculate(self) -> pd.Series:
        return self._impl.atr()
