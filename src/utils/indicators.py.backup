"""
Crypto Trading MVP - Indicadores Técnicos Simples
Implementação básica usando apenas pandas e numpy
"""

import pandas as pd
import numpy as np
from typing import Union

def simple_moving_average(data: Union[pd.Series, list], period: int = 20):
    """Média móvel simples"""
    if isinstance(data, list):
        data = pd.Series(data)
    return data.rolling(window=period).mean()

def exponential_moving_average(data: Union[pd.Series, list], period: int = 20):
    """Média móvel exponencial"""
    if isinstance(data, list):
        data = pd.Series(data)
    return data.ewm(span=period).mean()

def relative_strength_index(data: Union[pd.Series, list], period: int = 14):
    """Índice de força relativa"""
    if isinstance(data, list):
        data = pd.Series(data)
ECHO est� desativado.
    delta = data.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
ECHO est� desativado.
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# Aliases para compatibilidade
SMA = simple_moving_average
EMA = exponential_moving_average
RSI = relative_strength_index
