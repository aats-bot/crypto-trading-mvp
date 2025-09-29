"""
Implementação do indicador UT Bot (baseado em ATR)
"""

import pandas as pd
import numpy as np
from .base_indicator import BaseIndicator
from .atr import ATR

class UTBot(BaseIndicator):
    """UT Bot Indicator (ATR-based trend following)"""
    
    def __init__(self, config):
        """
        Inicializa UT Bot
        
        Args:
            config: Dicionário com 'atr_period' e 'atr_multiplier'
        """
        super().__init__(config)
        self.atr_period = config.get('atr_period', 10)
        self.atr_multiplier = config.get('atr_multiplier', 3.0)
        
        # Inicializar ATR
        atr_config = {'period': self.atr_period}
        self.atr = ATR(atr_config)
        
    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula UT Bot
        
        Args:
            data: DataFrame com dados OHLCV
            
        Returns:
            DataFrame com colunas 'ut_upper', 'ut_lower', 'ut_signal'
        """
        if not self.validate_data(data):
            raise ValueError("Dados inválidos para cálculo do UT Bot")
            
        # Calcular ATR
        atr_values = self.atr.calculate(data)
        
        # Calcular HL2 (média de high e low)
        hl2 = (data['high'] + data['low']) / 2
        
        # Calcular bandas UT
        ut_upper = hl2 - (self.atr_multiplier * atr_values)
        ut_lower = hl2 + (self.atr_multiplier * atr_values)
        
        # Inicializar arrays para trailing stops
        ut_final_upper = pd.Series(index=data.index, dtype=float)
        ut_final_lower = pd.Series(index=data.index, dtype=float)
        ut_signal = pd.Series(index=data.index, dtype=int)
        
        # Calcular trailing stops
        for i in range(len(data)):
            if i == 0:
                ut_final_upper.iloc[i] = ut_upper.iloc[i]
                ut_final_lower.iloc[i] = ut_lower.iloc[i]
                ut_signal.iloc[i] = 1  # Iniciar com sinal de compra
            else:
                # Upper trailing stop
                if ut_upper.iloc[i] < ut_final_upper.iloc[i-1] or data['close'].iloc[i-1] > ut_final_upper.iloc[i-1]:
                    ut_final_upper.iloc[i] = ut_upper.iloc[i]
                else:
                    ut_final_upper.iloc[i] = ut_final_upper.iloc[i-1]
                
                # Lower trailing stop
                if ut_lower.iloc[i] > ut_final_lower.iloc[i-1] or data['close'].iloc[i-1] < ut_final_lower.iloc[i-1]:
                    ut_final_lower.iloc[i] = ut_lower.iloc[i]
                else:
                    ut_final_lower.iloc[i] = ut_final_lower.iloc[i-1]
                
                # Determinar sinal
                if data['close'].iloc[i] <= ut_final_lower.iloc[i]:
                    ut_signal.iloc[i] = 1  # Sinal de compra
                elif data['close'].iloc[i] >= ut_final_upper.iloc[i]:
                    ut_signal.iloc[i] = -1  # Sinal de venda
                else:
                    ut_signal.iloc[i] = ut_signal.iloc[i-1]  # Manter sinal anterior
        
        result = pd.DataFrame({
            'ut_upper': ut_final_upper,
            'ut_lower': ut_final_lower,
            'ut_signal': ut_signal
        }, index=data.index)
        
        return result
    
    def get_signal(self, data: pd.DataFrame) -> int:
        """
        Obtém o sinal atual do UT Bot
        
        Args:
            data: DataFrame com dados OHLCV
            
        Returns:
            1 para compra, -1 para venda, 0 para neutro
        """
        ut_data = self.calculate(data)
        if len(ut_data) > 0:
            return ut_data['ut_signal'].iloc[-1]
        return 0

