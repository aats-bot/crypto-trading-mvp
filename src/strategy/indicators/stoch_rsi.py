from __future__ import annotations
import pandas as pd
from .rsi import RSIIndicator

class StochRSIIndicator:
    """
    Stochastic RSI: normaliza o RSI no intervalo [0,100] usando janela (k_window).
    Fórmula: 100 * (RSI - min(RSI_w)) / (max(RSI_w) - min(RSI_w))
    """
    def __init__(self, close: pd.Series, rsi_window: int = 14, k_window: int = 14):
        self.close = close
        self.rsi_window = rsi_window
        self.k_window = k_window

    def stoch_rsi(self) -> pd.Series:
        rsi = RSIIndicator(self.close, window=self.rsi_window).rsi()
        roll_min = rsi.rolling(self.k_window, min_periods=1).min()
        roll_max = rsi.rolling(self.k_window, min_periods=1).max()
        denom = (roll_max - roll_min).replace(0, 1e-12)
        return 100 * (rsi - roll_min) / denom

# wrapper simples
class StochRSI:
    def __init__(self, close: pd.Series, rsi_window: int = 14, k_window: int = 14):
        self._ind = StochRSIIndicator(close, rsi_window=rsi_window, k_window=k_window)

    def stoch_rsi(self) -> pd.Series:
        return self._ind.stoch_rsi()
