# 🧪 Testes Unitários - Gerenciador de Risco
"""
Testes unitários para o gerenciador de risco do MVP Bot
Localização: /tests/unit/test_risk_manager.py
"""
import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime, timedelta

from src.bot.risk_manager import RiskManager
from src.bot.interfaces import (
    OrderRequest, OrderSide, OrderType, Position, PositionSide,
    MarketData
)


class TestRiskManagerInitialization:
    """Testes para inicialização do gerenciador de risco"""
    
    def test_risk_manager_default_initialization(self):
        """Testa inicialização com parâmetros padrão"""
        risk_manager = RiskManager()
        
        assert risk_manager.max_position_size == 1000.0
        assert risk_manager.max_daily_loss == 100.0
        assert risk_manager.max_open_positions == 5
        assert risk_manager.risk_per_trade == 0.02
        assert risk_manager.daily_loss == 0.0
        assert len(risk_manager.daily_trades) == 0
    
    def test_risk_manager_custom_initialization(self):
        """Testa inicialização com parâmetros customizados"""
        config = {
            "max_position_size": 2000.0,
            "max_daily_loss": 200.0,
            "max_open_positions": 10,
            "risk_per_trade": 0.03
        }
        
        risk_manager = RiskManager(config)
        
        assert risk_manager.max_position_size == 2000.0
        assert risk_manager.max_daily_loss == 200.0
        assert risk_manager.max_open_positions == 10
        assert risk_manager.risk_per_trade == 0.03


class TestOrderValidation:
    """Testes para validação de ordens"""
    
    @pytest.fixture
    def risk_manager(self):
        """Fixture do gerenciador de risco"""
        return RiskManager()
    
    @pytest.fixture
    def valid_order_request(self):
        """Fixture de ordem válida"""
        return OrderRequest(
            symbol="BTCUSDT",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=0.001
        )
    
    @pytest.fixture
    def market_data(self):
        """Fixture de dados de mercado"""
        return MarketData(
            symbol="BTCUSDT",
            price=50000.0,
            timestamp=datetime.now(),
            volume=1000.0
        )
    
    @pytest.mark.asyncio
    async def test_validate_order_valid(self, risk_manager, valid_order_request, market_data):
        """Testa validação de ordem válida"""
        positions = []
        account_balance = {"USDT": 5000.0}
        
        is_valid = await risk_manager.validate_order(
            valid_order_request, positions, account_balance, market_data
        )
        
        assert is_valid is True
    
    @pytest.mark.asyncio
    async def test_validate_order_insufficient_balance(self, risk_manager, valid_order_request, market_data):
        """Testa validação com saldo insuficiente"""
        positions = []
        account_balance = {"USDT": 10.0}  # Saldo muito baixo
        
        is_valid = await risk_manager.validate_order(
            valid_order_request, positions, account_balance, market_data
        )
        
        assert is_valid is False
    
    @pytest.mark.asyncio
    async def test_validate_order_too_many_positions(self, risk_manager, valid_order_request, market_data):
        """Testa validação com muitas posições abertas"""
        # Criar muitas posições
        positions = []
        for i in range(6):  # Mais que o limite padrão de 5
            position = Position(
                symbol=f"BTC{i}USDT",
                side=PositionSide.LONG,
                size=0.001,
                entry_price=50000.0,
                unrealized_pnl=0.0,
                timestamp=datetime.now()
            )
            positions.append(position)
        
        account_balance = {"USDT": 5000.0}
        
        is_valid = await risk_manager.validate_order(
            valid_order_request, positions, account_balance, market_data
        )
        
        assert is_valid is False
    
    @pytest.mark.asyncio
    async def test_validate_order_daily_loss_exceeded(self, risk_manager, valid_order_request, market_data):
        """Testa validação com perda diária excedida"""
        # Simular perda diária alta
        risk_manager.daily_loss = 150.0  # Acima do limite de 100
        
        positions = []
        account_balance = {"USDT": 5000.0}
        
        is_valid = await risk_manager.validate_order(
            valid_order_request, positions, account_balance, market_data
        )
        
        assert is_valid is False


