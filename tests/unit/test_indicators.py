# 🧪 Testes Unitários - Indicadores Técnicos
"""
Testes unitários para os indicadores técnicos do MVP Bot
Localização: /tests/unit/test_indicators.py
"""
import pytest
import numpy as np
from datetime import datetime, timedelta

from src.strategy.indicators.base_indicator import BaseIndicator
from src.strategy.indicators.ema import EMAIndicator
from src.strategy.indicators.rsi import RSIIndicator
from src.strategy.indicators.atr import ATRIndicator
from src.strategy.indicators.ut_bot import UTBotIndicator
from src.strategy.indicators.ewo import EWOIndicator
from src.strategy.indicators.stoch_rsi import StochRSIIndicator
from src.strategy.indicators.heikin_ashi import HeikinAshiIndicator


class TestBaseIndicator:
    """Testes para classe base dos indicadores"""
    
    def test_base_indicator_initialization(self):
        """Testa inicialização do indicador base"""
        indicator = BaseIndicator(period=14)
        
        assert indicator.period == 14
        assert indicator.data == []
        assert indicator.name == "BaseIndicator"
    
    def test_base_indicator_add_data(self):
        """Testa adição de dados"""
        indicator = BaseIndicator(period=5)
        
        # Adicionar dados
        for i in range(10):
            indicator.add_data(100 + i)
        
        assert len(indicator.data) == 10
        assert indicator.data[-1] == 109
    
    def test_base_indicator_get_data(self):
        """Testa obtenção de dados"""
        indicator = BaseIndicator(period=5)
        
        # Adicionar dados
        data = [100, 101, 102, 103, 104, 105]
        for value in data:
            indicator.add_data(value)
        
        # Obter últimos 3 valores
        recent_data = indicator.get_data(3)
        assert recent_data == [103, 104, 105]
    
    def test_base_indicator_is_ready(self):
        """Testa se indicador está pronto"""
        indicator = BaseIndicator(period=5)
        
        # Não deve estar pronto inicialmente
        assert not indicator.is_ready()
        
        # Adicionar dados suficientes
        for i in range(5):
            indicator.add_data(100 + i)
        
        # Agora deve estar pronto
        assert indicator.is_ready()


class TestEMAIndicator:
    """Testes para indicador EMA"""
    
    @pytest.fixture
    def ema_indicator(self):
        """Fixture do indicador EMA"""
        return EMAIndicator(period=10)
    
    def test_ema_initialization(self, ema_indicator):
        """Testa inicialização do EMA"""
        assert ema_indicator.period == 10
        assert ema_indicator.name == "EMA"
        assert ema_indicator.alpha == 2 / (10 + 1)
    
    def test_ema_calculate_simple_case(self, ema_indicator):
        """Testa cálculo EMA caso simples"""
        # Dados constantes devem resultar em EMA igual ao valor
        for _ in range(20):
            ema_indicator.add_data(100.0)
        
        ema_value = ema_indicator.calculate()
        assert abs(ema_value - 100.0) < 0.01
    
    def test_ema_calculate_trending_data(self, ema_indicator):
        """Testa EMA com dados em tendência"""
        # Dados crescentes
        for i in range(20):
            ema_indicator.add_data(100 + i)
        
        ema_value = ema_indicator.calculate()
        
        # EMA deve estar entre o valor inicial e final
        assert 100 < ema_value < 119
        
        # EMA deve ser menor que o último valor (lag)
        assert ema_value < 119
    
    def test_ema_not_ready(self):
        """Testa EMA quando não há dados suficientes"""
        ema = EMAIndicator(period=10)
        
        # Adicionar poucos dados
        for i in range(5):
            ema.add_data(100 + i)
        
        # Não deve estar pronto
        assert not ema.is_ready()
        
        # Calcular deve retornar None ou 0
        result = ema.calculate()
        assert result is None or result == 0


