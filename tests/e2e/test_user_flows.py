"""
Testes End-to-End de Fluxos de Usuário
Semana 3 da Onda 1 - Compatível com Windows
"""
import pytest
import asyncio
import json
import time
from datetime import datetime, timedelta
import sys
import os
from unittest.mock import Mock, patch, MagicMock
import tempfile
import shutil

# Adicionar o diretório do projeto ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

# Importar componentes dos testes anteriores
try:
    from tests.integration.test_simple_integration import SimpleAPI, SimpleCache
    # Usar a versão mais completa do banco de dados
    from tests.integration.test_database_integration import DatabaseManager as SimpleDatabase
    from tests.unit.test_ppp_vishva_strategy import PPPVishvaStrategy
except ImportError:
    # Fallback para componentes básicos
    class SimpleAPI:
        def __init__(self):
            self.is_running = False
        async def start(self):
            self.is_running = True
            return {"status": "started"}
        async def stop(self):
            self.is_running = False
            return {"status": "stopped"}
    
    class SimpleDatabase:
        def __init__(self):
            self.is_connected = False
        async def connect(self):
            self.is_connected = True
            return {"status": "connected"}
        async def disconnect(self):
            self.is_connected = False
            return {"status": "disconnected"}
    
    class SimpleCache:
        def __init__(self):
            self.is_connected = False
        async def connect(self):
            self.is_connected = True
            return {"status": "connected"}
        async def disconnect(self):
            self.is_connected = False
            return {"status": "disconnected"}


