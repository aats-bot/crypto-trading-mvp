from .ema_indicator import EMAIndicator

class EWOIndicator:
    def __init__(self, fast_period: int = 5, slow_period: int = 35):
        self.fast = EMAIndicator(fast_period)
        self.slow = EMAIndicator(slow_period)
        self._value = None

    def add_price(self, price: float):
        f = self.fast.add_data(price)
        s = self.slow.add_data(price)
        if f is None or s is None:
            self._value = None
        else:
            self._value = f - s
        return self._value

    def value(self):
        return self._value