class TestPositionSizeCalculation:
    """Testes para cálculo de tamanho de posição"""
    
    @pytest.fixture
    def risk_manager(self):
        """Fixture do gerenciador de risco"""
        return RiskManager()
    
    def test_calculate_position_size_basic(self, risk_manager):
        """Testa cálculo básico de tamanho de posição"""
        account_balance = {"USDT": 10000.0}
        current_price = 50000.0
        
        position_size = risk_manager.calculate_position_size(
            account_balance, current_price
        )
        
        # Com risk_per_trade de 2%, deve ser 200 USDT / 50000 = 0.004 BTC
        expected_size = (10000.0 * 0.02) / 50000.0
        assert abs(position_size - expected_size) < 0.0001
    
    def test_calculate_position_size_max_limit(self, risk_manager):
        """Testa limite máximo de posição"""
        account_balance = {"USDT": 100000.0}  # Saldo muito alto
        current_price = 50000.0
        
        position_size = risk_manager.calculate_position_size(
            account_balance, current_price
        )
        
        # Não deve exceder max_position_size (1000 USDT)
        max_size = 1000.0 / 50000.0
        assert position_size <= max_size
    
    def test_calculate_position_size_insufficient_balance(self, risk_manager):
        """Testa cálculo com saldo insuficiente"""
        account_balance = {"USDT": 50.0}  # Saldo muito baixo
        current_price = 50000.0
        
        position_size = risk_manager.calculate_position_size(
            account_balance, current_price
        )
        
        # Deve retornar 0 ou valor muito pequeno
        assert position_size <= 0.001


class TestDailyLimits:
    """Testes para limites diários"""
    
    @pytest.fixture
    def risk_manager(self):
        """Fixture do gerenciador de risco"""
        return RiskManager()
    
    @pytest.mark.asyncio
    async def test_check_daily_limits_within_limit(self, risk_manager):
        """Testa verificação dentro do limite diário"""
        # Perda dentro do limite
        risk_manager.daily_loss = 50.0
        
        within_limit = await risk_manager.check_daily_limits()
        assert within_limit is True
    
    @pytest.mark.asyncio
    async def test_check_daily_limits_exceeded(self, risk_manager):
        """Testa verificação com limite excedido"""
        # Perda acima do limite
        risk_manager.daily_loss = 150.0
        
        within_limit = await risk_manager.check_daily_limits()
        assert within_limit is False
    
    def test_update_daily_loss_profit(self, risk_manager):
        """Testa atualização com lucro"""
        initial_loss = risk_manager.daily_loss
        
        # Simular lucro
        risk_manager.update_daily_loss(50.0)  # Lucro de 50
        
        # Perda diária deve diminuir (ou ficar em 0)
        assert risk_manager.daily_loss <= initial_loss
    
    def test_update_daily_loss_loss(self, risk_manager):
        """Testa atualização com perda"""
        initial_loss = risk_manager.daily_loss
        
        # Simular perda
        risk_manager.update_daily_loss(-30.0)  # Perda de 30
        
        # Perda diária deve aumentar
        assert risk_manager.daily_loss == initial_loss + 30.0
    
    def test_reset_daily_stats(self, risk_manager):
        """Testa reset das estatísticas diárias"""
        # Adicionar algumas perdas e trades
        risk_manager.daily_loss = 50.0
        risk_manager.daily_trades = [
            {"timestamp": datetime.now(), "pnl": -10.0},
            {"timestamp": datetime.now(), "pnl": -20.0}
        ]
        
        risk_manager.reset_daily_stats()
        
        assert risk_manager.daily_loss == 0.0
        assert len(risk_manager.daily_trades) == 0


class TestStopLossCalculation:
    """Testes para cálculo de stop loss"""
    
    @pytest.fixture
    def risk_manager(self):
        """Fixture do gerenciador de risco"""
        return RiskManager()
    
    def test_calculate_stop_loss_long_position(self, risk_manager):
        """Testa cálculo de stop loss para posição longa"""
        entry_price = 50000.0
        stop_loss_pct = 0.02  # 2%
        
        stop_loss = risk_manager.calculate_stop_loss(
            entry_price, PositionSide.LONG, stop_loss_pct
        )
        
        # Stop loss deve ser 2% abaixo do preço de entrada
        expected_stop_loss = entry_price * (1 - stop_loss_pct)
        assert abs(stop_loss - expected_stop_loss) < 0.01
    
    def test_calculate_stop_loss_short_position(self, risk_manager):
        """Testa cálculo de stop loss para posição curta"""
        entry_price = 50000.0
        stop_loss_pct = 0.02  # 2%
        
        stop_loss = risk_manager.calculate_stop_loss(
            entry_price, PositionSide.SHORT, stop_loss_pct
        )
        
        # Stop loss deve ser 2% acima do preço de entrada
        expected_stop_loss = entry_price * (1 + stop_loss_pct)
        assert abs(stop_loss - expected_stop_loss) < 0.01


