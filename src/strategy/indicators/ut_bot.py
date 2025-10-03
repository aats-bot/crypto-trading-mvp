from __future__ import annotations
import pandas as pd

class UTBotIndicator:
    """
    Implementação simples de um 'UT Bot'-like:
    - Calcula ATR (Wilder) com janela padrão 14
    - Gera bandas superior/inferior: close +/- factor * ATR
    - Sinal de compra quando close cruza acima da banda sup.
    - Sinal de venda quando close cruza abaixo da banda inf.
    """
    def __init__(self, high: pd.Series, low: pd.Series, close: pd.Series,
                 atr_period: int = 14, factor: float = 1.5):
        self.high = high
        self.low = low
        self.close = close
        self.atr_period = atr_period
        self.factor = factor

    def _atr(self) -> pd.Series:
        prev_close = self.close.shift(1)
        tr1 = self.high - self.low
        tr2 = (self.high - prev_close).abs()
        tr3 = (self.low - prev_close).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        # Wilder smoothing = EMA com alpha=1/period e adjust=False
        return tr.ewm(alpha=1/self.atr_period, adjust=False).mean()

    def bands(self) -> tuple[pd.Series, pd.Series]:
        atr = self._atr()
        upper = self.close + self.factor * atr
        lower = self.close - self.factor * atr
        return upper, lower

    def signals(self) -> pd.DataFrame:
        upper, lower = self.bands()
        above = self.close > upper
        below = self.close < lower
        buy = (~above.shift(1).fillna(False)) & above
        sell = (~below.shift(1).fillna(False)) & below
        return pd.DataFrame({"buy": buy, "sell": sell})

    # alguns testes usam .calculate()
    def calculate(self) -> pd.DataFrame:
        return self.signals()
