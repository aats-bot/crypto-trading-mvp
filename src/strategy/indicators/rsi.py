"""
Implementação do indicador RSI (Relative Strength Index)
"""

import pandas as pd
import numpy as np
from .base_indicator import BaseIndicator

class RSI(BaseIndicator):
    """Relative Strength Index"""
    
    def __init__(self, config):
        """
        Inicializa RSI
        
        Args:
            config: Dicionário com 'period' (período do RSI)
        """
        super().__init__(config)
        self.period = config.get('period', 14)
        
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        """
        Calcula RSI
        
        Args:
            data: DataFrame com dados OHLCV
            
        Returns:
            Série com valores do RSI
        """
        if not self.validate_data(data):
            raise ValueError("Dados inválidos para cálculo do RSI")
            
        # Calcular mudanças de preço
        delta = data['close'].diff()
        
        # Separar ganhos e perdas
        gains = delta.where(delta > 0, 0)
        losses = -delta.where(delta < 0, 0)
        
        # Calcular médias móveis dos ganhos e perdas
        avg_gains = gains.rolling(window=self.period).mean()
        avg_losses = losses.rolling(window=self.period).mean()
        
        # Calcular RS e RSI
        rs = avg_gains / avg_losses
        rsi = 100 - (100 / (1 + rs))
        
        return rsi

