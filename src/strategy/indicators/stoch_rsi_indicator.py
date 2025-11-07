from .rsi_indicator import RSIIndicator

class StochRSIIndicator:
    def __init__(self, rsi_period: int = 14, stoch_period: int = 14):
        self.rsi = RSIIndicator(rsi_period)
        self.stoch_period = int(stoch_period)
        self.rsi_values = []

    def add_price(self, price: float):
        self.rsi.add_data(price)
        v = self.rsi.value()
        if v is None:
            return None
        self.rsi_values.append(v)
        if len(self.rsi_values) < self.stoch_period:
            return None
        window = self.rsi_values[-self.stoch_period:]
        lo, hi = min(window), max(window)
        if hi - lo == 0:
            return 0.5
        return (v - lo) / (hi - lo)
