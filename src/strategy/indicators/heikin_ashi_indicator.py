class HeikinAshiIndicator:
    def __init__(self):
        self.ohlc = []  # list of dicts: {open, high, low, close}

    def add_ohlc(self, open: float, high: float, low: float, close: float):
        self.ohlc.append({"open": float(open), "high": float(high), "low": float(low), "close": float(close)})

    def calculate_candles(self):
        if not self.ohlc:
            return []
        ha = []
        prev_ha_open = self.ohlc[0]["open"]
        prev_ha_close = self.ohlc[0]["close"]
        for i, c in enumerate(self.ohlc):
            ha_close = (c["open"] + c["high"] + c["low"] + c["close"]) / 4.0
            ha_open = (prev_ha_open + prev_ha_close) / 2.0 if i > 0 else (c["open"] + c["close"]) / 2.0
            ha_high = max(c["high"], ha_open, ha_close)
            ha_low  = min(c["low"], ha_open, ha_close)
            ha.append({"open": ha_open, "high": ha_high, "low": ha_low, "close": ha_close})
            prev_ha_open, prev_ha_close = ha_open, ha_close
        return ha
