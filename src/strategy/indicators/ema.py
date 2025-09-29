"""
Implementação do indicador EMA (Exponential Moving Average)
"""

import pandas as pd
import numpy as np
from .base_indicator import BaseIndicator

class EMA(BaseIndicator):
    """Exponential Moving Average"""
    
    def __init__(self, config):
        """
        Inicializa EMA
        
        Args:
            config: Dicionário com 'period' (período da EMA)
        """
        super().__init__(config)
        self.period = config.get('period', 20)
        
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        """
        Calcula EMA
        
        Args:
            data: DataFrame com dados OHLCV
            
        Returns:
            Série com valores da EMA
        """
        if not self.validate_data(data):
            raise ValueError("Dados inválidos para cálculo da EMA")
            
        return data['close'].ewm(span=self.period, adjust=False).mean()

class EMA100(EMA):
    """EMA de 100 períodos para filtro de tendência"""
    
    def __init__(self, config):
        config['period'] = 100
        super().__init__(config)

class EMA20(EMA):
    """EMA de 20 períodos para validação multi-timeframe"""
    
    def __init__(self, config):
        config['period'] = 20
        super().__init__(config)

