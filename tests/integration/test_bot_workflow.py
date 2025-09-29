# 🧪 Testes de Integração - Workflow do Bot
"""
Testes de integração para o workflow completo do bot de trading
Localização: /tests/integration/test_bot_workflow.py
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta

from src.bot.trading_bot import TradingBot
from src.bot.worker import TradingWorker
from src.bot.strategies import get_strategy
from src.bot.risk_manager import RiskManager
from src.bot.bybit_provider import BybitProvider
from src.bot.interfaces import MarketData, Position, PositionSide, OrderSide, OrderType


@pytest.mark.integration
class TestTradingBotWorkflow:
    """Testes de integração do workflow do bot de trading"""
    
    @pytest.fixture
    def mock_bybit_provider(self):
        """Mock do provider Bybit"""
        provider = Mock(spec=BybitProvider)
        provider.get_market_data = AsyncMock()
        provider.place_order = AsyncMock()
        provider.get_positions = AsyncMock(return_value=[])
        provider.get_account_balance = AsyncMock(return_value={"USDT": 1000.0})
        provider.get_order_history = AsyncMock(return_value=[])
        return provider
    
    @pytest.fixture
    def risk_manager(self):
        """Fixture do gerenciador de risco"""
        return RiskManager({
            "max_position_size": 500.0,
            "max_daily_loss": 50.0,
            "risk_per_trade": 0.02
        })
    
    @pytest.fixture
    def trading_bot(self, mock_bybit_provider, risk_manager):
        """Fixture do bot de trading"""
        client_config = {
            "client_id": 1,
            "strategy": "sma",
            "symbols": ["BTCUSDT"],
            "fast_period": 5,
            "slow_period": 10,
            "risk_per_trade": 0.02
        }
        
        return TradingBot(
            client_config=client_config,
            bybit_provider=mock_bybit_provider,
            risk_manager=risk_manager
        )
    
    @pytest.mark.asyncio
    async def test_bot_initialization(self, trading_bot):
        """Testa inicialização do bot"""
        assert trading_bot.client_id == 1
        assert trading_bot.symbols == ["BTCUSDT"]
        assert trading_bot.strategy is not None
        assert trading_bot.risk_manager is not None
        assert trading_bot.is_running is False
    
    @pytest.mark.asyncio
    async def test_bot_start_stop(self, trading_bot):
        """Testa início e parada do bot"""
        # Iniciar bot
        await trading_bot.start()
        assert trading_bot.is_running is True
        
        # Parar bot
        await trading_bot.stop()
        assert trading_bot.is_running is False
    
    @pytest.mark.asyncio
    async def test_single_trading_cycle(self, trading_bot, mock_bybit_provider):
        """Testa um ciclo completo de trading"""
        # Mock dos dados de mercado
        market_data = MarketData(
            symbol="BTCUSDT",
            price=50000.0,
            timestamp=datetime.now(),
            volume=1000.0
        )
        mock_bybit_provider.get_market_data.return_value = market_data
        
        # Mock de posições vazias
        mock_bybit_provider.get_positions.return_value = []
        
        # Mock de saldo
        mock_bybit_provider.get_account_balance.return_value = {"USDT": 1000.0}
        
        # Executar um ciclo
        await trading_bot._trading_cycle()
        
        # Verificar que os métodos foram chamados
        mock_bybit_provider.get_market_data.assert_called()
        mock_bybit_provider.get_positions.assert_called()
        mock_bybit_provider.get_account_balance.assert_called()
    
    @pytest.mark.asyncio
    async def test_order_execution_workflow(self, trading_bot, mock_bybit_provider):
        """Testa workflow de execução de ordens"""
        # Mock dos dados que gerarão uma ordem
        market_data = MarketData(
            symbol="BTCUSDT",
            price=50000.0,
            timestamp=datetime.now(),
            volume=1000.0
        )
        mock_bybit_provider.get_market_data.return_value = market_data
        mock_bybit_provider.get_positions.return_value = []
        mock_bybit_provider.get_account_balance.return_value = {"USDT": 1000.0}
        
        # Mock de ordem executada com sucesso
        mock_order = Mock()
        mock_order.id = "order_123"
        mock_order.status = "filled"
        mock_bybit_provider.place_order.return_value = mock_order
        
        # Patch da estratégia para garantir que retorne uma ordem
        with patch.object(trading_bot.strategy, 'analyze') as mock_analyze:
            from src.bot.interfaces import OrderRequest
            mock_order_request = OrderRequest(
                symbol="BTCUSDT",
                side=OrderSide.BUY,
                order_type=OrderType.MARKET,
                quantity=0.001
            )
            mock_analyze.return_value = [mock_order_request]
            
            # Executar ciclo
            await trading_bot._trading_cycle()
            
            # Verificar que a ordem foi colocada
            mock_bybit_provider.place_order.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_risk_management_integration(self, trading_bot, mock_bybit_provider):
        """Testa integração com gerenciamento de risco"""
        # Mock de dados que normalmente gerariam ordem
        market_data = MarketData(
            symbol="BTCUSDT",
            price=50000.0,
            timestamp=datetime.now(),
            volume=1000.0
        )
        mock_bybit_provider.get_market_data.return_value = market_data
        mock_bybit_provider.get_positions.return_value = []
        
        # Mock de saldo insuficiente (deve bloquear ordem)
        mock_bybit_provider.get_account_balance.return_value = {"USDT": 10.0}
        
        # Patch da estratégia para retornar ordem
        with patch.object(trading_bot.strategy, 'analyze') as mock_analyze:
            from src.bot.interfaces import OrderRequest
            mock_order_request = OrderRequest(
                symbol="BTCUSDT",
                side=OrderSide.BUY,
                order_type=OrderType.MARKET,
                quantity=0.001
            )
            mock_analyze.return_value = [mock_order_request]
            
            # Executar ciclo
            await trading_bot._trading_cycle()
            
            # Verificar que a ordem NÃO foi colocada devido ao risco
            mock_bybit_provider.place_order.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_position_monitoring(self, trading_bot, mock_bybit_provider):
        """Testa monitoramento de posições"""
        # Mock de posição existente
        position = Position(
            symbol="BTCUSDT",
            side=PositionSide.LONG,
            size=0.001,
            entry_price=49000.0,
            unrealized_pnl=10.0,
            timestamp=datetime.now()
        )
        mock_bybit_provider.get_positions.return_value = [position]
        
        # Mock de dados de mercado
        market_data = MarketData(
            symbol="BTCUSDT",
            price=50000.0,
            timestamp=datetime.now(),
            volume=1000.0
        )
        mock_bybit_provider.get_market_data.return_value = market_data
        mock_bybit_provider.get_account_balance.return_value = {"USDT": 1000.0}
        
        # Executar ciclo
        await trading_bot._trading_cycle()
        
        # Verificar que a posição foi processada
        assert len(trading_bot.current_positions) > 0


@pytest.mark.integration
class TestTradingWorkerIntegration:
    """Testes de integração do worker de trading"""
    
    @pytest.fixture
    def trading_worker(self):
        """Fixture do worker de trading"""
        return TradingWorker()
    
    @pytest.mark.asyncio
    async def test_worker_bot_management(self, trading_worker):
        """Testa gerenciamento de bots pelo worker"""
        client_config = {
            "client_id": 1,
            "strategy": "sma",
            "symbols": ["BTCUSDT"],
            "bybit_api_key": "test_key",
            "bybit_api_secret": "test_secret"
        }
        
        # Adicionar bot
        with patch('src.bot.bybit_provider.BybitProvider'):
            await trading_worker.add_client_bot(client_config)
            
            # Verificar que o bot foi adicionado
            assert 1 in trading_worker.client_bots
            
            # Remover bot
            await trading_worker.remove_client_bot(1)
            
            # Verificar que o bot foi removido
            assert 1 not in trading_worker.client_bots
    
    @pytest.mark.asyncio
    async def test_worker_status_reporting(self, trading_worker):
        """Testa relatório de status do worker"""
        # Obter status sem bots
        status = await trading_worker.get_status()
        
        assert "active_bots" in status
        assert "total_clients" in status
        assert status["active_bots"] == 0
        assert status["total_clients"] == 0
    
    @pytest.mark.asyncio
    async def test_worker_multiple_clients(self, trading_worker):
        """Testa worker com múltiplos clientes"""
        client_configs = [
            {
                "client_id": 1,
                "strategy": "sma",
                "symbols": ["BTCUSDT"],
                "bybit_api_key": "test_key_1",
                "bybit_api_secret": "test_secret_1"
            },
            {
                "client_id": 2,
                "strategy": "rsi",
                "symbols": ["ETHUSDT"],
                "bybit_api_key": "test_key_2",
                "bybit_api_secret": "test_secret_2"
            }
        ]
        
        with patch('src.bot.bybit_provider.BybitProvider'):
            # Adicionar múltiplos bots
            for config in client_configs:
                await trading_worker.add_client_bot(config)
            
            # Verificar que ambos foram adicionados
            assert len(trading_worker.client_bots) == 2
            assert 1 in trading_worker.client_bots
            assert 2 in trading_worker.client_bots
            
            # Obter status
            status = await trading_worker.get_status()
            assert status["total_clients"] == 2


@pytest.mark.integration
class TestStrategyIntegration:
    """Testes de integração das estratégias"""
    
    @pytest.mark.asyncio
    async def test_sma_strategy_integration(self):
        """Testa integração completa da estratégia SMA"""
        strategy = get_strategy("sma", {
            "fast_period": 5,
            "slow_period": 10,
            "risk_per_trade": 0.02
        })
        
        # Dados de mercado simulados
        market_data = MarketData(
            symbol="BTCUSDT",
            price=50000.0,
            timestamp=datetime.now(),
            volume=1000.0
        )
        
        # Testar análise sem posições
        orders = await strategy.analyze(market_data, [])
        assert isinstance(orders, list)
        
        # Testar com posição existente
        position = Position(
            symbol="BTCUSDT",
            side=PositionSide.LONG,
            size=0.001,
            entry_price=49000.0,
            unrealized_pnl=10.0,
            timestamp=datetime.now()
        )
        
        orders_with_position = await strategy.analyze(market_data, [position])
        assert isinstance(orders_with_position, list)
    
    @pytest.mark.asyncio
    async def test_rsi_strategy_integration(self):
        """Testa integração completa da estratégia RSI"""
        strategy = get_strategy("rsi", {
            "rsi_period": 14,
            "oversold": 30,
            "overbought": 70,
            "risk_per_trade": 0.02
        })
        
        # Dados de mercado simulados
        market_data = MarketData(
            symbol="BTCUSDT",
            price=50000.0,
            timestamp=datetime.now(),
            volume=1000.0
        )
        
        # Testar análise
        orders = await strategy.analyze(market_data, [])
        assert isinstance(orders, list)
        
        # Testar parâmetros de risco
        risk_params = strategy.get_risk_parameters()
        assert "max_position_size" in risk_params
        assert "risk_per_trade" in risk_params


@pytest.mark.integration
class TestEndToEndWorkflow:
    """Testes de workflow completo end-to-end"""
    
    @pytest.fixture
    def complete_system_mocks(self):
        """Mocks para sistema completo"""
        mocks = {}
        
        # Mock Bybit Provider
        mocks['bybit'] = Mock(spec=BybitProvider)
        mocks['bybit'].get_market_data = AsyncMock()
        mocks['bybit'].place_order = AsyncMock()
        mocks['bybit'].get_positions = AsyncMock(return_value=[])
        mocks['bybit'].get_account_balance = AsyncMock(return_value={"USDT": 1000.0})
        
        return mocks
    
    @pytest.mark.asyncio
    async def test_complete_trading_workflow(self, complete_system_mocks):
        """Testa workflow completo de trading"""
        # 1. Configuração do cliente
        client_config = {
            "client_id": 1,
            "strategy": "sma",
            "symbols": ["BTCUSDT"],
            "fast_period": 5,
            "slow_period": 10,
            "risk_per_trade": 0.02,
            "bybit_api_key": "test_key",
            "bybit_api_secret": "test_secret"
        }
        
        # 2. Criar componentes
        risk_manager = RiskManager()
        
        with patch('src.bot.bybit_provider.BybitProvider', return_value=complete_system_mocks['bybit']):
            trading_bot = TradingBot(
                client_config=client_config,
                bybit_provider=complete_system_mocks['bybit'],
                risk_manager=risk_manager
            )
            
            # 3. Mock dados de mercado
            market_data = MarketData(
                symbol="BTCUSDT",
                price=50000.0,
                timestamp=datetime.now(),
                volume=1000.0
            )
            complete_system_mocks['bybit'].get_market_data.return_value = market_data
            
            # 4. Iniciar bot
            await trading_bot.start()
            assert trading_bot.is_running is True
            
            # 5. Executar alguns ciclos
            for _ in range(3):
                await trading_bot._trading_cycle()
                await asyncio.sleep(0.1)  # Pequena pausa
            
            # 6. Parar bot
            await trading_bot.stop()
            assert trading_bot.is_running is False
            
            # 7. Verificar que os métodos foram chamados
            assert complete_system_mocks['bybit'].get_market_data.call_count >= 3
            assert complete_system_mocks['bybit'].get_positions.call_count >= 3
    
    @pytest.mark.asyncio
    async def test_error_recovery_workflow(self, complete_system_mocks):
        """Testa recuperação de erros no workflow"""
        client_config = {
            "client_id": 1,
            "strategy": "sma",
            "symbols": ["BTCUSDT"],
            "bybit_api_key": "test_key",
            "bybit_api_secret": "test_secret"
        }
        
        # Mock que gera erro na primeira chamada, sucesso na segunda
        complete_system_mocks['bybit'].get_market_data.side_effect = [
            Exception("Network error"),
            MarketData(
                symbol="BTCUSDT",
                price=50000.0,
                timestamp=datetime.now(),
                volume=1000.0
            )
        ]
        
        risk_manager = RiskManager()
        
        with patch('src.bot.bybit_provider.BybitProvider', return_value=complete_system_mocks['bybit']):
            trading_bot = TradingBot(
                client_config=client_config,
                bybit_provider=complete_system_mocks['bybit'],
                risk_manager=risk_manager
            )
            
            # Executar ciclos - primeiro deve falhar, segundo deve funcionar
            await trading_bot._trading_cycle()  # Erro
            await trading_bot._trading_cycle()  # Sucesso
            
            # Verificar que foi chamado duas vezes
            assert complete_system_mocks['bybit'].get_market_data.call_count == 2
    
    @pytest.mark.asyncio
    async def test_performance_under_load(self, complete_system_mocks):
        """Testa performance sob carga"""
        import time
        
        client_config = {
            "client_id": 1,
            "strategy": "sma",
            "symbols": ["BTCUSDT", "ETHUSDT", "ADAUSDT"],  # Múltiplos símbolos
            "bybit_api_key": "test_key",
            "bybit_api_secret": "test_secret"
        }
        
        # Mock dados de mercado
        market_data = MarketData(
            symbol="BTCUSDT",
            price=50000.0,
            timestamp=datetime.now(),
            volume=1000.0
        )
        complete_system_mocks['bybit'].get_market_data.return_value = market_data
        
        risk_manager = RiskManager()
        
        with patch('src.bot.bybit_provider.BybitProvider', return_value=complete_system_mocks['bybit']):
            trading_bot = TradingBot(
                client_config=client_config,
                bybit_provider=complete_system_mocks['bybit'],
                risk_manager=risk_manager
            )
            
            # Medir tempo de execução de múltiplos ciclos
            start_time = time.time()
            
            for _ in range(10):
                await trading_bot._trading_cycle()
            
            end_time = time.time()
            
            # Deve ser razoavelmente rápido (< 5 segundos para 10 ciclos)
            assert (end_time - start_time) < 5.0
            
            # Verificar que todos os símbolos foram processados
            assert complete_system_mocks['bybit'].get_market_data.call_count >= 30  # 10 ciclos * 3 símbolos

