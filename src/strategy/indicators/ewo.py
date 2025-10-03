from __future__ import annotations
import pandas as pd

class EWOIndicator:
    """
    Elliott Wave Oscillator (EWO) = EMA(fast) - EMA(slow)
    Por padrão, fast=5, slow=35 (valores comuns).
    """
    def __init__(self, close: pd.Series, fast: int = 5, slow: int = 35, adjust: bool = False):
        self.close = close
        self.fast = fast
        self.slow = slow
        self.adjust = adjust

    def ewo(self) -> pd.Series:
        fast_ema = self.close.ewm(span=self.fast, adjust=self.adjust).mean()
        slow_ema = self.close.ewm(span=self.slow, adjust=self.adjust).mean()
        return fast_ema - slow_ema

# wrapper simplificado usado por alguns testes
class EWO:
    def __init__(self, close: pd.Series, fast: int = 5, slow: int = 35, adjust: bool = False):
        self._ind = EWOIndicator(close, fast=fast, slow=slow, adjust=adjust)

    def ewo(self) -> pd.Series:
        return self._ind.ewo()
