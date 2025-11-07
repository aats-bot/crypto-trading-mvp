# Minimal, test-compatible indicators API
from __future__ import annotations
from typing import List, Optional, Iterable
import math

# reexport safe_float (usado por strategies)
try:
    from src.utils.data_utils import safe_float  # type: ignore
except Exception:
    def safe_float(x, default=None):
        try:
            v = float(x)
            if math.isnan(v) or math.isinf(v):
                return default
            return v
        except Exception:
            return default


class BaseIndicator:
    def __init__(self, period: int, **_):
        self.period = int(period)
        self.data: List[float] = []
        self.name = self.__class__.__name__

    # testes usam .add_value
    def add_value(self, value: float) -> None:
        v = safe_float(value, default=None)
        if v is not None:
            self.data.append(v)

    # alias (caso algum código legado chame add_data)
    add_data = add_value

    def is_ready(self) -> bool:
        return len(self.data) >= self.period

    def calculate(self, *_a, **_k):
        raise NotImplementedError


def _clean_series(seq: Iterable[float]) -> List[float]:
    out: List[float] = []
    for v in seq:
        fv = safe_float(v, default=None)
        if fv is not None:
            out.append(fv)
    return out


class EMAIndicator(BaseIndicator):
    def __init__(self, period: int, **_):
        super().__init__(period)

    def calculate(self, data: Optional[List[float]] = None) -> Optional[float]:
        seq = _clean_series(self.data if data is None else data)
        if not seq:
            return None
        k = 2.0 / (self.period + 1.0)
        ema = seq[0]
        for x in seq[1:]:
            ema = x * k + ema * (1.0 - k)
        return ema


class RSIIndicator(BaseIndicator):
    def __init__(self, period: int = 14, **_):
        super().__init__(period)

    def calculate(self, data: Optional[List[float]] = None) -> Optional[float]:
        seq = _clean_series(self.data if data is None else data)
        if len(seq) < self.period + 1:
            return None
        gains, losses = [], []
        for i in range(1, len(seq)):
            d = seq[i] - seq[i - 1]
            gains.append(max(d, 0.0))
            losses.append(-min(d, 0.0))
        g = sum(gains[-self.period:]) / self.period
        l = sum(losses[-self.period:]) / self.period
        if l == 0:
            return 100.0
        rs = g / l
        return 100.0 - (100.0 / (1.0 + rs))


class ATRIndicator(BaseIndicator):
    def __init__(self, period: int = 14, **_):
        super().__init__(period)
        self._ohlc: List[tuple[float, float, float]] = []  # (high, low, close)

    def add_ohlc_data(self, high: float, low: float, close: float) -> None:
        h = safe_float(high); l = safe_float(low); c = safe_float(close)
        if None not in (h, l, c):
            self._ohlc.append((h, l, c))

    def calculate(self, data=None) -> Optional[float]:
        if len(self._ohlc) < self.period + 1:
            return None
        trs: List[float] = []
        prev_close = self._ohlc[0][2]
        for (h, l, c) in self._ohlc[1:]:
            tr = max(h - l, abs(h - prev_close), abs(l - prev_close))
            trs.append(tr)
            prev_close = c
        if len(trs) < self.period:
            return None
        return sum(trs[-self.period:]) / self.period


class UTBotIndicator(BaseIndicator):
    def __init__(self, period: int = 14, multiplier: float = 2.0, **_):
        super().__init__(period)
        self.multiplier = float(multiplier)

    def calculate_signals(self, prices: List[float]) -> List[str]:
        seq = _clean_series(prices)
        if len(seq) < 2:
            return []
        out: List[str] = []
        for i in range(1, len(seq)):
            prev, cur = seq[i - 1], seq[i]
            change = (cur - prev) / prev if prev != 0 else 0.0
            if change > 0.005 * self.multiplier:
                out.append("buy")
            elif change < -0.005 * self.multiplier:
                out.append("sell")
            else:
                out.append("hold")
        return out


class EWOIndicator(BaseIndicator):
    def __init__(self, fast_period: int = 5, slow_period: int = 35, **_):
        super().__init__(fast_period)
        self.fast_period = int(fast_period)
        self.slow_period = int(slow_period)

    def _ema(self, seq: List[float], p: int) -> float:
        k = 2.0 / (p + 1.0)
        v = seq[0]
        for x in seq[1:]:
            v = x * k + v * (1.0 - k)
        return v

    def calculate(self, data: Optional[List[float]] = None) -> Optional[float]:
        seq = _clean_series(self.data if data is None else data)
        if len(seq) < max(self.fast_period, self.slow_period):
            return None
        return self._ema(seq, self.fast_period) - self._ema(seq, self.slow_period)


class StochRSIIndicator(BaseIndicator):
    def __init__(self, rsi_period: int = 14, stoch_period: int = 14, **_):
        super().__init__(rsi_period)
        self.rsi_period = int(rsi_period)
        self.stoch_period = int(stoch_period)

    def calculate(self, data: Optional[List[float]] = None) -> Optional[float]:
        seq = _clean_series(self.data if data is None else data)
        if len(seq) < self.rsi_period + self.stoch_period + 1:
            return None

        def _rsi(vals: List[float], p: int) -> Optional[float]:
            if len(vals) < p + 1:
                return None
            gains, losses = [], []
            for i in range(1, len(vals)):
                d = vals[i] - vals[i - 1]
                gains.append(max(d, 0.0))
                losses.append(-min(d, 0.0))
            g = sum(gains[-p:]) / p
            l = sum(losses[-p:]) / p
            if l == 0:
                return 100.0
            rs = g / l
            return 100.0 - (100.0 / (1.0 + rs))

        rsi_series: List[float] = []
        for i in range(self.rsi_period, len(seq)):
            r = _rsi(seq[: i + 1], self.rsi_period)
            if r is not None:
                rsi_series.append(r)
        if len(rsi_series) < self.stoch_period:
            return None
        window = rsi_series[-self.stoch_period:]
        mn, mx = min(window), max(window)
        if mx == mn:
            return 0.5
        return (rsi_series[-1] - mn) / (mx - mn)


class HeikinAshiIndicator:
    # Aceita quaisquer kwargs para não falhar em assinaturas divergentes
    def __init__(self, **_):
        pass

    def calculate_candles(self, ohlc: List[dict]) -> List[dict]:
        out: List[dict] = []
        ha_open = None
        for i, c in enumerate(ohlc):
            o = safe_float(c.get("open")); h = safe_float(c.get("high"))
            l = safe_float(c.get("low"));  cl = safe_float(c.get("close"))
            if None in (o, h, l, cl):
                continue
            ha_close = (o + h + l + cl) / 4.0
            if i == 0:
                ha_open = (o + cl) / 2.0
            else:
                prev = out[-1]
                ha_open = (prev["open"] + prev["close"]) / 2.0
            ha_high = max(h, ha_open, ha_close)
            ha_low = min(l, ha_open, ha_close)
            out.append({"open": ha_open, "high": ha_high, "low": ha_low, "close": ha_close})
        return out


__all__ = [
    "safe_float",
    "BaseIndicator",
    "EMAIndicator",
    "RSIIndicator",
    "ATRIndicator",
    "UTBotIndicator",
    "EWOIndicator",
    "StochRSIIndicator",
    "HeikinAshiIndicator",
]
