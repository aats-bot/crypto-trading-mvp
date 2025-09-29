"""
Implementação do indicador EWO (Elliott Wave Oscillator)
"""

import pandas as pd
import numpy as np
from .base_indicator import BaseIndicator

class EWO(BaseIndicator):
    """Elliott Wave Oscillator (momentum indicator)"""
    
    def __init__(self, config):
        """
        Inicializa EWO
        
        Args:
            config: Dicionário com 'fast_period' e 'slow_period'
        """
        super().__init__(config)
        self.fast_period = config.get('fast_period', 5)
        self.slow_period = config.get('slow_period', 35)
        
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        """
        Calcula EWO
        
        Args:
            data: DataFrame com dados OHLCV
            
        Returns:
            Série com valores do EWO
        """
        if not self.validate_data(data):
            raise ValueError("Dados inválidos para cálculo do EWO")
            
        # Calcular SMAs
        sma_fast = data['close'].rolling(window=self.fast_period).mean()
        sma_slow = data['close'].rolling(window=self.slow_period).mean()
        
        # EWO = SMA_fast - SMA_slow
        ewo = sma_fast - sma_slow
        
        return ewo
    
    def get_momentum_signal(self, data: pd.DataFrame, threshold: float = 0.0) -> int:
        """
        Obtém sinal de momentum baseado no EWO
        
        Args:
            data: DataFrame com dados OHLCV
            threshold: Limiar para determinar sinal
            
        Returns:
            1 para momentum positivo, -1 para negativo, 0 para neutro
        """
        ewo_values = self.calculate(data)
        if len(ewo_values) > 0:
            current_ewo = ewo_values.iloc[-1]
            if current_ewo > threshold:
                return 1
            elif current_ewo < -threshold:
                return -1
        return 0

