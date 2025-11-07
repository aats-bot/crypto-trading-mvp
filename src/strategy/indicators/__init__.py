from __future__ import annotations


# src/strategy/indicators/__init__.py
import types
import sys
import pandas as pd

PKG = __name__  # "src.strategy.indicators"
# ---- Implementações mínimas e determinísticas usadas nos testes ----

class EMAIndicator:
    def __init__(self, close: pd.Series, window: int = 12, adjust: bool = False):
        self.close = close
        self.window = window
        self.adjust = adjust
    def ema(self) -> pd.Series:
        return self.close.ewm(span=self.window, adjust=self.adjust).mean()

class RSIIndicator:
    def __init__(self, close: pd.Series, window: int = 14):
        self.close = close; self.window = window
    def rsi(self) -> pd.Series:
        delta = self.close.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.ewm(alpha=1/self.window, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1/self.window, adjust=False).mean()
        rs = avg_gain / (avg_loss.replace(0, 1e-12))
        return 100 - (100 / (1 + rs))

class ATRIndicator:
    def __init__(self, high: pd.Series, low: pd.Series, close: pd.Series, window: int = 14):
        self.high, self.low, self.close, self.window = high, low, close, window
    def atr(self) -> pd.Series:
        prev_close = self.close.shift(1)
        tr = pd.concat([
            (self.high - self.low),
            (self.high - prev_close).abs(),
            (self.low - prev_close).abs(),
        ], axis=1).max(axis=1)
        return tr.rolling(self.window, min_periods=1).mean()

class EWOIndicator:
    """Elliott Wave Oscillator = EMA(fast) - EMA(slow)"""
    def __init__(self, close: pd.Series, fast: int = 5, slow: int = 35, adjust: bool = False):
        self.close, self.fast, self.slow, self.adjust = close, fast, slow, adjust
    def ewo(self) -> pd.Series:
        f = self.close.ewm(span=self.fast, adjust=self.adjust).mean()
        s = self.close.ewm(span=self.slow, adjust=self.adjust).mean()
        return f - s

class StochRSIIndicator:
    def __init__(self, close: pd.Series, rsi_window: int = 14, k_window: int = 14):
        self.close, self.rsi_window, self.k_window = close, rsi_window, k_window
    def stoch_rsi(self) -> pd.Series:
        rsi = RSIIndicator(self.close, window=self.rsi_window).rsi()
        roll_min = rsi.rolling(self.k_window, min_periods=1).min()
        roll_max = rsi.rolling(self.k_window, min_periods=1).max()
        denom = (roll_max - roll_min).replace(0, 1e-12)
        return 100 * (rsi - roll_min) / denom

class MACDIndicator:
    def __init__(self, close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9, adjust: bool = False):
        self.close, self.fast, self.slow, self.signal, self.adjust = close, fast, slow, signal, adjust
    def macd(self):
        ema_fast = self.close.ewm(span=self.fast, adjust=self.adjust).mean()
        ema_slow = self.close.ewm(span=self.slow, adjust=self.adjust).mean()
        macd = ema_fast - ema_slow
        signal = macd.ewm(span=self.signal, adjust=self.adjust).mean()
        hist = macd - signal
        return macd, signal, hist

class BBANDSIndicator:
    def __init__(self, close: pd.Series, window: int = 20, n_std: float = 2.0):
        self.close, self.window, self.n_std = close, window, n_std
    def bands(self):
        ma = self.close.rolling(self.window, min_periods=1).mean()
        sd = self.close.rolling(self.window, min_periods=1).std(ddof=0).fillna(0)
        upper = ma + self.n_std * sd
        lower = ma - self.n_std * sd
        return lower, ma, upper

# Wrappers simples que alguns testes esperam
class EMA: 
    def __init__(self, close: pd.Series, window: int = 12, adjust: bool = False): self._i = EMAIndicator(close, window, adjust)
    def ema(self): return self._i.ema()

class RSI:
    def __init__(self, close: pd.Series, window: int = 14): self._i = RSIIndicator(close, window)
    def rsi(self): return self._i.rsi()

class ATR:
    def __init__(self, high, low, close, window: int = 14): self._i = ATRIndicator(high, low, close, window)
    def atr(self): return self._i.atr()

class EWO:
    def __init__(self, close, fast=5, slow=35, adjust=False): self._i = EWOIndicator(close, fast, slow, adjust)
    def ewo(self): return self._i.ewo()

class StochRSI:
    def __init__(self, close, rsi_window=14, k_window=14): self._i = StochRSIIndicator(close, rsi_window, k_window)
    def stoch_rsi(self): return self._i.stoch_rsi()

class MACD:
    def __init__(self, close, fast=12, slow=26, signal=9, adjust=False): self._i = MACDIndicator(close, fast, slow, signal, adjust)
    def macd(self): return self._i.macd()

class BBANDS:
    def __init__(self, close, window=20, n_std=2.0): self._i = BBANDSIndicator(close, window, n_std)
    def bands(self): return self._i.bands()

# ---- Public API direto do pacote ----
__all__ = [
    "EMAIndicator","RSIIndicator","ATRIndicator","EWOIndicator","StochRSIIndicator","MACDIndicator","BBANDSIndicator",
    "EMA","RSI","ATR","EWO","StochRSI","MACD","BBANDS"
]

# ---- Submódulos dinâmicos (fazem imports do tipo ...indicators.ema funcionarem) ----
def _make_module(name: str, symbols: dict):
    m = types.ModuleType(f"{PKG}.{name}")
    m.__dict__.update(symbols)
    sys.modules[m.__name__] = m

_make_module("ema", {"EMAIndicator": EMAIndicator, "EMA": EMA})
_make_module("rsi", {"RSIIndicator": RSIIndicator, "RSI": RSI})
_make_module("atr", {"ATRIndicator": ATRIndicator, "ATR": ATR})
_make_module("ewo", {"EWOIndicator": EWOIndicator, "EWO": EWO})
_make_module("stoch_rsi", {"StochRSIIndicator": StochRSIIndicator, "StochRSI": StochRSI})
_make_module("macd", {"MACDIndicator": MACDIndicator, "MACD": MACD})
_make_module("bbands", {"BBANDSIndicator": BBANDSIndicator, "BBANDS": BBANDS})
