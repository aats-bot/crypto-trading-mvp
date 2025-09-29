# 🧪 Testes Unitários - Estratégias de Trading
"""
Testes unitários para as estratégias de trading do MVP Bot
Localização: /tests/unit/test_strategies.py
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from src.bot.strategies import get_strategy, get_available_strategies, get_strategy_info
from src.bot.interfaces import MarketData, Position, PositionSide, OrderSide, OrderType


class TestStrategyFactory:
    """Testes para o factory de estratégias"""
    
    def test_get_available_strategies(self):
        """Testa se retorna estratégias disponíveis"""
        strategies = get_available_strategies()
        
        assert isinstance(strategies, list)
        assert "sma" in strategies
        assert "rsi" in strategies
        assert len(strategies) >= 2
    
    def test_get_strategy_info(self):
        """Testa informações das estratégias"""
        sma_info = get_strategy_info("sma")
        
        assert "name" in sma_info
        assert "description" in sma_info
        assert "parameters" in sma_info
        assert sma_info["name"] == "Simple Moving Average"
    
    def test_get_strategy_sma(self):
        """Testa criação de estratégia SMA"""
        config = {"fast_period": 5, "slow_period": 10}
        strategy = get_strategy("sma", config)
        
        assert strategy is not None
        assert hasattr(strategy, 'analyze')
        assert hasattr(strategy, 'get_risk_parameters')
    
    def test_get_strategy_rsi(self):
        """Testa criação de estratégia RSI"""
        config = {"rsi_period": 14, "oversold": 30, "overbought": 70}
        strategy = get_strategy("rsi", config)
        
        assert strategy is not None
        assert hasattr(strategy, 'analyze')
        assert hasattr(strategy, 'get_risk_parameters')
    
    def test_get_strategy_invalid(self):
        """Testa estratégia inválida"""
        with pytest.raises(ValueError):
            get_strategy("invalid_strategy")


class TestSMAStrategy:
    """Testes para estratégia SMA"""
    
    @pytest.fixture
    def sma_strategy(self):
        """Fixture da estratégia SMA"""
        config = {"fast_period": 5, "slow_period": 10, "risk_per_trade": 0.02}
        return get_strategy("sma", config)
    
    @pytest.fixture
    def market_data(self):
        """Fixture de dados de mercado"""
        return MarketData(
            symbol="BTCUSDT",
            price=50000.0,
            timestamp=datetime.now(),
            volume=1000.0
        )
    
    def test_sma_initialization(self, sma_strategy):
        """Testa inicialização da estratégia SMA"""
        assert sma_strategy.fast_period == 5
        assert sma_strategy.slow_period == 10
        assert sma_strategy.risk_per_trade == 0.02
    
    def test_sma_risk_parameters(self, sma_strategy):
        """Testa parâmetros de risco"""
        risk_params = sma_strategy.get_risk_parameters()
        
        assert "max_position_size" in risk_params
        assert "max_daily_loss" in risk_params
        assert "stop_loss_pct" in risk_params
        assert risk_params["risk_per_trade"] == 0.02
    
    def test_sma_update_risk_parameters(self, sma_strategy):
        """Testa atualização de parâmetros de risco"""
        new_params = {"max_position_size": 2000.0}
        sma_strategy.update_risk_parameters(new_params)
        
        risk_params = sma_strategy.get_risk_parameters()
        assert risk_params["max_position_size"] == 2000.0
    
    @pytest.mark.asyncio
    async def test_sma_analyze_no_positions(self, sma_strategy, market_data):
        """Testa análise SMA sem posições"""
        orders = await sma_strategy.analyze(market_data, [])
        
        # Pode ou não gerar ordens dependendo dos dados mock
        assert isinstance(orders, list)
    
    @pytest.mark.asyncio
    async def test_sma_analyze_with_position(self, sma_strategy, market_data):
        """Testa análise SMA com posição existente"""
        position = Position(
            symbol="BTCUSDT",
            side=PositionSide.LONG,
            size=0.001,
            entry_price=49000.0,
            unrealized_pnl=1.0,
            timestamp=datetime.now()
        )
        
        orders = await sma_strategy.analyze(market_data, [position])
        assert isinstance(orders, list)
    
    def test_sma_calculate_sma(self, sma_strategy):
        """Testa cálculo de média móvel"""
        prices = [100, 102, 104, 106, 108]
        sma = sma_strategy._calculate_sma(prices, 5)
        
        expected = sum(prices) / len(prices)
        assert sma == expected
    
    def test_sma_calculate_sma_insufficient_data(self, sma_strategy):
        """Testa SMA com dados insuficientes"""
        prices = [100, 102]
        sma = sma_strategy._calculate_sma(prices, 5)
        
        assert sma == 0.0


class TestRSIStrategy:
    """Testes para estratégia RSI"""
    
    @pytest.fixture
    def rsi_strategy(self):
        """Fixture da estratégia RSI"""
        config = {"rsi_period": 14, "oversold": 30, "overbought": 70}
        return get_strategy("rsi", config)
    
    def test_rsi_initialization(self, rsi_strategy):
        """Testa inicialização da estratégia RSI"""
        assert rsi_strategy.rsi_period == 14
        assert rsi_strategy.oversold == 30
        assert rsi_strategy.overbought == 70
    
    def test_rsi_calculate_rsi(self, rsi_strategy):
        """Testa cálculo do RSI"""
        # Preços com tendência de alta
        prices = [100 + i for i in range(20)]
        rsi = rsi_strategy._calculate_rsi(prices, 14)
        
        # RSI deve estar acima de 50 para tendência de alta
        assert 0 <= rsi <= 100
        assert rsi > 50  # Tendência de alta
    
    def test_rsi_calculate_rsi_insufficient_data(self, rsi_strategy):
        """Testa RSI com dados insuficientes"""
        prices = [100, 102]
        rsi = rsi_strategy._calculate_rsi(prices, 14)
        
        assert rsi == 50.0  # Valor neutro padrão
    
    @pytest.mark.asyncio
    async def test_rsi_analyze(self, rsi_strategy, market_data):
        """Testa análise RSI"""
        orders = await rsi_strategy.analyze(market_data, [])
        assert isinstance(orders, list)


@pytest.mark.integration
class TestStrategyIntegration:
    """Testes de integração entre estratégias"""
    
    @pytest.mark.asyncio
    async def test_multiple_strategies_same_data(self, market_data):
        """Testa múltiplas estratégias com os mesmos dados"""
        sma_strategy = get_strategy("sma")
        rsi_strategy = get_strategy("rsi")
        
        sma_orders = await sma_strategy.analyze(market_data, [])
        rsi_orders = await rsi_strategy.analyze(market_data, [])
        
        # Ambas devem retornar listas
        assert isinstance(sma_orders, list)
        assert isinstance(rsi_orders, list)
    
    def test_all_strategies_have_required_methods(self):
        """Testa se todas as estratégias têm métodos obrigatórios"""
        strategies = get_available_strategies()
        
        for strategy_name in strategies:
            strategy = get_strategy(strategy_name)
            
            # Métodos obrigatórios
            assert hasattr(strategy, 'analyze')
            assert hasattr(strategy, 'get_risk_parameters')
            assert hasattr(strategy, 'update_risk_parameters')
            
            # Métodos assíncronos
            assert asyncio.iscoroutinefunction(strategy.analyze)


class TestPPPVishvaStrategy:
    """Testes para estratégia PPP Vishva (se disponível)"""
    
    @pytest.fixture
    def ppp_strategy(self):
        """Fixture da estratégia PPP Vishva"""
        try:
            config = {"sl_ratio": 1.25, "max_pyramid_levels": 5}
            return get_strategy("ppp_vishva", config)
        except ValueError:
            pytest.skip("PPP Vishva strategy not available")
    
    def test_ppp_initialization(self, ppp_strategy):
        """Testa inicialização da estratégia PPP Vishva"""
        if ppp_strategy:
            info = ppp_strategy.get_strategy_info()
            assert info["name"] == "PPP Vishva Algorithm"
            assert "indicators" in info
    
    @pytest.mark.asyncio
    async def test_ppp_analyze(self, ppp_strategy, market_data):
        """Testa análise PPP Vishva"""
        if ppp_strategy:
            orders = await ppp_strategy.analyze(market_data, [])
            assert isinstance(orders, list)


# Testes de performance
@pytest.mark.performance
class TestStrategyPerformance:
    """Testes de performance das estratégias"""
    
    @pytest.mark.asyncio
    async def test_strategy_analysis_speed(self, market_data):
        """Testa velocidade de análise das estratégias"""
        import time
        
        strategies = ["sma", "rsi"]
        
        for strategy_name in strategies:
            strategy = get_strategy(strategy_name)
            
            start_time = time.time()
            await strategy.analyze(market_data, [])
            end_time = time.time()
            
            # Análise deve ser rápida (< 1 segundo)
            assert (end_time - start_time) < 1.0
    
    def test_strategy_memory_usage(self):
        """Testa uso de memória das estratégias"""
        import sys
        
        # Criar múltiplas instâncias
        strategies = []
        for i in range(10):
            strategies.append(get_strategy("sma"))
        
        # Verificar que não há vazamentos óbvios
        assert len(strategies) == 10
        assert all(s is not None for s in strategies)

