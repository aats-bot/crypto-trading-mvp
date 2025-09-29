"""
Crypto Trading MVP - Indicadores TÃ©cnicos Simples
ImplementaÃ§Ã£o bÃ¡sica de indicadores usando apenas pandas e numpy
"""

import pandas as pd
import numpy as np
from typing import Union, Optional

class SimpleIndicators:
    """Indicadores tÃ©cnicos simples usando apenas pandas/numpy"""
ECHO est  desativado.
    @staticmethod
    def sma(data: Union[pd.Series, np.ndarray], period: int = 20) -> pd.Series:
        """Simple Moving Average"""
        if isinstance(data, np.ndarray):
            data = pd.Series(data)
        return data.rolling(window=period).mean()
ECHO est  desativado.
    @staticmethod
    def ema(data: Union[pd.Series, np.ndarray], period: int = 20) -> pd.Series:
        """Exponential Moving Average"""
        if isinstance(data, np.ndarray):
            data = pd.Series(data)
        return data.ewm(span=period).mean()
ECHO est  desativado.
    @staticmethod
    def rsi(data: Union[pd.Series, np.ndarray], period: int = 14) -> pd.Series:
        """Relative Strength Index"""
        if isinstance(data, np.ndarray):
            data = pd.Series(data)
ECHO est  desativado.
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
ECHO est  desativado.
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
ECHO est  desativado.
    @staticmethod
    def bollinger_bands(data: Union[pd.Series, np.ndarray], period: int = 20, std_dev: float = 2) -> pd.DataFrame:
        """Bollinger Bands"""
        if isinstance(data, np.ndarray):
            data = pd.Series(data)
ECHO est  desativado.
        sma = data.rolling(window=period).mean()
        std = data.rolling(window=period).std()
ECHO est  desativado.
        upper = sma + (std * std_dev)
        lower = sma - (std * std_dev)
ECHO est  desativado.
        return pd.DataFrame({
            'upper': upper,
            'middle': sma,
            'lower': lower
        })
ECHO est  desativado.
    @staticmethod
    def macd(data: Union[pd.Series, np.ndarray], fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
        """MACD Indicator"""
        if isinstance(data, np.ndarray):
            data = pd.Series(data)
ECHO est  desativado.
        ema_fast = data.ewm(span=fast).mean()
        ema_slow = data.ewm(span=slow).mean()
ECHO est  desativado.
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal).mean()
        histogram = macd_line - signal_line
ECHO est  desativado.
        return pd.DataFrame({
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        })

# Aliases para compatibilidade
def SMA(data, timeperiod=20):
    return SimpleIndicators.sma(data, timeperiod)

def EMA(data, timeperiod=20):
    return SimpleIndicators.ema(data, timeperiod)

def RSI(data, timeperiod=14):
    return SimpleIndicators.rsi(data, timeperiod)

def MACD(data, fastperiod=12, slowperiod=26, signalperiod=9):
    result = SimpleIndicators.macd(data, fastperiod, slowperiod, signalperiod)
    return result['macd'], result['signal'], result['histogram']

def BBANDS(data, timeperiod=20, nbdevup=2, nbdevdn=2):
    result = SimpleIndicators.bollinger_bands(data, timeperiod, nbdevup)
    return result['upper'], result['middle'], result['lower']
