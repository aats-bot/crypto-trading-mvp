"""
Implementação do indicador ATR (Average True Range)
"""

import pandas as pd
import numpy as np
from .base_indicator import BaseIndicator

class ATR(BaseIndicator):
    """Average True Range"""
    
    def __init__(self, config):
        """
        Inicializa ATR
        
        Args:
            config: Dicionário com 'period' (período do ATR)
        """
        super().__init__(config)
        self.period = config.get('period', 14)
        
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        """
        Calcula ATR
        
        Args:
            data: DataFrame com dados OHLCV
            
        Returns:
            Série com valores do ATR
        """
        if not self.validate_data(data):
            raise ValueError("Dados inválidos para cálculo do ATR")
            
        # Calcular True Range
        high_low = data['high'] - data['low']
        high_close_prev = np.abs(data['high'] - data['close'].shift(1))
        low_close_prev = np.abs(data['low'] - data['close'].shift(1))
        
        true_range = pd.concat([high_low, high_close_prev, low_close_prev], axis=1).max(axis=1)
        
        # Calcular ATR como média móvel do True Range
        atr = true_range.rolling(window=self.period).mean()
        
        return atr

