from .base_indicator import BaseIndicator

class EMAIndicator(BaseIndicator):
    def __init__(self, period: int = 14):
        super().__init__(period)
        self._ema = None

    def add_data(self, price: float):
        super().add_data(price)
        k = 2 / (self.period + 1)
        self._ema = price if self._ema is None else (price - self._ema) * k + self._ema
        return self._ema

    def value(self):
        return self._ema