class TradingSystem:
    """
    Sistema de trading completo para testes E2E
    Simula o sistema real com todos os componentes integrados
    """
    
    def __init__(self, config_dir=None):
        self.config_dir = config_dir or tempfile.mkdtemp()
        self.api = SimpleAPI()
        self.database = SimpleDatabase(":memory:")  # Banco em memória para testes
        self.cache = SimpleCache()
        self.strategy_engine = StrategyEngine()
        self.dashboard = StreamlitDashboard()
        self.is_initialized = False
        
        # Estado do sistema
        self.users = {}
        self.active_strategies = {}
        self.market_data_feeds = {}
        self.system_logs = []
        
    async def initialize(self):
        """Inicializar sistema completo"""
        try:
            # Conectar componentes
            await self.api.start()
            await self.database.connect()
            await self.cache.connect()
            
            # Inicializar estratégias
            await self.strategy_engine.initialize()
            
            # Configurar dashboard
            self.dashboard.configure(self.api, self.database)
            
            self.is_initialized = True
            await self._log_event("INFO", "Sistema inicializado com sucesso")
            
            return {"status": "initialized", "components": 4}
            
        except Exception as e:
            await self._log_event("ERROR", f"Erro na inicialização: {e}")
            raise
    
    async def shutdown(self):
        """Desligar sistema"""
        try:
            # Parar componentes na ordem inversa
            if hasattr(self.dashboard, 'stop'):
                await self.dashboard.stop()
            
            await self.strategy_engine.shutdown()
            await self.cache.disconnect()
            await self.database.disconnect()
            await self.api.stop()
            
            self.is_initialized = False
            
            # Limpar diretório temporário
            if os.path.exists(self.config_dir):
                shutil.rmtree(self.config_dir, ignore_errors=True)
            
            return {"status": "shutdown"}
            
        except Exception as e:
            print(f"Erro no shutdown: {e}")
            return {"status": "error", "error": str(e)}
    
    async def create_user_account(self, username, email, password):
        """Criar conta de usuário completa"""
        if not self.is_initialized:
            raise RuntimeError("Sistema não inicializado")
        
        # Criar usuário no banco
        user = await self.database.create_user(username, email, password)
        
        # Cache da sessão
        session_data = {
            "user_id": user["id"],
            "username": username,
            "login_time": datetime.now().isoformat(),
            "permissions": ["trade", "view_positions", "manage_strategies"]
        }
        
        await self.cache.set(f"session:{user['id']}", session_data, ttl=3600)
        
        # Adicionar ao estado do sistema
        self.users[user["id"]] = user
        
        await self._log_event("INFO", f"Usuário criado: {username}", user["id"])
        
        return user
    
    async def user_login(self, username, password):
        """Login de usuário"""
        # Simular autenticação
        user = None
        for u in self.users.values():
            if u["username"] == username:
                user = u
                break
        
        if not user:
            raise ValueError("Usuário não encontrado")
        
        # Atualizar sessão
        session_data = {
            "user_id": user["id"],
            "username": username,
            "login_time": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
            "permissions": ["trade", "view_positions", "manage_strategies"]
        }
        
        await self.cache.set(f"session:{user['id']}", session_data, ttl=3600)
        
        await self._log_event("INFO", f"Login realizado: {username}", user["id"])
        
        return {"user": user, "session": session_data}
    
    async def configure_strategy(self, user_id, strategy_name, parameters):
        """Configurar estratégia de trading"""
        if not self.is_initialized:
            raise RuntimeError("Sistema não inicializado")
        
        # Validar usuário
        if user_id not in self.users:
            raise ValueError("Usuário não encontrado")
        
        # Criar estratégia no banco
        strategy = await self.database.create_strategy(
            user_id=user_id,
            name=strategy_name,
            strategy_type="ppp_vishva",
            parameters=parameters
        )
        
        # Registrar no engine de estratégias
        strategy_instance = await self.strategy_engine.create_strategy(
            strategy["id"], 
            strategy_name, 
            parameters
        )
        
        self.active_strategies[strategy["id"]] = strategy_instance
        
        await self._log_event("INFO", f"Estratégia configurada: {strategy_name}", user_id)
        
        return strategy
    
    async def start_trading(self, user_id, strategy_id, symbols):
        """Iniciar trading com estratégia"""
        if strategy_id not in self.active_strategies:
            raise ValueError("Estratégia não encontrada")
        
        strategy = self.active_strategies[strategy_id]
        
        # Configurar símbolos para monitoramento
        for symbol in symbols:
            await self._setup_market_data_feed(symbol)
        
        # Ativar estratégia
        await strategy.activate(symbols)
        
        await self._log_event("INFO", f"Trading iniciado para {len(symbols)} símbolos", user_id)
        
        return {
            "status": "trading_started",
            "strategy_id": strategy_id,
            "symbols": symbols,
            "timestamp": datetime.now().isoformat()
        }
    
    async def execute_trade(self, user_id, symbol, side, quantity, strategy_id=None):
        """Executar trade"""
        # Obter dados de mercado atuais
        market_data = await self.api.get_market_data(symbol)
        
        # Criar posição
        position = await self.database.create_position(
            user_id=user_id,
            strategy_id=strategy_id,
            symbol=symbol,
            side=side,
            size=quantity,
            entry_price=market_data["price"]
        )
        
        # Simular execução na exchange
        execution_result = {
            "order_id": f"order_{int(time.time())}",
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "price": market_data["price"],
            "status": "filled",
            "timestamp": datetime.now().isoformat()
        }
        
        # Cache da posição
        await self.cache.set(f"position:{position['id']}", position, ttl=300)
        
        await self._log_event("INFO", f"Trade executado: {side} {quantity} {symbol}", user_id)
        
        return {
            "position": position,
            "execution": execution_result
        }
    
    async def get_user_dashboard_data(self, user_id):
        """Obter dados para dashboard do usuário"""
        # Posições ativas
        positions = await self.database.get_user_positions(user_id, status="open")
        
        # Estratégias do usuário
        strategies = await self.database.get_user_strategies(user_id)
        
        # Performance geral
        all_positions = await self.database.get_user_positions(user_id)
        total_pnl = sum(p.get("pnl", 0) for p in all_positions)
        
        # Dados de mercado dos símbolos ativos
        active_symbols = list(set(p["symbol"] for p in positions))
        market_data = {}
        
        for symbol in active_symbols:
            market_data[symbol] = await self.api.get_market_data(symbol)
        
        return {
            "user_id": user_id,
            "positions": positions,
            "strategies": strategies,
            "performance": {
                "total_pnl": total_pnl,
                "active_positions": len(positions),
                "total_trades": len(all_positions)
            },
            "market_data": market_data,
            "timestamp": datetime.now().isoformat()
        }
    
    async def stop_trading(self, user_id, strategy_id):
        """Parar trading"""
        if strategy_id in self.active_strategies:
            strategy = self.active_strategies[strategy_id]
            await strategy.deactivate()
            
            await self._log_event("INFO", f"Trading parado para estratégia {strategy_id}", user_id)
            
            return {"status": "trading_stopped", "strategy_id": strategy_id}
        
        raise ValueError("Estratégia não encontrada")
    
    async def _setup_market_data_feed(self, symbol):
        """Configurar feed de dados de mercado"""
        if symbol not in self.market_data_feeds:
            # Simular configuração de feed
            feed_config = {
                "symbol": symbol,
                "intervals": ["1m", "5m", "15m"],
                "active": True,
                "last_update": datetime.now().isoformat()
            }
            
            self.market_data_feeds[symbol] = feed_config
            
            # Cache da configuração
            await self.cache.set(f"feed:{symbol}", feed_config, ttl=3600)
    
    async def _log_event(self, level, message, user_id=None):
        """Registrar evento no sistema"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message,
            "user_id": user_id,
            "component": "TradingSystem"
        }
        
        self.system_logs.append(log_entry)
        
        # Salvar no banco se conectado
        if self.database.is_connected:
            await self.database.log_message(level, message, "TradingSystem", user_id)


class StrategyEngine:
    """Engine de estratégias para testes E2E"""
    
    def __init__(self):
        self.strategies = {}
        self.is_initialized = False
    
    async def initialize(self):
        """Inicializar engine"""
        self.is_initialized = True
        return {"status": "initialized"}
    
    async def shutdown(self):
        """Desligar engine"""
        for strategy in self.strategies.values():
            if hasattr(strategy, 'deactivate'):
                await strategy.deactivate()
        
        self.strategies.clear()
        self.is_initialized = False
        return {"status": "shutdown"}
    
    async def create_strategy(self, strategy_id, name, parameters):
        """Criar instância de estratégia"""
        strategy = TradingStrategy(strategy_id, name, parameters)
        await strategy.initialize()
        
        self.strategies[strategy_id] = strategy
        return strategy


class TradingStrategy:
    """Estratégia de trading para testes E2E"""
    
    def __init__(self, strategy_id, name, parameters):
        self.id = strategy_id
        self.name = name
        self.parameters = parameters
        self.is_active = False
        self.symbols = []
        self.positions = {}
    
    async def initialize(self):
        """Inicializar estratégia"""
        return {"status": "initialized", "strategy_id": self.id}
    
    async def activate(self, symbols):
        """Ativar estratégia"""
        self.is_active = True
        self.symbols = symbols
        return {"status": "activated", "symbols": symbols}
    
    async def deactivate(self):
        """Desativar estratégia"""
        self.is_active = False
        self.symbols = []
        return {"status": "deactivated"}
    
    async def analyze_market(self, symbol, market_data):
        """Analisar mercado"""
        # Simulação simples de análise
        signal = "hold"  # Padrão conservador
        
        if "price" in market_data:
            # Lógica básica baseada em preço
            price = market_data["price"]
            if price > 50000:  # BTC acima de 50k
                signal = "sell"
            elif price < 45000:  # BTC abaixo de 45k
                signal = "buy"
        
        return {
            "symbol": symbol,
            "signal": signal,
            "confidence": 0.7,
            "timestamp": datetime.now().isoformat()
        }


class StreamlitDashboard:
    """Simulação do dashboard Streamlit"""
    
    def __init__(self):
        self.api = None
        self.database = None
        self.is_configured = False
        self.pages = {}
    
    def configure(self, api, database):
        """Configurar dashboard"""
        self.api = api
        self.database = database
        self.is_configured = True
        
        # Configurar páginas
        self.pages = {
            "home": HomePage(api, database),
            "trading": TradingPage(api, database),
            "positions": PositionsPage(api, database),
            "strategies": StrategiesPage(api, database),
            "settings": SettingsPage(api, database)
        }
        
        return {"status": "configured", "pages": len(self.pages)}
    
    async def render_page(self, page_name, user_id, **kwargs):
        """Renderizar página"""
        if not self.is_configured:
            raise RuntimeError("Dashboard não configurado")
        
        if page_name not in self.pages:
            raise ValueError(f"Página não encontrada: {page_name}")
        
        page = self.pages[page_name]
        return await page.render(user_id, **kwargs)
    
    async def handle_user_action(self, page_name, action, user_id, **kwargs):
        """Processar ação do usuário"""
        if page_name not in self.pages:
            raise ValueError(f"Página não encontrada: {page_name}")
        
        page = self.pages[page_name]
        return await page.handle_action(action, user_id, **kwargs)


class BasePage:
    """Classe base para páginas do dashboard"""
    
    def __init__(self, api, database):
        self.api = api
        self.database = database
    
    async def render(self, user_id, **kwargs):
        """Renderizar página (implementar nas subclasses)"""
        raise NotImplementedError
    
    async def handle_action(self, action, user_id, **kwargs):
        """Processar ação (implementar nas subclasses)"""
        raise NotImplementedError


class HomePage(BasePage):
    """Página inicial do dashboard"""
    
    async def render(self, user_id, **kwargs):
        """Renderizar página inicial"""
        # Obter dados do usuário
        user = await self.database.get_user(user_id)
        positions = await self.database.get_user_positions(user_id, status="open")
        strategies = await self.database.get_user_strategies(user_id)
        
        return {
            "page": "home",
            "user": user,
            "summary": {
                "active_positions": len(positions),
                "active_strategies": len([s for s in strategies if s.get("is_active")]),
                "total_strategies": len(strategies)
            },
            "recent_activity": positions[-5:] if positions else [],
            "timestamp": datetime.now().isoformat()
        }
    
    async def handle_action(self, action, user_id, **kwargs):
        """Processar ações da página inicial"""
        if action == "refresh_data":
            return await self.render(user_id)
        
        return {"error": f"Ação não reconhecida: {action}"}


class TradingPage(BasePage):
    """Página de trading"""
    
    async def render(self, user_id, **kwargs):
        """Renderizar página de trading"""
        symbol = kwargs.get("symbol", "BTCUSDT")
        
        # Obter dados de mercado
        market_data = await self.api.get_market_data(symbol)
        
        # Obter estratégias ativas
        strategies = await self.database.get_user_strategies(user_id, active_only=True)
        
        return {
            "page": "trading",
            "symbol": symbol,
            "market_data": market_data,
            "strategies": strategies,
            "trading_enabled": True,
            "timestamp": datetime.now().isoformat()
        }
    
    async def handle_action(self, action, user_id, **kwargs):
        """Processar ações de trading"""
        if action == "place_order":
            symbol = kwargs.get("symbol")
            side = kwargs.get("side")
            quantity = kwargs.get("quantity")
            
            if not all([symbol, side, quantity]):
                return {"error": "Parâmetros obrigatórios: symbol, side, quantity"}
            
            # Simular execução de ordem
            market_data = await self.api.get_market_data(symbol)
            
            position = await self.database.create_position(
                user_id=user_id,
                strategy_id=kwargs.get("strategy_id"),
                symbol=symbol,
                side=side,
                size=float(quantity),
                entry_price=market_data["price"]
            )
            
            return {
                "success": True,
                "position": position,
                "message": f"Ordem executada: {side} {quantity} {symbol}"
            }
        
        elif action == "cancel_order":
            # Simular cancelamento
            return {"success": True, "message": "Ordem cancelada"}
        
        return {"error": f"Ação não reconhecida: {action}"}


class PositionsPage(BasePage):
    """Página de posições"""
    
    async def render(self, user_id, **kwargs):
        """Renderizar página de posições"""
        status_filter = kwargs.get("status", "all")
        
        if status_filter == "all":
            positions = await self.database.get_user_positions(user_id)
        else:
            positions = await self.database.get_user_positions(user_id, status=status_filter)
        
        # Calcular métricas
        total_pnl = sum(p.get("pnl", 0) for p in positions)
        open_positions = [p for p in positions if p.get("status") == "open"]
        
        return {
            "page": "positions",
            "positions": positions,
            "metrics": {
                "total_positions": len(positions),
                "open_positions": len(open_positions),
                "total_pnl": total_pnl
            },
            "filter": status_filter,
            "timestamp": datetime.now().isoformat()
        }
    
    async def handle_action(self, action, user_id, **kwargs):
        """Processar ações de posições"""
        if action == "close_position":
            position_id = kwargs.get("position_id")
            exit_price = kwargs.get("exit_price", 50000.0)
            
            if not position_id:
                return {"error": "position_id é obrigatório"}
            
            # Simular fechamento
            closed_position = await self.database.close_position(
                position_id=position_id,
                exit_price=exit_price,
                pnl=kwargs.get("pnl", 0),
                fees=kwargs.get("fees", 0)
            )
            
            return {
                "success": True,
                "position": closed_position,
                "message": f"Posição {position_id} fechada"
            }
        
        return {"error": f"Ação não reconhecida: {action}"}


class StrategiesPage(BasePage):
    """Página de estratégias"""
    
    async def render(self, user_id, **kwargs):
        """Renderizar página de estratégias"""
        strategies = await self.database.get_user_strategies(user_id, active_only=False)
        
        return {
            "page": "strategies",
            "strategies": strategies,
            "available_types": ["ppp_vishva", "sma_crossover", "rsi_divergence"],
            "timestamp": datetime.now().isoformat()
        }
    
    async def handle_action(self, action, user_id, **kwargs):
        """Processar ações de estratégias"""
        if action == "create_strategy":
            name = kwargs.get("name")
            strategy_type = kwargs.get("type", "ppp_vishva")
            parameters = kwargs.get("parameters", {})
            
            if not name:
                return {"error": "Nome da estratégia é obrigatório"}
            
            strategy = await self.database.create_strategy(
                user_id=user_id,
                name=name,
                strategy_type=strategy_type,
                parameters=parameters
            )
            
            return {
                "success": True,
                "strategy": strategy,
                "message": f"Estratégia '{name}' criada"
            }
        
        elif action == "delete_strategy":
            strategy_id = kwargs.get("strategy_id")
            
            if not strategy_id:
                return {"error": "strategy_id é obrigatório"}
            
            # Simular exclusão (marcar como inativa)
            return {
                "success": True,
                "message": f"Estratégia {strategy_id} removida"
            }
        
        return {"error": f"Ação não reconhecida: {action}"}


class SettingsPage(BasePage):
    """Página de configurações"""
    
    async def render(self, user_id, **kwargs):
        """Renderizar página de configurações"""
        user = await self.database.get_user(user_id)
        
        return {
            "page": "settings",
            "user": user,
            "settings": {
                "notifications": True,
                "risk_management": True,
                "auto_trading": False
            },
            "timestamp": datetime.now().isoformat()
        }
    
    async def handle_action(self, action, user_id, **kwargs):
        """Processar ações de configurações"""
        if action == "update_settings":
            settings = kwargs.get("settings", {})
            
            return {
                "success": True,
                "settings": settings,
                "message": "Configurações atualizadas"
            }
        
        return {"error": f"Ação não reconhecida: {action}"}


class TestUserFlows:
    """Testes de fluxos completos de usuário"""
    
    @pytest.mark.asyncio
    async def test_complete_user_journey(self):
        """Testa jornada completa do usuário"""
        system = TradingSystem()
        
        try:
            # 1. Inicializar sistema
            init_result = await system.initialize()
            assert init_result["status"] == "initialized"
            assert init_result["components"] == 4
            
            # 2. Criar conta de usuário
            user = await system.create_user_account(
                username="trader_e2e",
                email="trader@e2e.com",
                password="secure_password"
            )
            
            assert user["username"] == "trader_e2e"
            assert user["email"] == "trader@e2e.com"
            
            # 3. Login do usuário
            login_result = await system.user_login("trader_e2e", "secure_password")
            assert login_result["user"]["id"] == user["id"]
            assert "session" in login_result
            
            # 4. Configurar estratégia
            strategy_params = {
                "risk_per_trade": 0.02,
                "max_positions": 3,
                "stop_loss": 0.05,
                "take_profit": 0.10
            }
            
            strategy = await system.configure_strategy(
                user_id=user["id"],
                strategy_name="E2E PPP Vishva",
                parameters=strategy_params
            )
            
            assert strategy["name"] == "E2E PPP Vishva"
            assert strategy["parameters"]["risk_per_trade"] == 0.02
            
            # 5. Iniciar trading
            trading_result = await system.start_trading(
                user_id=user["id"],
                strategy_id=strategy["id"],
                symbols=["BTCUSDT", "ETHUSDT"]
            )
            
            assert trading_result["status"] == "trading_started"
            assert len(trading_result["symbols"]) == 2
            
            # 6. Executar trades
            trade1 = await system.execute_trade(
                user_id=user["id"],
                symbol="BTCUSDT",
                side="buy",
                quantity=0.1,
                strategy_id=strategy["id"]
            )
            
            assert trade1["position"]["symbol"] == "BTCUSDT"
            assert trade1["position"]["side"] == "buy"
            assert trade1["execution"]["status"] == "filled"
            
            trade2 = await system.execute_trade(
                user_id=user["id"],
                symbol="ETHUSDT",
                side="sell",
                quantity=1.0,
                strategy_id=strategy["id"]
            )
            
            assert trade2["position"]["symbol"] == "ETHUSDT"
            assert trade2["position"]["side"] == "sell"
            
            # 7. Verificar dashboard
            dashboard_data = await system.get_user_dashboard_data(user["id"])
            
            assert dashboard_data["user_id"] == user["id"]
            assert len(dashboard_data["positions"]) == 2
            assert len(dashboard_data["strategies"]) == 1
            assert dashboard_data["performance"]["active_positions"] == 2
            
            # 8. Parar trading
            stop_result = await system.stop_trading(user["id"], strategy["id"])
            assert stop_result["status"] == "trading_stopped"
            
            # 9. Verificar logs do sistema
            assert len(system.system_logs) > 0
            
            # Verificar eventos específicos
            log_messages = [log["message"] for log in system.system_logs]
            assert any("Sistema inicializado" in msg for msg in log_messages)
            assert any("Usuário criado" in msg for msg in log_messages)
            assert any("Login realizado" in msg for msg in log_messages)
            assert any("Estratégia configurada" in msg for msg in log_messages)
            assert any("Trading iniciado" in msg for msg in log_messages)
            
        finally:
            await system.shutdown()
    
    @pytest.mark.asyncio
    async def test_dashboard_interaction_flow(self):
        """Testa fluxo de interação com dashboard"""
        system = TradingSystem()
        
        try:
            await system.initialize()
            
            # Criar usuário
            user = await system.create_user_account("dashboard_user", "dash@test.com", "pass")
            
            # Testar todas as páginas do dashboard
            dashboard = system.dashboard
            
            # 1. Página inicial
            home_data = await dashboard.render_page("home", user["id"])
            assert home_data["page"] == "home"
            assert home_data["user"]["username"] == "dashboard_user"
            assert "summary" in home_data
            
            # 2. Página de trading
            trading_data = await dashboard.render_page("trading", user["id"], symbol="BTCUSDT")
            assert trading_data["page"] == "trading"
            assert trading_data["symbol"] == "BTCUSDT"
            assert "market_data" in trading_data
            
            # 3. Executar ordem via dashboard
            order_result = await dashboard.handle_user_action(
                "trading", "place_order", user["id"],
                symbol="BTCUSDT", side="buy", quantity="0.1"
            )
            
            assert order_result["success"] is True
            assert "position" in order_result
            
            # 4. Página de posições
            positions_data = await dashboard.render_page("positions", user["id"])
            assert positions_data["page"] == "positions"
            assert len(positions_data["positions"]) == 1
            assert positions_data["metrics"]["total_positions"] == 1
            
            # 5. Fechar posição via dashboard
            position_id = positions_data["positions"][0]["id"]
            close_result = await dashboard.handle_user_action(
                "positions", "close_position", user["id"],
                position_id=position_id, exit_price=51000.0
            )
            
            assert close_result["success"] is True
            
            # 6. Página de estratégias
            strategies_data = await dashboard.render_page("strategies", user["id"])
            assert strategies_data["page"] == "strategies"
            assert "available_types" in strategies_data
            
            # 7. Criar estratégia via dashboard
            strategy_result = await dashboard.handle_user_action(
                "strategies", "create_strategy", user["id"],
                name="Dashboard Strategy", type="ppp_vishva",
                parameters={"risk_per_trade": 0.01}
            )
            
            assert strategy_result["success"] is True
            assert strategy_result["strategy"]["name"] == "Dashboard Strategy"
            
            # 8. Página de configurações
            settings_data = await dashboard.render_page("settings", user["id"])
            assert settings_data["page"] == "settings"
            assert settings_data["user"]["id"] == user["id"]
            
        finally:
            await system.shutdown()
    
    @pytest.mark.asyncio
    async def test_multi_user_concurrent_flow(self):
        """Testa fluxo com múltiplos usuários concorrentes"""
        system = TradingSystem()
        
        try:
            await system.initialize()
            
            # Criar múltiplos usuários
            users = []
            for i in range(3):
                user = await system.create_user_account(
                    f"user_{i}", f"user{i}@test.com", "password"
                )
                users.append(user)
            
            # Configurar estratégias para cada usuário
            strategies = []
            for i, user in enumerate(users):
                strategy = await system.configure_strategy(
                    user_id=user["id"],
                    strategy_name=f"Strategy User {i}",
                    parameters={"risk_per_trade": 0.01 * (i + 1)}
                )
                strategies.append(strategy)
            
            # Iniciar trading concorrente
            trading_tasks = []
            for i, (user, strategy) in enumerate(zip(users, strategies)):
                symbols = ["BTCUSDT"] if i == 0 else ["ETHUSDT"] if i == 1 else ["BTCUSDT", "ETHUSDT"]
                task = system.start_trading(user["id"], strategy["id"], symbols)
                trading_tasks.append(task)
            
            trading_results = await asyncio.gather(*trading_tasks)
            
            # Verificar que todos iniciaram
            for result in trading_results:
                assert result["status"] == "trading_started"
            
            # Executar trades concorrentes
            trade_tasks = []
            for i, user in enumerate(users):
                symbol = "BTCUSDT" if i % 2 == 0 else "ETHUSDT"
                side = "buy" if i % 2 == 0 else "sell"
                
                task = system.execute_trade(
                    user_id=user["id"],
                    symbol=symbol,
                    side=side,
                    quantity=0.1 * (i + 1),
                    strategy_id=strategies[i]["id"]
                )
                trade_tasks.append(task)
            
            trade_results = await asyncio.gather(*trade_tasks)
            
            # Verificar execuções
            for i, result in enumerate(trade_results):
                assert result["execution"]["status"] == "filled"
                assert result["position"]["user_id"] == users[i]["id"]
            
            # Verificar dados do dashboard para cada usuário
            dashboard_tasks = []
            for user in users:
                task = system.get_user_dashboard_data(user["id"])
                dashboard_tasks.append(task)
            
            dashboard_results = await asyncio.gather(*dashboard_tasks)
            
            # Cada usuário deve ter seus próprios dados
            for i, data in enumerate(dashboard_results):
                assert data["user_id"] == users[i]["id"]
                assert len(data["positions"]) == 1  # Cada um fez 1 trade
                assert len(data["strategies"]) == 1  # Cada um tem 1 estratégia
            
            # Parar trading para todos
            stop_tasks = []
            for user, strategy in zip(users, strategies):
                task = system.stop_trading(user["id"], strategy["id"])
                stop_tasks.append(task)
            
            stop_results = await asyncio.gather(*stop_tasks)
            
            for result in stop_results:
                assert result["status"] == "trading_stopped"
            
        finally:
            await system.shutdown()
    
    @pytest.mark.asyncio
    async def test_error_recovery_flow(self):
        """Testa fluxo de recuperação de erros"""
        system = TradingSystem()
        
        try:
            await system.initialize()
            
            # 1. Tentar operações sem usuário
            with pytest.raises(ValueError, match="Usuário não encontrado"):
                await system.configure_strategy(999, "Invalid Strategy", {})
            
            # 2. Criar usuário válido
            user = await system.create_user_account("error_user", "error@test.com", "pass")
            
            # 3. Tentar login com credenciais inválidas
            with pytest.raises(ValueError, match="Usuário não encontrado"):
                await system.user_login("invalid_user", "wrong_pass")
            
            # 4. Login válido
            login_result = await system.user_login("error_user", "pass")
            assert login_result["user"]["id"] == user["id"]
            
            # 5. Configurar estratégia
            strategy = await system.configure_strategy(
                user_id=user["id"],
                strategy_name="Error Recovery Strategy",
                parameters={"risk_per_trade": 0.02}
            )
            
            # 6. Tentar iniciar trading com estratégia inválida
            with pytest.raises(ValueError, match="Estratégia não encontrada"):
                await system.start_trading(user["id"], 999, ["BTCUSDT"])
            
            # 7. Iniciar trading válido
            trading_result = await system.start_trading(
                user["id"], strategy["id"], ["BTCUSDT"]
            )
            assert trading_result["status"] == "trading_started"
            
            # 8. Tentar parar trading com estratégia inválida
            with pytest.raises(ValueError, match="Estratégia não encontrada"):
                await system.stop_trading(user["id"], 999)
            
            # 9. Parar trading válido
            stop_result = await system.stop_trading(user["id"], strategy["id"])
            assert stop_result["status"] == "trading_stopped"
            
            # 10. Verificar que o sistema continua funcionando após erros
            dashboard_data = await system.get_user_dashboard_data(user["id"])
            assert dashboard_data["user_id"] == user["id"]
            
            # 11. Verificar logs de erro
            error_logs = [log for log in system.system_logs if log["level"] == "ERROR"]
            # Pode não haver logs de ERROR se os erros foram tratados com exceções
            
        finally:
            await system.shutdown()
    
    @pytest.mark.asyncio
    async def test_performance_under_load(self):
        """Testa performance sob carga"""
        system = TradingSystem()
        
        try:
            await system.initialize()
            
            # Criar usuário
            user = await system.create_user_account("perf_user", "perf@test.com", "pass")
            
            # Configurar estratégia
            strategy = await system.configure_strategy(
                user_id=user["id"],
                strategy_name="Performance Strategy",
                parameters={"risk_per_trade": 0.01}
            )
            
            # Iniciar trading
            await system.start_trading(user["id"], strategy["id"], ["BTCUSDT", "ETHUSDT"])
            
            # Teste de performance: múltiplas operações
            start_time = time.time()
            
            # Executar múltiplos trades
            trade_tasks = []
            for i in range(20):  # 20 trades
                symbol = "BTCUSDT" if i % 2 == 0 else "ETHUSDT"
                side = "buy" if i % 2 == 0 else "sell"
                
                task = system.execute_trade(
                    user_id=user["id"],
                    symbol=symbol,
                    side=side,
                    quantity=0.01,
                    strategy_id=strategy["id"]
                )
                trade_tasks.append(task)
            
            trade_results = await asyncio.gather(*trade_tasks)
            
            # Múltiplas consultas ao dashboard
            dashboard_tasks = []
            for _ in range(10):
                task = system.get_user_dashboard_data(user["id"])
                dashboard_tasks.append(task)
            
            dashboard_results = await asyncio.gather(*dashboard_tasks)
            
            total_time = time.time() - start_time
            
            # Verificar resultados
            assert len(trade_results) == 20
            assert len(dashboard_results) == 10
            
            # Todos os trades devem ter sido executados
            for result in trade_results:
                assert result["execution"]["status"] == "filled"
            
            # Todas as consultas devem retornar dados válidos
            for data in dashboard_results:
                assert data["user_id"] == user["id"]
                assert len(data["positions"]) == 20  # 20 trades executados
            
            # Performance deve ser razoável
            assert total_time < 5.0  # Menos de 5 segundos para 30 operações
            
            # Verificar integridade dos dados
            final_dashboard = await system.get_user_dashboard_data(user["id"])
            assert final_dashboard["performance"]["total_trades"] == 20
            assert final_dashboard["performance"]["active_positions"] == 20
            
        finally:
            await system.shutdown()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

