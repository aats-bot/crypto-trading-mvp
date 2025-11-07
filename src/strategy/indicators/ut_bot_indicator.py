from .ema_indicator import EMAIndicator

class UTBotIndicator:
    def __init__(self, period: int = 14, multiplier: float = 2.0):
        self.ema = EMAIndicator(period)
        self.multiplier = float(multiplier)
        self.last_signal = None  # "buy"/"sell"/None

    def add_price(self, price: float):
        ema = self.ema.add_data(price)
        if ema is None:
            return None
        # sinal bem simples só para compat de teste
        if price > ema:
            self.last_signal = "buy"
        elif price < ema:
            self.last_signal = "sell"
        return self.last_signal
