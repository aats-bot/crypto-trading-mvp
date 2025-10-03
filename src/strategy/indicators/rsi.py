from __future__ import annotations
import pandas as pd
try:
    import pandas_ta as ta
except Exception:
    ta = None

class RSIIndicator:
    def __init__(self, close: pd.Series, window: int = 14):
        self.close = close
        self.window = window

    def rsi(self) -> pd.Series:
        if ta is not None:
            return ta.rsi(self.close, length=self.window)
        # Fallback simples estilo Wilder
        delta = self.close.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        roll_up = gain.ewm(alpha=1/self.window, adjust=False).mean()
        roll_down = loss.ewm(alpha=1/self.window, adjust=False).mean().replace(0, 1e-12)
        rs = roll_up / roll_down
        return 100 - (100 / (1 + rs))
