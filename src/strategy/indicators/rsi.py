from __future__ import annotations
import pandas as pd

class RSIIndicator:
    def __init__(self, close: pd.Series, window: int = 14):
        self.close = close
        self.window = window

    def rsi(self) -> pd.Series:
        delta = self.close.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.ewm(alpha=1/self.window, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1/self.window, adjust=False).mean()
        rs = avg_gain / (avg_loss.replace(0, 1e-12))
        return 100 - (100 / (1 + rs))

# wrapper esperado em alguns testes
class RSI:
    def __init__(self, close: pd.Series, window: int = 14):
        self._ind = RSIIndicator(close, window)

    def rsi(self) -> pd.Series:
        return self._ind.rsi()
