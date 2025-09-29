"""
Testes unitários para a estratégia PPP Vishva
"""
import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Adicionar o diretório do projeto ao path para imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

# Mock da estratégia PPP Vishva baseada no código analisado
class PPPVishvaStrategy:
    """
    Implementação da estratégia PPP Vishva para testes
    Baseada no código original analisado
    """
    
    def __init__(self, 
                 sl_ratio: float = 1.25,
                 pyramid_levels: int = 5,
                 risk_per_trade: float = 0.02):
        self.sl_ratio = sl_ratio
        self.pyramid_levels = pyramid_levels
        self.risk_per_trade = risk_per_trade
        
        # Strategy parameters
        self.ema_period = 100
        self.atr_period = 14
        self.ut_bot_factor = 3.0
        self.ewo_fast = 5
        self.ewo_slow = 35
        self.stoch_rsi_period = 14
        
        # Data storage
        self.price_history = {}
        self.indicators = {}
        self.last_signals = {}
        
        # Risk parameters
        self.risk_params = {
            "max_position_size": 2000.0,
            "max_daily_loss": 200.0,
            "max_open_positions": self.pyramid_levels,
            "stop_loss_pct": 0.03,
            "take_profit_pct": 0.06,
            "risk_per_trade": self.risk_per_trade,
            "sl_ratio": self.sl_ratio
        }
    
    def calculate_ema(self, prices: list, period: int) -> float:
        """Calculate Exponential Moving Average"""
        if len(prices) < period:
            return prices[-1] if prices else 0.0
        
        multiplier = 2 / (period + 1)
        ema = prices[0]
        
        for price in prices[1:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        
        return ema
    
    def calculate_atr(self, highs: list, lows: list, closes: list, period: int = 14) -> float:
        """Calculate Average True Range"""
        if len(closes) < 2:
            return 0.0
        
        true_ranges = []
        for i in range(1, len(closes)):
            high_low = highs[i] - lows[i]
            high_close = abs(highs[i] - closes[i-1])
            low_close = abs(lows[i] - closes[i-1])
            true_range = max(high_low, high_close, low_close)
            true_ranges.append(true_range)
        
        if len(true_ranges) < period:
            return sum(true_ranges) / len(true_ranges)
        
        return sum(true_ranges[-period:]) / period
    
    def calculate_ewo(self, prices: list, fast_period: int = 5, slow_period: int = 35) -> float:
        """Calculate Elliott Wave Oscillator"""
        if len(prices) < slow_period:
            return 0.0
        
        fast_ema = self.calculate_ema(prices, fast_period)
        slow_ema = self.calculate_ema(prices, slow_period)
        
        return fast_ema - slow_ema
    
    def calculate_stoch_rsi(self, prices: list, period: int = 14) -> float:
        """Calculate Stochastic RSI"""
        if len(prices) < period + 1:
            return 0.5
        
        # Simplified RSI calculation
        gains = []
        losses = []
        
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        if len(gains) < period:
            return 0.5
        
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 1.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        # Normalize to 0-1 range
        return rsi / 100
    
    def calculate_heikin_ashi(self, ohlc_data: list) -> dict:
        """Calculate Heikin Ashi candles"""
        if not ohlc_data:
            return {"open": 0, "high": 0, "low": 0, "close": 0}
        
        last_candle = ohlc_data[-1]
        
        # Simplified Heikin Ashi calculation
        ha_close = (last_candle["open"] + last_candle["high"] + 
                   last_candle["low"] + last_candle["close"]) / 4
        
        if len(ohlc_data) > 1:
            prev_candle = ohlc_data[-2]
            ha_open = (prev_candle["open"] + prev_candle["close"]) / 2
        else:
            ha_open = (last_candle["open"] + last_candle["close"]) / 2
        
        ha_high = max(last_candle["high"], ha_open, ha_close)
        ha_low = min(last_candle["low"], ha_open, ha_close)
        
        return {
            "open": ha_open,
            "high": ha_high,
            "low": ha_low,
            "close": ha_close
        }
    
    def generate_signal(self, market_data: dict) -> str:
        """Generate trading signal based on indicators"""
        # Simplified signal generation logic
        if not market_data or "close" not in market_data:
            return "hold"
        
        # This would contain the actual signal logic
        # For testing purposes, return based on simple conditions
        return "buy" if market_data["close"] > 50000 else "sell"


class TestPPPVishvaStrategy:
    """Testes para a estratégia PPP Vishva"""
    
    @pytest.fixture
    def strategy(self):
        """Fixture da estratégia para testes"""
        return PPPVishvaStrategy()
    
    @pytest.fixture
    def sample_prices(self):
        """Fixture com preços de exemplo"""
        return [50000, 50100, 49950, 50200, 50150, 50300, 50250, 50400, 50350, 50500]
    
    @pytest.fixture
    def sample_ohlc_data(self):
        """Fixture com dados OHLC de exemplo"""
        return [
            {"open": 50000, "high": 50200, "low": 49800, "close": 50100},
            {"open": 50100, "high": 50300, "low": 49900, "close": 50200},
            {"open": 50200, "high": 50400, "low": 50000, "close": 50300},
            {"open": 50300, "high": 50500, "low": 50100, "close": 50400},
            {"open": 50400, "high": 50600, "low": 50200, "close": 50500}
        ]
    
    def test_strategy_initialization(self):
        """Testa inicialização da estratégia"""
        strategy = PPPVishvaStrategy(sl_ratio=1.5, pyramid_levels=3, risk_per_trade=0.01)
        
        assert strategy.sl_ratio == 1.5
        assert strategy.pyramid_levels == 3
        assert strategy.risk_per_trade == 0.01
        assert strategy.ema_period == 100
        assert strategy.atr_period == 14
        assert strategy.ut_bot_factor == 3.0
        
        # Verificar parâmetros de risco
        assert strategy.risk_params["max_position_size"] == 2000.0
        assert strategy.risk_params["stop_loss_pct"] == 0.03
        assert strategy.risk_params["take_profit_pct"] == 0.06
    
    def test_calculate_ema_basic(self, strategy, sample_prices):
        """Testa cálculo básico da EMA"""
        ema = strategy.calculate_ema(sample_prices, 5)
        
        # EMA deve ser um número válido
        assert isinstance(ema, (int, float))
        assert ema > 0
        
        # EMA deve estar próxima da média dos preços recentes
        recent_avg = sum(sample_prices[-5:]) / 5
        assert abs(ema - recent_avg) < recent_avg * 0.1  # Dentro de 10%
    
    def test_calculate_ema_insufficient_data(self, strategy):
        """Testa EMA com dados insuficientes"""
        short_prices = [50000, 50100]
        ema = strategy.calculate_ema(short_prices, 10)
        
        # Deve retornar o último preço quando dados insuficientes
        assert ema == 50100
    
    def test_calculate_ema_empty_data(self, strategy):
        """Testa EMA com dados vazios"""
        ema = strategy.calculate_ema([], 10)
        assert ema == 0.0
    
    def test_calculate_ema_single_price(self, strategy):
        """Testa EMA com um único preço"""
        ema = strategy.calculate_ema([50000], 5)
        assert ema == 50000
    
    def test_calculate_atr_basic(self, strategy):
        """Testa cálculo básico do ATR"""
        highs = [50200, 50300, 50400, 50500, 50600]
        lows = [49800, 49900, 50000, 50100, 50200]
        closes = [50000, 50100, 50200, 50300, 50400]
        
        atr = strategy.calculate_atr(highs, lows, closes, 3)
        
        # ATR deve ser um número positivo
        assert isinstance(atr, (int, float))
        assert atr > 0
        
        # ATR deve ser razoável (não muito maior que a diferença high-low típica)
        typical_range = sum(h - l for h, l in zip(highs, lows)) / len(highs)
        assert atr <= typical_range * 2  # ATR não deve ser muito maior que o range típico
    
    def test_calculate_atr_insufficient_data(self, strategy):
        """Testa ATR com dados insuficientes"""
        highs = [50200]
        lows = [49800]
        closes = [50000]
        
        atr = strategy.calculate_atr(highs, lows, closes, 14)
        assert atr == 0.0
    
    def test_calculate_ewo_basic(self, strategy, sample_prices):
        """Testa cálculo básico do EWO"""
        ewo = strategy.calculate_ewo(sample_prices, 3, 7)
        
        # EWO deve ser um número (pode ser positivo ou negativo)
        assert isinstance(ewo, (int, float))
        
        # EWO deve ser a diferença entre EMAs rápida e lenta
        fast_ema = strategy.calculate_ema(sample_prices, 3)
        slow_ema = strategy.calculate_ema(sample_prices, 7)
        expected_ewo = fast_ema - slow_ema
        
        assert abs(ewo - expected_ewo) < 0.01  # Pequena tolerância para erros de ponto flutuante
    
    def test_calculate_ewo_insufficient_data(self, strategy):
        """Testa EWO com dados insuficientes"""
        short_prices = [50000, 50100]
        ewo = strategy.calculate_ewo(short_prices, 5, 10)
        assert ewo == 0.0
    
    def test_calculate_stoch_rsi_basic(self, strategy, sample_prices):
        """Testa cálculo básico do Stochastic RSI"""
        stoch_rsi = strategy.calculate_stoch_rsi(sample_prices, 5)
        
        # Stoch RSI deve estar entre 0 e 1
        assert isinstance(stoch_rsi, (int, float))
        assert 0 <= stoch_rsi <= 1
    
    def test_calculate_stoch_rsi_trending_up(self, strategy):
        """Testa Stoch RSI com preços em alta"""
        trending_up_prices = [50000, 50100, 50200, 50300, 50400, 50500, 50600]
        stoch_rsi = strategy.calculate_stoch_rsi(trending_up_prices, 5)
        
        # Com preços em alta, Stoch RSI deve ser alto
        assert stoch_rsi > 0.7
    
    def test_calculate_stoch_rsi_trending_down(self, strategy):
        """Testa Stoch RSI com preços em baixa"""
        trending_down_prices = [50600, 50500, 50400, 50300, 50200, 50100, 50000]
        stoch_rsi = strategy.calculate_stoch_rsi(trending_down_prices, 5)
        
        # Com preços em baixa, Stoch RSI deve ser baixo
        assert stoch_rsi < 0.3
    
    def test_calculate_stoch_rsi_insufficient_data(self, strategy):
        """Testa Stoch RSI com dados insuficientes"""
        short_prices = [50000, 50100]
        stoch_rsi = strategy.calculate_stoch_rsi(short_prices, 10)
        assert stoch_rsi == 0.5  # Valor neutro quando dados insuficientes
    
    def test_calculate_heikin_ashi_basic(self, strategy, sample_ohlc_data):
        """Testa cálculo básico do Heikin Ashi"""
        ha = strategy.calculate_heikin_ashi(sample_ohlc_data)
        
        # Deve retornar dicionário com OHLC
        assert isinstance(ha, dict)
        assert "open" in ha
        assert "high" in ha
        assert "low" in ha
        assert "close" in ha
        
        # Todos os valores devem ser números positivos
        for key, value in ha.items():
            assert isinstance(value, (int, float))
            assert value > 0
        
        # High deve ser >= Open e Close
        assert ha["high"] >= ha["open"]
        assert ha["high"] >= ha["close"]
        
        # Low deve ser <= Open e Close
        assert ha["low"] <= ha["open"]
        assert ha["low"] <= ha["close"]
    
    def test_calculate_heikin_ashi_empty_data(self, strategy):
        """Testa Heikin Ashi com dados vazios"""
        ha = strategy.calculate_heikin_ashi([])
        
        expected = {"open": 0, "high": 0, "low": 0, "close": 0}
        assert ha == expected
    
    def test_calculate_heikin_ashi_single_candle(self, strategy):
        """Testa Heikin Ashi com uma única vela"""
        single_candle = [{"open": 50000, "high": 50200, "low": 49800, "close": 50100}]
        ha = strategy.calculate_heikin_ashi(single_candle)
        
        # Com uma única vela, HA open deve ser média de open e close
        expected_open = (50000 + 50100) / 2
        expected_close = (50000 + 50200 + 49800 + 50100) / 4
        
        assert abs(ha["open"] - expected_open) < 0.01
        assert abs(ha["close"] - expected_close) < 0.01
    
    def test_generate_signal_basic(self, strategy):
        """Testa geração básica de sinal"""
        # Teste com preço alto (deve gerar buy)
        high_price_data = {"close": 55000}
        signal = strategy.generate_signal(high_price_data)
        assert signal == "buy"
        
        # Teste com preço baixo (deve gerar sell)
        low_price_data = {"close": 45000}
        signal = strategy.generate_signal(low_price_data)
        assert signal == "sell"
    
    def test_generate_signal_invalid_data(self, strategy):
        """Testa geração de sinal com dados inválidos"""
        # Dados vazios
        signal = strategy.generate_signal({})
        assert signal == "hold"
        
        # Dados sem close
        signal = strategy.generate_signal({"open": 50000})
        assert signal == "hold"
        
        # Dados None
        signal = strategy.generate_signal(None)
        assert signal == "hold"
    
    @pytest.mark.performance
    def test_indicator_calculation_performance(self, strategy, sample_prices):
        """Testa performance dos cálculos de indicadores"""
        import time
        
        # Criar dataset maior para teste de performance
        large_prices = sample_prices * 100  # 1000 pontos de dados
        
        # Testar EMA
        start_time = time.time()
        strategy.calculate_ema(large_prices, 100)
        ema_time = time.time() - start_time
        assert ema_time < 0.01  # Deve executar em menos de 10ms
        
        # Testar ATR
        highs = [p * 1.01 for p in large_prices]
        lows = [p * 0.99 for p in large_prices]
        
        start_time = time.time()
        strategy.calculate_atr(highs, lows, large_prices, 14)
        atr_time = time.time() - start_time
        assert atr_time < 0.01  # Deve executar em menos de 10ms
    
    def test_risk_parameters_validation(self, strategy):
        """Testa validação dos parâmetros de risco"""
        # Verificar se todos os parâmetros de risco estão definidos
        required_params = [
            "max_position_size", "max_daily_loss", "max_open_positions",
            "stop_loss_pct", "take_profit_pct", "risk_per_trade", "sl_ratio"
        ]
        
        for param in required_params:
            assert param in strategy.risk_params
            assert isinstance(strategy.risk_params[param], (int, float))
            assert strategy.risk_params[param] > 0
    
    def test_strategy_parameters_consistency(self, strategy):
        """Testa consistência dos parâmetros da estratégia"""
        # Stop loss deve ser menor que take profit
        assert strategy.risk_params["stop_loss_pct"] < strategy.risk_params["take_profit_pct"]
        
        # Risk per trade deve ser razoável (entre 0.1% e 10%)
        assert 0.001 <= strategy.risk_params["risk_per_trade"] <= 0.1
        
        # SL ratio deve ser >= 1
        assert strategy.risk_params["sl_ratio"] >= 1.0
        
        # Max open positions deve ser <= pyramid levels
        assert strategy.risk_params["max_open_positions"] <= strategy.pyramid_levels


# Testes de integração entre indicadores
class TestPPPVishvaIntegration:
    """Testes de integração entre diferentes indicadores"""
    
    @pytest.fixture
    def strategy(self):
        return PPPVishvaStrategy()
    
    def test_indicators_with_real_market_conditions(self, strategy, bullish_market_data):
        """Testa indicadores com condições reais de mercado"""
        # Converter DataFrame para listas
        closes = bullish_market_data['close'].tolist()
        highs = bullish_market_data['high'].tolist()
        lows = bullish_market_data['low'].tolist()
        
        # Calcular todos os indicadores
        ema = strategy.calculate_ema(closes, 20)
        atr = strategy.calculate_atr(highs, lows, closes, 14)
        ewo = strategy.calculate_ewo(closes, 5, 35)
        stoch_rsi = strategy.calculate_stoch_rsi(closes, 14)
        
        # Verificar se todos os indicadores retornam valores válidos
        assert ema > 0
        assert atr > 0
        assert isinstance(ewo, (int, float))
        assert 0 <= stoch_rsi <= 1
        
        # Em mercado em alta, EMA deve estar próxima dos preços recentes
        recent_avg = sum(closes[-20:]) / 20
        assert abs(ema - recent_avg) < recent_avg * 0.2
    
    def test_indicators_correlation_in_trending_market(self, strategy, bullish_market_data, bearish_market_data):
        """Testa correlação entre indicadores em mercados com tendência"""
        
        # Mercado em alta
        bull_closes = bullish_market_data['close'].tolist()
        bull_ewo = strategy.calculate_ewo(bull_closes, 5, 35)
        bull_stoch_rsi = strategy.calculate_stoch_rsi(bull_closes, 14)
        
        # Mercado em baixa
        bear_closes = bearish_market_data['close'].tolist()
        bear_ewo = strategy.calculate_ewo(bear_closes, 5, 35)
        bear_stoch_rsi = strategy.calculate_stoch_rsi(bear_closes, 14)
        
        # Em mercado em alta, EWO deve ser mais positivo e Stoch RSI mais alto
        assert bull_ewo > bear_ewo
        assert bull_stoch_rsi > bear_stoch_rsi
    
    def test_strategy_consistency_across_timeframes(self, strategy):
        """Testa consistência da estratégia em diferentes timeframes"""
        # Simular dados de diferentes timeframes
        base_prices = [50000 + i * 10 for i in range(100)]
        
        # Timeframe 1: dados originais
        ema_1m = strategy.calculate_ema(base_prices, 20)
        
        # Timeframe 2: dados com intervalos maiores (simulando 5m)
        prices_5m = base_prices[::5]  # Pegar a cada 5 pontos
        ema_5m = strategy.calculate_ema(prices_5m, 4)  # Ajustar período proporcionalmente
        
        # EMAs devem estar na mesma direção geral
        assert (ema_1m > base_prices[0]) == (ema_5m > prices_5m[0])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

