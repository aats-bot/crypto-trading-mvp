"""
Implementação do indicador Stochastic RSI
"""

import pandas as pd
import numpy as np
from .base_indicator import BaseIndicator
from .rsi import RSI

class StochRSI(BaseIndicator):
    """Stochastic RSI"""
    
    def __init__(self, config):
        """
        Inicializa Stochastic RSI
        
        Args:
            config: Dicionário com 'rsi_period', 'stoch_period', 'k_period', 'd_period'
        """
        super().__init__(config)
        self.rsi_period = config.get('rsi_period', 14)
        self.stoch_period = config.get('stoch_period', 14)
        self.k_period = config.get('k_period', 3)
        self.d_period = config.get('d_period', 3)
        
        # Inicializar RSI
        rsi_config = {'period': self.rsi_period}
        self.rsi = RSI(rsi_config)
        
    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula Stochastic RSI
        
        Args:
            data: DataFrame com dados OHLCV
            
        Returns:
            DataFrame com colunas 'stoch_rsi_k' e 'stoch_rsi_d'
        """
        if not self.validate_data(data):
            raise ValueError("Dados inválidos para cálculo do Stochastic RSI")
            
        # Calcular RSI
        rsi_values = self.rsi.calculate(data)
        
        # Calcular Stochastic do RSI
        rsi_min = rsi_values.rolling(window=self.stoch_period).min()
        rsi_max = rsi_values.rolling(window=self.stoch_period).max()
        
        stoch_rsi = (rsi_values - rsi_min) / (rsi_max - rsi_min) * 100
        
        # Calcular %K e %D
        stoch_rsi_k = stoch_rsi.rolling(window=self.k_period).mean()
        stoch_rsi_d = stoch_rsi_k.rolling(window=self.d_period).mean()
        
        result = pd.DataFrame({
            'stoch_rsi_k': stoch_rsi_k,
            'stoch_rsi_d': stoch_rsi_d
        }, index=data.index)
        
        return result
    
    def get_reversal_signal(self, data: pd.DataFrame, 
                           oversold_level: float = 20, 
                           overbought_level: float = 80) -> int:
        """
        Obtém sinal de reversão baseado no Stochastic RSI
        
        Args:
            data: DataFrame com dados OHLCV
            oversold_level: Nível de sobrevenda
            overbought_level: Nível de sobrecompra
            
        Returns:
            1 para sinal de compra (reversão de sobrevenda)
            -1 para sinal de venda (reversão de sobrecompra)
            0 para neutro
        """
        stoch_data = self.calculate(data)
        if len(stoch_data) < 2:
            return 0
            
        current_k = stoch_data['stoch_rsi_k'].iloc[-1]
        current_d = stoch_data['stoch_rsi_d'].iloc[-1]
        prev_k = stoch_data['stoch_rsi_k'].iloc[-2]
        prev_d = stoch_data['stoch_rsi_d'].iloc[-2]
        
        # Sinal de compra: cruzamento para cima em área de sobrevenda
        if (current_k > current_d and prev_k <= prev_d and 
            current_k < oversold_level):
            return 1
            
        # Sinal de venda: cruzamento para baixo em área de sobrecompra
        if (current_k < current_d and prev_k >= prev_d and 
            current_k > overbought_level):
            return -1
            
        return 0