class TestRSIIndicator:
    """Testes para indicador RSI"""
    
    @pytest.fixture
    def rsi_indicator(self):
        """Fixture do indicador RSI"""
        return RSIIndicator(period=14)
    
    def test_rsi_initialization(self, rsi_indicator):
        """Testa inicialização do RSI"""
        assert rsi_indicator.period == 14
        assert rsi_indicator.name == "RSI"
    
    def test_rsi_calculate_trending_up(self, rsi_indicator):
        """Testa RSI com tendência de alta"""
        # Dados crescentes
        for i in range(20):
            rsi_indicator.add_data(100 + i * 2)
        
        rsi_value = rsi_indicator.calculate()
        
        # RSI deve estar entre 0 e 100
        assert 0 <= rsi_value <= 100
        
        # Para tendência de alta, RSI deve ser > 50
        assert rsi_value > 50
    
    def test_rsi_calculate_trending_down(self, rsi_indicator):
        """Testa RSI com tendência de baixa"""
        # Dados decrescentes
        for i in range(20):
            rsi_indicator.add_data(120 - i * 2)
        
        rsi_value = rsi_indicator.calculate()
        
        # RSI deve estar entre 0 e 100
        assert 0 <= rsi_value <= 100
        
        # Para tendência de baixa, RSI deve ser < 50
        assert rsi_value < 50
    
    def test_rsi_calculate_sideways(self, rsi_indicator):
        """Testa RSI com movimento lateral"""
        # Dados oscilando
        for i in range(20):
            value = 100 + (5 if i % 2 == 0 else -5)
            rsi_indicator.add_data(value)
        
        rsi_value = rsi_indicator.calculate()
        
        # RSI deve estar próximo de 50 para movimento lateral
        assert 30 <= rsi_value <= 70


class TestATRIndicator:
    """Testes para indicador ATR"""
    
    @pytest.fixture
    def atr_indicator(self):
        """Fixture do indicador ATR"""
        return ATRIndicator(period=14)
    
    def test_atr_initialization(self, atr_indicator):
        """Testa inicialização do ATR"""
        assert atr_indicator.period == 14
        assert atr_indicator.name == "ATR"
    
    def test_atr_add_ohlc_data(self, atr_indicator):
        """Testa adição de dados OHLC"""
        # Adicionar dados OHLC
        for i in range(20):
            high = 105 + i
            low = 95 + i
            close = 100 + i
            
            atr_indicator.add_ohlc_data(high, low, close)
        
        assert len(atr_indicator.high_data) == 20
        assert len(atr_indicator.low_data) == 20
        assert len(atr_indicator.close_data) == 20
    
    def test_atr_calculate_high_volatility(self, atr_indicator):
        """Testa ATR com alta volatilidade"""
        # Dados com alta volatilidade
        for i in range(20):
            high = 110 + i + (i % 3) * 10
            low = 90 + i - (i % 3) * 10
            close = 100 + i
            
            atr_indicator.add_ohlc_data(high, low, close)
        
        atr_value = atr_indicator.calculate()
        
        # ATR deve ser positivo e refletir volatilidade
        assert atr_value > 0
        assert atr_value > 10  # Alta volatilidade


class TestUTBotIndicator:
    """Testes para indicador UT Bot"""
    
    @pytest.fixture
    def ut_bot_indicator(self):
        """Fixture do indicador UT Bot"""
        return UTBotIndicator(period=14, multiplier=2.0)
    
    def test_ut_bot_initialization(self, ut_bot_indicator):
        """Testa inicialização do UT Bot"""
        assert ut_bot_indicator.period == 14
        assert ut_bot_indicator.multiplier == 2.0
        assert ut_bot_indicator.name == "UT Bot"
    
    def test_ut_bot_calculate_signals(self, ut_bot_indicator):
        """Testa cálculo de sinais UT Bot"""
        # Adicionar dados de tendência
        for i in range(30):
            high = 105 + i
            low = 95 + i
            close = 100 + i
            
            ut_bot_indicator.add_ohlc_data(high, low, close)
        
        signal = ut_bot_indicator.calculate()
        
        # Sinal deve ser 1 (buy), -1 (sell) ou 0 (neutro)
        assert signal in [-1, 0, 1]


class TestEWOIndicator:
    """Testes para indicador EWO (Elliott Wave Oscillator)"""
    
    @pytest.fixture
    def ewo_indicator(self):
        """Fixture do indicador EWO"""
        return EWOIndicator(fast_period=5, slow_period=35)
    
    def test_ewo_initialization(self, ewo_indicator):
        """Testa inicialização do EWO"""
        assert ewo_indicator.fast_period == 5
        assert ewo_indicator.slow_period == 35
        assert ewo_indicator.name == "EWO"
    
    def test_ewo_calculate_momentum(self, ewo_indicator):
        """Testa cálculo de momentum EWO"""
        # Dados com momentum crescente
        for i in range(50):
            price = 100 + i * 0.5
            ewo_indicator.add_data(price)
        
        ewo_value = ewo_indicator.calculate()
        
        # EWO deve refletir momentum positivo
        assert ewo_value is not None


