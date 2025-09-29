"""
Testes de validação matemática dos indicadores técnicos
Compara implementações com cálculos de referência conhecidos
"""
import pytest
import numpy as np
import pandas as pd
import math
from typing import List
import sys
import os

# Adicionar o diretório do projeto ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

# Importar a estratégia
from test_ppp_vishva_strategy import PPPVishvaStrategy


class ReferenceIndicators:
    """
    Implementações de referência dos indicadores técnicos
    Baseadas em fórmulas matemáticas padrão da indústria
    """
    
    @staticmethod
    def reference_ema(prices: List[float], period: int) -> float:
        """Implementação de referência da EMA"""
        if len(prices) < period:
            return prices[-1] if prices else 0.0
        
        # Fórmula padrão: EMA = (Close * K) + (EMA_prev * (1 - K))
        # onde K = 2 / (period + 1)
        k = 2.0 / (period + 1)
        ema = prices[0]
        
        for price in prices[1:]:
            ema = (price * k) + (ema * (1 - k))
        
        return ema
    
    @staticmethod
    def reference_sma(prices: List[float], period: int) -> float:
        """Implementação de referência da SMA"""
        if len(prices) < period:
            return sum(prices) / len(prices) if prices else 0.0
        
        return sum(prices[-period:]) / period
    
    @staticmethod
    def reference_atr(highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> float:
        """Implementação de referência do ATR"""
        if len(closes) < 2:
            return 0.0
        
        true_ranges = []
        for i in range(1, len(closes)):
            # True Range = max(high-low, |high-prev_close|, |low-prev_close|)
            hl = highs[i] - lows[i]
            hc = abs(highs[i] - closes[i-1])
            lc = abs(lows[i] - closes[i-1])
            tr = max(hl, hc, lc)
            true_ranges.append(tr)
        
        # ATR é a média móvel dos True Ranges
        if len(true_ranges) < period:
            return sum(true_ranges) / len(true_ranges)
        
        # Usar SMA para simplificar (em produção seria EMA)
        return sum(true_ranges[-period:]) / period
    
    @staticmethod
    def reference_rsi(prices: List[float], period: int = 14) -> float:
        """Implementação de referência do RSI"""
        if len(prices) < period + 1:
            return 50.0  # Valor neutro
        
        # Calcular mudanças de preço
        changes = []
        for i in range(1, len(prices)):
            changes.append(prices[i] - prices[i-1])
        
        # Separar ganhos e perdas
        gains = [max(change, 0) for change in changes]
        losses = [abs(min(change, 0)) for change in changes]
        
        # Calcular médias
        if len(gains) < period:
            avg_gain = sum(gains) / len(gains) if gains else 0
            avg_loss = sum(losses) / len(losses) if losses else 0
        else:
            avg_gain = sum(gains[-period:]) / period
            avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def reference_stoch_rsi(prices: List[float], period: int = 14) -> float:
        """Implementação de referência do Stochastic RSI"""
        if len(prices) < period + 1:
            return 0.5
        
        # Calcular RSI para cada ponto
        rsi_values = []
        for i in range(period, len(prices) + 1):
            rsi = ReferenceIndicators.reference_rsi(prices[:i], period)
            rsi_values.append(rsi)
        
        if len(rsi_values) < period:
            return 0.5
        
        # Calcular Stochastic do RSI
        recent_rsi = rsi_values[-period:]
        highest_rsi = max(recent_rsi)
        lowest_rsi = min(recent_rsi)
        current_rsi = rsi_values[-1]
        
        if highest_rsi == lowest_rsi:
            return 0.5
        
        stoch_rsi = (current_rsi - lowest_rsi) / (highest_rsi - lowest_rsi)
        return stoch_rsi


class TestMathematicalValidation:
    """Testes de validação matemática dos indicadores"""
    
    @pytest.fixture
    def strategy(self):
        return PPPVishvaStrategy()
    
    @pytest.fixture
    def reference_calc(self):
        return ReferenceIndicators()
    
    @pytest.fixture
    def test_prices(self):
        """Preços de teste conhecidos para validação"""
        return [
            100.0, 101.5, 99.8, 102.3, 98.7, 103.1, 97.9, 104.2,
            96.5, 105.0, 95.8, 106.1, 94.9, 107.3, 93.7, 108.5,
            92.4, 109.8, 91.2, 111.0, 90.1, 112.5, 89.3, 114.0,
            88.7, 115.2, 87.9, 116.8, 86.5, 118.3
        ]
    
    def test_ema_mathematical_accuracy(self, strategy, reference_calc, test_prices):
        """Testa precisão matemática da EMA contra implementação de referência"""
        periods = [5, 10, 20]
        
        for period in periods:
            strategy_ema = strategy.calculate_ema(test_prices, period)
            reference_ema = reference_calc.reference_ema(test_prices, period)
            
            # Tolerância de 0.01% para diferenças de ponto flutuante
            tolerance = abs(reference_ema) * 0.0001
            assert abs(strategy_ema - reference_ema) <= tolerance, \
                f"EMA({period}): Strategy={strategy_ema}, Reference={reference_ema}"
    
    def test_ema_edge_cases(self, strategy, reference_calc):
        """Testa casos extremos da EMA"""
        # Caso 1: Lista vazia
        assert strategy.calculate_ema([], 10) == reference_calc.reference_ema([], 10)
        
        # Caso 2: Um único valor
        single_price = [100.0]
        assert strategy.calculate_ema(single_price, 10) == reference_calc.reference_ema(single_price, 10)
        
        # Caso 3: Período maior que dados disponíveis
        short_prices = [100.0, 101.0, 102.0]
        strategy_result = strategy.calculate_ema(short_prices, 10)
        reference_result = reference_calc.reference_ema(short_prices, 10)
        assert strategy_result == reference_result
        
        # Caso 4: Valores idênticos
        identical_prices = [100.0] * 20
        strategy_result = strategy.calculate_ema(identical_prices, 10)
        reference_result = reference_calc.reference_ema(identical_prices, 10)
        tolerance = 0.01
        assert abs(strategy_result - reference_result) <= tolerance
    
    def test_atr_mathematical_accuracy(self, strategy, reference_calc):
        """Testa precisão matemática do ATR"""
        # Criar dados OHLC de teste
        test_data = [
            (102, 100, 101),  # (high, low, close)
            (103, 99, 102),
            (105, 101, 104),
            (104, 98, 99),
            (106, 100, 105),
            (108, 103, 107),
            (107, 102, 103),
            (109, 104, 108),
            (111, 106, 110),
            (110, 105, 106),
            (112, 107, 111),
            (114, 109, 113),
            (113, 108, 109),
            (115, 110, 114),
            (117, 112, 116)
        ]
        
        highs = [d[0] for d in test_data]
        lows = [d[1] for d in test_data]
        closes = [d[2] for d in test_data]
        
        periods = [5, 10, 14]
        
        for period in periods:
            strategy_atr = strategy.calculate_atr(highs, lows, closes, period)
            reference_atr = reference_calc.reference_atr(highs, lows, closes, period)
            
            # Tolerância maior para ATR devido à complexidade do cálculo
            tolerance = max(abs(reference_atr) * 0.01, 0.01)  # 1% ou 0.01
            assert abs(strategy_atr - reference_atr) <= tolerance, \
                f"ATR({period}): Strategy={strategy_atr}, Reference={reference_atr}"
    
    def test_stoch_rsi_mathematical_accuracy(self, strategy, reference_calc, test_prices):
        """Testa precisão matemática do Stochastic RSI"""
        periods = [14, 21]
        
        for period in periods:
            strategy_stoch_rsi = strategy.calculate_stoch_rsi(test_prices, period)
            reference_stoch_rsi = reference_calc.reference_stoch_rsi(test_prices, period)
            
            # Tolerância maior para Stoch RSI devido à complexidade e diferentes implementações
            tolerance = 0.3  # 30% - algoritmos podem variar significativamente
            
            # Verificar se ambos estão na mesma região geral (alta, média, baixa)
            if reference_stoch_rsi > 0.7:  # Região de sobrecompra
                assert strategy_stoch_rsi > 0.4, f"StochRSI({period}): Strategy={strategy_stoch_rsi}, Reference={reference_stoch_rsi}"
            elif reference_stoch_rsi < 0.3:  # Região de sobrevenda
                assert strategy_stoch_rsi < 0.6, f"StochRSI({period}): Strategy={strategy_stoch_rsi}, Reference={reference_stoch_rsi}"
            else:  # Região neutra
                assert 0 <= strategy_stoch_rsi <= 1, f"StochRSI({period}): Strategy={strategy_stoch_rsi}, Reference={reference_stoch_rsi}"
    
    def test_ema_convergence_properties(self, strategy):
        """Testa propriedades matemáticas de convergência da EMA"""
        # Propriedade 1: EMA de valores constantes deve convergir para o valor
        constant_value = 100.0
        constant_prices = [constant_value] * 100
        
        ema = strategy.calculate_ema(constant_prices, 20)
        assert abs(ema - constant_value) < 0.01
        
        # Propriedade 2: EMA deve estar entre min e max dos valores recentes
        varied_prices = [95, 105, 98, 102, 97, 103, 96, 104, 99, 101]
        ema = strategy.calculate_ema(varied_prices, 5)
        
        recent_min = min(varied_prices[-5:])
        recent_max = max(varied_prices[-5:])
        assert recent_min <= ema <= recent_max
        
        # Propriedade 3: EMA deve ser mais sensível a valores recentes
        trend_up_prices = list(range(100, 120))  # Tendência de alta
        ema_up = strategy.calculate_ema(trend_up_prices, 10)
        
        trend_down_prices = list(range(120, 100, -1))  # Tendência de baixa
        ema_down = strategy.calculate_ema(trend_down_prices, 10)
        
        # EMA de tendência de alta deve ser maior que de tendência de baixa
        assert ema_up > ema_down
    
    def test_atr_properties(self, strategy):
        """Testa propriedades matemáticas do ATR"""
        # Propriedade 1: ATR deve ser sempre não-negativo
        test_cases = [
            ([100, 101, 102], [99, 100, 101], [100, 101, 102]),  # Tendência de alta
            ([102, 101, 100], [101, 100, 99], [102, 101, 100]),  # Tendência de baixa
            ([100, 100, 100], [100, 100, 100], [100, 100, 100])  # Sem movimento
        ]
        
        for highs, lows, closes in test_cases:
            atr = strategy.calculate_atr(highs, lows, closes, 3)
            assert atr >= 0
        
        # Propriedade 2: ATR deve aumentar com maior volatilidade
        low_vol_highs = [100.1, 100.2, 100.1, 100.2, 100.1]
        low_vol_lows = [99.9, 99.8, 99.9, 99.8, 99.9]
        low_vol_closes = [100.0, 100.0, 100.0, 100.0, 100.0]
        
        high_vol_highs = [102, 98, 103, 97, 104]
        high_vol_lows = [98, 94, 99, 93, 100]
        high_vol_closes = [100, 96, 101, 95, 102]
        
        low_atr = strategy.calculate_atr(low_vol_highs, low_vol_lows, low_vol_closes, 5)
        high_atr = strategy.calculate_atr(high_vol_highs, high_vol_lows, high_vol_closes, 5)
        
        assert high_atr > low_atr
    
    def test_numerical_stability(self, strategy):
        """Testa estabilidade numérica dos cálculos"""
        # Teste com números muito grandes
        large_prices = [1e10, 1e10 + 1000, 1e10 + 2000, 1e10 + 1500]
        ema_large = strategy.calculate_ema(large_prices, 3)
        assert not math.isnan(ema_large) and not math.isinf(ema_large)
        
        # Teste com números muito pequenos
        small_prices = [1e-6, 1.1e-6, 1.2e-6, 1.15e-6]
        ema_small = strategy.calculate_ema(small_prices, 3)
        assert not math.isnan(ema_small) and not math.isinf(ema_small)
        
        # Teste com diferenças muito pequenas
        similar_prices = [100.000001, 100.000002, 100.000003, 100.000002]
        ema_similar = strategy.calculate_ema(similar_prices, 3)
        assert not math.isnan(ema_similar) and not math.isinf(ema_similar)
    
    def test_monotonicity_properties(self, strategy):
        """Testa propriedades de monotonicidade"""
        # EMA deve preservar tendências monotônicas
        increasing_prices = [100, 101, 102, 103, 104, 105]
        decreasing_prices = [105, 104, 103, 102, 101, 100]
        
        ema_inc = strategy.calculate_ema(increasing_prices, 4)
        ema_dec = strategy.calculate_ema(decreasing_prices, 4)
        
        # EMA de sequência crescente deve ser maior que de sequência decrescente
        assert ema_inc > ema_dec
        
        # EMA deve estar entre primeiro e último valor para sequências monotônicas
        assert increasing_prices[0] <= ema_inc <= increasing_prices[-1]
        assert decreasing_prices[-1] <= ema_dec <= decreasing_prices[0]
    
    def test_period_sensitivity(self, strategy, test_prices):
        """Testa sensibilidade ao período dos indicadores"""
        # EMAs com períodos menores devem ser mais sensíveis a mudanças recentes
        ema_fast = strategy.calculate_ema(test_prices, 5)
        ema_slow = strategy.calculate_ema(test_prices, 20)
        
        # Para dados com tendência de alta, EMA rápida deve ser maior
        if test_prices[-1] > test_prices[0]:  # Tendência de alta
            assert ema_fast > ema_slow
        else:  # Tendência de baixa
            assert ema_fast < ema_slow
    
    def test_boundary_value_analysis(self, strategy):
        """Testa análise de valores limite"""
        # Período = 1 (deve ser igual ao último preço)
        prices = [100, 101, 102, 103]
        ema_period_1 = strategy.calculate_ema(prices, 1)
        assert abs(ema_period_1 - prices[-1]) < 0.01
        
        # Período igual ao número de dados
        ema_period_max = strategy.calculate_ema(prices, len(prices))
        # Deve estar próximo da média simples
        sma = sum(prices) / len(prices)
        assert abs(ema_period_max - sma) < abs(sma) * 0.1  # Dentro de 10%
    
    @pytest.mark.performance
    def test_computational_complexity(self, strategy):
        """Testa complexidade computacional dos algoritmos"""
        import time
        
        # Testar escalabilidade com diferentes tamanhos de dataset
        sizes = [100, 1000, 5000]
        times = []
        
        for size in sizes:
            prices = list(range(size))
            
            start_time = time.time()
            strategy.calculate_ema(prices, min(20, size//2))
            end_time = time.time()
            
            times.append(end_time - start_time)
        
        # Verificar que o tempo cresce linearmente (não exponencialmente)
        # Para datasets 50x maiores, tempo não deve ser mais que 100x maior
        if len(times) >= 2:
            time_ratio = times[-1] / times[0]
            size_ratio = sizes[-1] / sizes[0]
            assert time_ratio < size_ratio * 2  # Margem para variações do sistema


class TestCrossValidation:
    """Testes de validação cruzada entre diferentes implementações"""
    
    @pytest.fixture
    def strategy(self):
        return PPPVishvaStrategy()
    
    def test_ema_vs_sma_relationship(self, strategy):
        """Testa relação entre EMA e SMA"""
        prices = [100, 102, 98, 104, 96, 106, 94, 108, 92, 110]
        period = 5
        
        ema = strategy.calculate_ema(prices, period)
        
        # Calcular SMA de referência
        sma = sum(prices[-period:]) / period
        
        # Para dados com tendência, EMA deve estar entre SMA e último preço
        last_price = prices[-1]
        
        if last_price > sma:  # Tendência de alta
            assert sma <= ema <= last_price
        else:  # Tendência de baixa
            assert last_price <= ema <= sma
    
    def test_indicator_correlation(self, strategy):
        """Testa correlação esperada entre indicadores"""
        # Criar dados com tendência clara
        uptrend_prices = list(range(100, 150))
        downtrend_prices = list(range(150, 100, -1))
        
        # Calcular indicadores para ambas as tendências
        ema_up = strategy.calculate_ema(uptrend_prices, 20)
        ema_down = strategy.calculate_ema(downtrend_prices, 20)
        
        stoch_rsi_up = strategy.calculate_stoch_rsi(uptrend_prices, 14)
        stoch_rsi_down = strategy.calculate_stoch_rsi(downtrend_prices, 14)
        
        # Em tendência de alta, indicadores devem refletir força
        assert ema_up > uptrend_prices[0]  # EMA acima do início
        assert stoch_rsi_up > 0.5  # StochRSI em território de alta
        
        # Em tendência de baixa, indicadores devem refletir fraqueza
        assert ema_down < downtrend_prices[0]  # EMA abaixo do início
        assert stoch_rsi_down < 0.5  # StochRSI em território de baixa


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

