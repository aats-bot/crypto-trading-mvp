from __future__ import annotations
import pandas as pd

class EMAIndicator:
    def __init__(self, close: pd.Series, window: int = 12, adjust: bool = False):
        self.close = close
        self.window = window
        self.adjust = adjust

    def ema(self) -> pd.Series:
        return self.close.ewm(span=self.window, adjust=self.adjust).mean()

# Classes compatíveis esperadas pelos testes
class EMA:
    def __init__(self, close: pd.Series, window: int = 12, adjust: bool = False):
        self._impl = EMAIndicator(close, window, adjust)

    def calculate(self) -> pd.Series:
        return self._impl.ema()

class EMA20(EMA):
    def __init__(self, close: pd.Series, adjust: bool = False):
        super().__init__(close, window=20, adjust=adjust)

class EMA100(EMA):
    def __init__(self, close: pd.Series, adjust: bool = False):
        super().__init__(close, window=100, adjust=adjust)
