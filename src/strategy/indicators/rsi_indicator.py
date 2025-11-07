from .base_indicator import BaseIndicator

class RSIIndicator(BaseIndicator):
    def value(self):
        if len(self.data) < self.period + 1:
            return None
        gains = []
        losses = []
        for i in range(-self.period, 0):
            diff = self.data[i] - self.data[i-1]
            gains.append(max(diff, 0.0))
            losses.append(max(-diff, 0.0))
        avg_gain = (sum(gains) / self.period) or 0.0
        avg_loss = (sum(losses) / self.period) or 0.0
        if avg_loss == 0:
            return 100.0
        rs = avg_gain / avg_loss
        return 100.0 - (100.0 / (1.0 + rs))