class TestTakeProfitCalculation:
    """Testes para cálculo de take profit"""
    
    @pytest.fixture
    def risk_manager(self):
        """Fixture do gerenciador de risco"""
        return RiskManager()
    
    def test_calculate_take_profit_long_position(self, risk_manager):
        """Testa cálculo de take profit para posição longa"""
        entry_price = 50000.0
        take_profit_pct = 0.04  # 4%
        
        take_profit = risk_manager.calculate_take_profit(
            entry_price, PositionSide.LONG, take_profit_pct
        )
        
        # Take profit deve ser 4% acima do preço de entrada
        expected_take_profit = entry_price * (1 + take_profit_pct)
        assert abs(take_profit - expected_take_profit) < 0.01
    
    def test_calculate_take_profit_short_position(self, risk_manager):
        """Testa cálculo de take profit para posição curta"""
        entry_price = 50000.0
        take_profit_pct = 0.04  # 4%
        
        take_profit = risk_manager.calculate_take_profit(
            entry_price, PositionSide.SHORT, take_profit_pct
        )
        
        # Take profit deve ser 4% abaixo do preço de entrada
        expected_take_profit = entry_price * (1 - take_profit_pct)
        assert abs(take_profit - expected_take_profit) < 0.01


class TestRiskParameterUpdate:
    """Testes para atualização de parâmetros de risco"""
    
    @pytest.fixture
    def risk_manager(self):
        """Fixture do gerenciador de risco"""
        return RiskManager()
    
    def test_update_risk_parameters(self, risk_manager):
        """Testa atualização de parâmetros de risco"""
        new_params = {
            "max_position_size": 2000.0,
            "max_daily_loss": 150.0,
            "risk_per_trade": 0.03
        }
        
        risk_manager.update_risk_parameters(new_params)
        
        assert risk_manager.max_position_size == 2000.0
        assert risk_manager.max_daily_loss == 150.0
        assert risk_manager.risk_per_trade == 0.03
    
    def test_update_partial_risk_parameters(self, risk_manager):
        """Testa atualização parcial de parâmetros"""
        original_max_positions = risk_manager.max_open_positions
        
        new_params = {
            "max_position_size": 1500.0
        }
        
        risk_manager.update_risk_parameters(new_params)
        
        # Parâmetro atualizado deve mudar
        assert risk_manager.max_position_size == 1500.0
        
        # Outros parâmetros devem permanecer iguais
        assert risk_manager.max_open_positions == original_max_positions


# Testes de integração
@pytest.mark.integration
class TestRiskManagerIntegration:
    """Testes de integração do gerenciador de risco"""
    
    @pytest.fixture
    def risk_manager(self):
        """Fixture do gerenciador de risco"""
        return RiskManager()
    
    @pytest.mark.asyncio
    async def test_full_risk_workflow(self, risk_manager):
        """Testa fluxo completo de gerenciamento de risco"""
        # Dados de teste
        order_request = OrderRequest(
            symbol="BTCUSDT",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=0.001
        )
        
        market_data = MarketData(
            symbol="BTCUSDT",
            price=50000.0,
            timestamp=datetime.now(),
            volume=1000.0
        )
        
        positions = []
        account_balance = {"USDT": 5000.0}
        
        # 1. Validar ordem
        is_valid = await risk_manager.validate_order(
            order_request, positions, account_balance, market_data
        )
        assert is_valid is True
        
        # 2. Calcular tamanho de posição
        position_size = risk_manager.calculate_position_size(
            account_balance, market_data.price
        )
        assert position_size > 0
        
        # 3. Calcular stop loss e take profit
        stop_loss = risk_manager.calculate_stop_loss(
            market_data.price, PositionSide.LONG, 0.02
        )
        take_profit = risk_manager.calculate_take_profit(
            market_data.price, PositionSide.LONG, 0.04
        )
        
        assert stop_loss < market_data.price
        assert take_profit > market_data.price
        
        # 4. Verificar limites diários
        within_limits = await risk_manager.check_daily_limits()
        assert within_limits is True


# Testes de performance
@pytest.mark.performance
class TestRiskManagerPerformance:
    """Testes de performance do gerenciador de risco"""
    
    @pytest.mark.asyncio
    async def test_validation_speed(self):
        """Testa velocidade de validação"""
        import time
        
        risk_manager = RiskManager()
        
        order_request = OrderRequest(
            symbol="BTCUSDT",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=0.001
        )
        
        market_data = MarketData(
            symbol="BTCUSDT",
            price=50000.0,
            timestamp=datetime.now(),
            volume=1000.0
        )
        
        positions = []
        account_balance = {"USDT": 5000.0}
        
        start_time = time.time()
        
        # Executar múltiplas validações
        for _ in range(100):
            await risk_manager.validate_order(
                order_request, positions, account_balance, market_data
            )
        
        end_time = time.time()
        
        # Deve ser rápido (< 1 segundo para 100 validações)
        assert (end_time - start_time) < 1.0