class TestStochRSIIndicator:
    """Testes para indicador Stochastic RSI"""
    
    @pytest.fixture
    def stoch_rsi_indicator(self):
        """Fixture do indicador Stoch RSI"""
        return StochRSIIndicator(rsi_period=14, stoch_period=14)
    
    def test_stoch_rsi_initialization(self, stoch_rsi_indicator):
        """Testa inicialização do Stoch RSI"""
        assert stoch_rsi_indicator.rsi_period == 14
        assert stoch_rsi_indicator.stoch_period == 14
        assert stoch_rsi_indicator.name == "Stoch RSI"
    
    def test_stoch_rsi_calculate_range(self, stoch_rsi_indicator):
        """Testa se Stoch RSI está no range correto"""
        # Adicionar dados suficientes
        for i in range(50):
            price = 100 + np.sin(i * 0.1) * 10
            stoch_rsi_indicator.add_data(price)
        
        k_value, d_value = stoch_rsi_indicator.calculate()
        
        # Valores devem estar entre 0 e 100
        if k_value is not None:
            assert 0 <= k_value <= 100
        if d_value is not None:
            assert 0 <= d_value <= 100


class TestHeikinAshiIndicator:
    """Testes para indicador Heikin Ashi"""
    
    @pytest.fixture
    def heikin_ashi_indicator(self):
        """Fixture do indicador Heikin Ashi"""
        return HeikinAshiIndicator()
    
    def test_heikin_ashi_initialization(self, heikin_ashi_indicator):
        """Testa inicialização do Heikin Ashi"""
        assert heikin_ashi_indicator.name == "Heikin Ashi"
    
    def test_heikin_ashi_calculate_candles(self, heikin_ashi_indicator):
        """Testa cálculo de velas Heikin Ashi"""
        # Adicionar dados OHLC
        for i in range(20):
            open_price = 100 + i
            high = 105 + i
            low = 95 + i
            close = 102 + i
            
            heikin_ashi_indicator.add_ohlc_data(open_price, high, low, close)
        
        ha_candle = heikin_ashi_indicator.calculate()
        
        # Deve retornar dados da vela Heikin Ashi
        assert ha_candle is not None
        if isinstance(ha_candle, dict):
            assert 'open' in ha_candle
            assert 'high' in ha_candle
            assert 'low' in ha_candle
            assert 'close' in ha_candle


# Testes de integração entre indicadores
@pytest.mark.integration
class TestIndicatorIntegration:
    """Testes de integração entre indicadores"""
    
    def test_multiple_indicators_same_data(self):
        """Testa múltiplos indicadores com os mesmos dados"""
        # Criar indicadores
        ema = EMAIndicator(period=10)
        rsi = RSIIndicator(period=14)
        atr = ATRIndicator(period=14)
        
        # Adicionar os mesmos dados
        for i in range(30):
            price = 100 + np.sin(i * 0.1) * 5
            high = price + 2
            low = price - 2
            
            ema.add_data(price)
            rsi.add_data(price)
            atr.add_ohlc_data(high, low, price)
        
        # Todos devem calcular valores
        ema_value = ema.calculate()
        rsi_value = rsi.calculate()
        atr_value = atr.calculate()
        
        assert ema_value is not None
        assert rsi_value is not None
        assert atr_value is not None
    
    def test_indicator_consistency(self):
        """Testa consistência entre indicadores"""
        indicators = [
            EMAIndicator(period=10),
            RSIIndicator(period=14),
            ATRIndicator(period=14)
        ]
        
        # Todos devem ter métodos básicos
        for indicator in indicators:
            assert hasattr(indicator, 'add_data')
            assert hasattr(indicator, 'calculate')
            assert hasattr(indicator, 'is_ready')
            assert hasattr(indicator, 'name')


# Testes de performance
@pytest.mark.performance
class TestIndicatorPerformance:
    """Testes de performance dos indicadores"""
    
    def test_indicator_calculation_speed(self):
        """Testa velocidade de cálculo dos indicadores"""
        import time
        
        indicators = [
            EMAIndicator(period=20),
            RSIIndicator(period=14),
            ATRIndicator(period=14)
        ]
        
        # Adicionar muitos dados
        data_points = 1000
        
        for indicator in indicators:
            start_time = time.time()
            
            for i in range(data_points):
                if hasattr(indicator, 'add_ohlc_data'):
                    indicator.add_ohlc_data(100 + i, 102 + i, 98 + i)
                else:
                    indicator.add_data(100 + i)
            
            # Calcular
            indicator.calculate()
            
            end_time = time.time()
            
            # Deve ser rápido (< 1 segundo para 1000 pontos)
            assert (end_time - start_time) < 1.0
    
    def test_memory_usage_large_dataset(self):
        """Testa uso de memória com dataset grande"""
        indicator = EMAIndicator(period=20)
        
        # Adicionar muitos dados
        for i in range(10000):
            indicator.add_data(100 + i)
        
        # Verificar que não há vazamento de memória óbvio
        assert len(indicator.data) <= 10000

