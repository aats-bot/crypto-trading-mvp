from .base_indicator import BaseIndicator

class ATRIndicator(BaseIndicator):
    def __init__(self, period: int = 14):
        super().__init__(period)
        self.high = []
        self.low = []
        self.close = []
        self._atr = None

    def add_ohlc(self, high: float, low: float, close: float):
        self.high.append(float(high))
        self.low.append(float(low))
        self.close.append(float(close))
        self._recalc()

    def _recalc(self):
        n = len(self.close)
        if n < self.period + 1:
            self._atr = None
            return
        trs = []
        for i in range(1, n):
            tr = max(self.high[i]-self.low[i], abs(self.high[i]-self.close[i-1]), abs(self.low[i]-self.close[i-1]))
            trs.append(tr)
        self._atr = sum(trs[-self.period:]) / self.period

    def value(self):
        return self._atr
