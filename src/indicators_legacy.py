# src/indicators.py
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Optional
import math

# ---------- Base ----------
class BaseIndicator:
    def __init__(self, period: int = 14, name: Optional[str] = None) -> None:
        self.period = int(period)
        self.data: List[float] = []
        self.name: str = name or self.__class__.__name__
        self._is_ready: bool = False

    def add_value(self, value: float) -> None:
        self.data.append(float(value))
        if len(self.data) >= self.period:
            self._is_ready = True

    def is_ready(self) -> bool:
        return self._is_ready


# ---------- EMA ----------
class EMAIndicator(BaseIndicator):
    def __init__(self, period: int = 14) -> None:
        super().__init__(period, "EMA")
        self.multiplier = 2.0 / (self.period + 1.0)
        self._ema: Optional[float] = None

    def add_value(self, value: float) -> float:
        v = float(value)
        super().add_value(v)
        if self._ema is None:
            # seed com média simples inicial quando houver dados suficientes
            if len(self.data) >= self.period:
                self._ema = sum(self.data[-self.period:]) / self.period
            else:
                self._ema = v
        else:
            self._ema = (v - self._ema) * self.multiplier + self._ema
        return self._ema

    def get_value(self) -> float:
        return float(self._ema or 0.0)


# ---------- RSI ----------
class RSIIndicator(BaseIndicator):
    def __init__(self, period: int = 14) -> None:
        super().__init__(period, "RSI")
        self.prev: Optional[float] = None
        self.avg_gain: float = 0.0
        self.avg_loss: float = 0.0
        self._rsi: float = 0.0
        self._warmup: List[float] = []

    def add_value(self, value: float) -> float:
        v = float(value)
        super().add_value(v)

        if self.prev is None:
            self.prev = v
            self._warmup.append(v)
            return self._rsi

        change = v - self.prev
        gain = max(change, 0.0)
        loss = max(-change, 0.0)

        if len(self._warmup) < self.period:
            self._warmup.append(v)
            self.avg_gain += gain
            self.avg_loss += loss
            if len(self._warmup) == self.period:
                self.avg_gain /= self.period
                self.avg_loss /= self.period
        else:
            self.avg_gain = (self.avg_gain * (self.period - 1) + gain) / self.period
            self.avg_loss = (self.avg_loss * (self.period - 1) + loss) / self.period

        self.prev = v
        if self.avg_loss == 0:
            self._rsi = 100.0
        else:
            rs = self.avg_gain / self.avg_loss
            self._rsi = 100.0 - (100.0 / (1.0 + rs))
        return self._rsi

    def get_value(self) -> float:
        return float(self._rsi)


# ---------- ATR ----------
class ATRIndicator(BaseIndicator):
    def __init__(self, period: int = 14) -> None:
        super().__init__(period, "ATR")
        self.prev_close: Optional[float] = None
        self.tr_values: List[float] = []
        self._atr: float = 0.0

    def add_ohlc_data(self, o: float, h: float, l: float, c: float) -> float:
        o, h, l, c = map(float, (o, h, l, c))
        # True Range
        if self.prev_close is None:
            tr = h - l
        else:
            tr = max(h - l, abs(h - self.prev_close), abs(l - self.prev_close))
        self.prev_close = c

        self.tr_values.append(tr)
        self.add_value(c)

        if len(self.tr_values) < self.period:
            self._atr = sum(self.tr_values) / len(self.tr_values)
        else:
            if len(self.tr_values) == self.period:
                self._atr = sum(self.tr_values[-self.period:]) / self.period
            else:
                self._atr = (self._atr * (self.period - 1) + tr) / self.period
        return self._atr

    def get_value(self) -> float:
        return float(self._atr)


# ---------- UT Bot (simplificado) ----------
class UTBotIndicator(BaseIndicator):
    def __init__(self, period: int = 14, multiplier: float = 2.0) -> None:
        super().__init__(period, "UTBot")
        self.multiplier = float(multiplier)
        self.last_signal: Optional[str] = None

    def calculate_signal(self, price: float, ema_value: float) -> str:
        # regra simples: desvio > multiplier% do EMA
        threshold = ema_value * (self.multiplier / 100.0)
        if price > ema_value + threshold:
            self.last_signal = "buy"
        elif price < ema_value - threshold:
            self.last_signal = "sell"
        else:
            self.last_signal = "hold"
        return self.last_signal


# ---------- EWO ----------
class EWOIndicator(BaseIndicator):
    def __init__(self, fast_period: int = 5, slow_period: int = 35) -> None:
        super().__init__(fast_period, "EWO")
        self.fast = EMAIndicator(fast_period)
        self.slow = EMAIndicator(slow_period)
        self._value: float = 0.0

    def add_value(self, price: float) -> float:
        f = self.fast.add_value(price)
        s = self.slow.add_value(price)
        self._value = float(f - s)
        # readiness = quando o lento estiver pronto
        self._is_ready = self.slow.is_ready()
        return self._value

    def get_value(self) -> float:
        return float(self._value)


# ---------- StochRSI ----------
class StochRSIIndicator(BaseIndicator):
    def __init__(self, rsi_period: int = 14, stoch_period: int = 14) -> None:
        super().__init__(rsi_period, "StochRSI")
        self.rsi = RSIIndicator(rsi_period)
        self.stoch_period = int(stoch_period)
        self.rsi_values: List[float] = []
        self._value: float = 0.5

    def add_value(self, price: float) -> float:
        rsi_val = self.rsi.add_value(price)
        self.rsi_values.append(rsi_val)
        window = self.rsi_values[-self.stoch_period:] if len(self.rsi_values) >= self.stoch_period else self.rsi_values
        lo = min(window) if window else 0.0
        hi = max(window) if window else 100.0
        self._value = 0.0 if hi == lo else (rsi_val - lo) / (hi - lo)
        self._is_ready = self.rsi.is_ready() and len(self.rsi_values) >= self.stoch_period
        return self._value

    def get_value(self) -> float:
        return float(self._value)


# ---------- Heikin Ashi ----------
@dataclass
class HeikinAshiCandle:
    open: float
    high: float
    low: float
    close: float

class HeikinAshiIndicator:
    def __init__(self) -> None:
        self.candles: List[HeikinAshiCandle] = []

    def calculate_candles(self, opens: List[float], highs: List[float], lows: List[float], closes: List[float]) -> List[HeikinAshiCandle]:
        ha: List[HeikinAshiCandle] = []
        prev_ha_open = opens[0] if opens else 0.0
        prev_ha_close = closes[0] if closes else 0.0
        for o, h, l, c in zip(opens, highs, lows, closes):
            ha_close = (o + h + l + c) / 4.0
            ha_open = (prev_ha_open + prev_ha_close) / 2.0
            ha_high = max(h, ha_open, ha_close)
            ha_low = min(l, ha_open, ha_close)
            prev_ha_open, prev_ha_close = ha_open, ha_close
            ha.append(HeikinAshiCandle(ha_open, ha_high, ha_low, ha_close))
        self.candles = ha
        return ha


# Helpers para robustez (NaN/Inf clamp)
def safe_float(x: float, default: float = 0.0) -> float:
    if x is None or math.isnan(x) or math.isinf(x):
        return default
    return float(x)
