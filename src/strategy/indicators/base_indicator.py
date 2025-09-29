"""
Classe base para indicadores técnicos
"""

import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseIndicator(ABC):
    """Classe base para todos os indicadores técnicos"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa o indicador
        
        Args:
            config: Configurações do indicador
        """
        self.config = config
        self.name = self.__class__.__name__
        
    @abstractmethod
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        """
        Calcula o indicador
        
        Args:
            data: DataFrame com dados OHLCV
            
        Returns:
            Série com valores do indicador
        """
        pass
    
    def validate_data(self, data: pd.DataFrame) -> bool:
        """
        Valida se os dados são adequados para o cálculo
        
        Args:
            data: DataFrame com dados OHLCV
            
        Returns:
            True se os dados são válidos
        """
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        return all(col in data.columns for col in required_columns)
    
    def prepare_data(self, kline_data: List[List]) -> pd.DataFrame:
        """
        Converte dados de kline da API em DataFrame - VERSÃO CORRIGIDA
        
        Args:
            kline_data: Lista de dados de kline da API Bybit
            
        Returns:
            DataFrame formatado
        """
        try:
            if not kline_data:
                return pd.DataFrame()
            
            # Verificar quantas colunas temos
            num_columns = len(kline_data[0]) if kline_data else 0
            
            # Definir colunas baseado no número de dados recebidos
            if num_columns == 6:
                # Formato: timestamp, open, high, low, close, volume
                columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
                numeric_columns = ['open', 'high', 'low', 'close', 'volume']
            elif num_columns == 7:
                # Formato: timestamp, open, high, low, close, volume, turnover
                columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'turnover']
                numeric_columns = ['open', 'high', 'low', 'close', 'volume', 'turnover']
            elif num_columns == 8:
                # Formato com campo adicional
                columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'turnover', 'extra']
                numeric_columns = ['open', 'high', 'low', 'close', 'volume', 'turnover']
            else:
                # Fallback: usar apenas as primeiras 6 colunas essenciais
                columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
                numeric_columns = ['open', 'high', 'low', 'close', 'volume']
                # Truncar dados para 6 colunas
                kline_data = [row[:6] for row in kline_data]
            
            # Criar DataFrame
            df = pd.DataFrame(kline_data, columns=columns)
            
            # Converter para tipos numéricos
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Converter timestamp
            df['timestamp'] = pd.to_datetime(df['timestamp'].astype(int), unit='ms')
            df.set_index('timestamp', inplace=True)
            
            # Ordenar por timestamp (mais antigo primeiro)
            df.sort_index(inplace=True)
            
            # Remover linhas com valores NaN
            df.dropna(inplace=True)
            
            return df
            
        except Exception as e:
            print(f"Erro ao preparar dados: {e}")
            return pd.DataFrame()

