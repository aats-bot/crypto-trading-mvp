"""
Implementação do indicador Heikin Ashi
Suaviza a tendência removendo ruído dos candles tradicionais
"""

import pandas as pd
import numpy as np
from .base_indicator import BaseIndicator

class HeikinAshi(BaseIndicator):
    """
    Indicador Heikin Ashi
    
    Transforma candles tradicionais em candles suavizados
    que facilitam a identificação de tendências
    """
    
    def __init__(self, config):
        super().__init__(config)
        self.name = "heikin_ashi"
    
    def calculate(self, df):
        """
        Calcula candles Heikin Ashi
        
        Args:
            df: DataFrame com colunas OHLCV
            
        Returns:
            DataFrame com candles Heikin Ashi
        """
        if len(df) < 2:
            return None
        
        # Criar cópia para evitar modificar original
        ha_data = df.copy()
        
        # Inicializar colunas Heikin Ashi
        ha_data['ha_close'] = 0.0
        ha_data['ha_open'] = 0.0
        ha_data['ha_high'] = 0.0
        ha_data['ha_low'] = 0.0
        
        # Calcular primeiro candle
        ha_data.loc[0, 'ha_close'] = (df.iloc[0]['open'] + df.iloc[0]['high'] + 
                                     df.iloc[0]['low'] + df.iloc[0]['close']) / 4
        ha_data.loc[0, 'ha_open'] = (df.iloc[0]['open'] + df.iloc[0]['close']) / 2
        ha_data.loc[0, 'ha_high'] = df.iloc[0]['high']
        ha_data.loc[0, 'ha_low'] = df.iloc[0]['low']
        
        # Calcular valores subsequentes usando .loc para evitar warning
        for i in range(1, len(df)):
            # HA Close
            ha_data.loc[i, 'ha_close'] = (df.iloc[i]['open'] + df.iloc[i]['high'] + 
                                         df.iloc[i]['low'] + df.iloc[i]['close']) / 4
            
            # HA Open - CORRIGIDO: usar .loc em vez de .iloc para assignment
            ha_data.loc[i, 'ha_open'] = (ha_data.loc[i-1, 'ha_open'] + 
                                        ha_data.loc[i-1, 'ha_close']) / 2
            
            # HA High
            ha_data.loc[i, 'ha_high'] = max(df.iloc[i]['high'], 
                                           ha_data.loc[i, 'ha_open'], 
                                           ha_data.loc[i, 'ha_close'])
            
            # HA Low
            ha_data.loc[i, 'ha_low'] = min(df.iloc[i]['low'], 
                                          ha_data.loc[i, 'ha_open'], 
                                          ha_data.loc[i, 'ha_close'])
        
        return ha_data
    
    def get_signal(self, df):
        """
        Gera sinal baseado na cor dos candles Heikin Ashi
        
        Returns:
            1: Tendência de alta (candle verde)
            -1: Tendência de baixa (candle vermelho)
            0: Indeciso
        """
        ha_data = self.calculate(df)
        
        if ha_data is None or len(ha_data) < 2:
            return 0
        
        # Últimos 2 candles
        current = ha_data.iloc[-1]
        previous = ha_data.iloc[-2]
        
        # Determinar cor do candle atual
        current_bullish = current['ha_close'] > current['ha_open']
        previous_bullish = previous['ha_close'] > previous['ha_open']
        
        # Sinal baseado na sequência de candles
        if current_bullish and previous_bullish:
            return 1  # Tendência de alta forte
        elif not current_bullish and not previous_bullish:
            return -1  # Tendência de baixa forte
        else:
            return 0  # Indeciso ou mudança de tendência
    
    def get_trend_signal(self, df):
        """
        Método adicional para compatibilidade com indicator_manager
        Retorna o mesmo que get_signal()
        """
        return self.get_signal(df)

