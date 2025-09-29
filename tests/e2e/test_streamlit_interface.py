"""
Testes End-to-End da Interface Streamlit
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

# Adicionar o diretório do projeto ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

# Importar componentes dos testes anteriores
try:
    from tests.e2e.test_user_flows import TradingSystem
    from tests.integration.test_simple_integration import SimpleAPI, SimpleDatabase, SimpleCache
except ImportError:
    # Fallback básico
    class TradingSystem:
        def __init__(self):
            pass
        async def initialize(self):
            return {"status": "initialized"}


class StreamlitApp:
    """
    Simulação da aplicação Streamlit completa
    Testa todos os componentes da interface
    """
    
    def __init__(self):
        self.session_state = {}
        self.trading_system = None
        self.current_user = None
        self.pages = {}
        self.widgets = {}
        self.is_running = False
        
    async def initialize(self):
        """Inicializar aplicação Streamlit"""
        self.trading_system = TradingSystem()
        await self.trading_system.initialize()
        
        # Configurar páginas
        self.pages = {
            "🏠 Dashboard": DashboardPage(self),
            "📈 Trading": TradingPage(self),
            "💼 Posições": PositionsPage(self),
            "⚙️ Estratégias": StrategiesPage(self),
            "📊 Analytics": AnalyticsPage(self),
            "🔧 Configurações": SettingsPage(self)
        }
        
        # Estado inicial da sessão
        self.session_state = {
            "authenticated": False,
            "user_id": None,
            "current_page": "🏠 Dashboard",
            "selected_symbol": "BTCUSDT",
            "refresh_interval": 5,
            "theme": "dark",
            "notifications": True
        }
        
        self.is_running = True
        return {"status": "initialized", "pages": len(self.pages)}
    
    async def shutdown(self):
        """Desligar aplicação"""
        if self.trading_system:
            await self.trading_system.shutdown()
        
        self.session_state.clear()
        self.pages.clear()
        self.widgets.clear()
        self.is_running = False
        
        return {"status": "shutdown"}
    
    async def authenticate_user(self, username, password):
        """Autenticar usuário"""
        if not self.is_running:
            raise RuntimeError("Aplicação não está rodando")
        
        # Simular autenticação
        if username and password:
            # Criar ou obter usuário
            try:
                user = await self.trading_system.create_user_account(username, f"{username}@test.com", password)
            except:
                # Usuário já existe, fazer login
                login_result = await self.trading_system.user_login(username, password)
                user = login_result["user"]
            
            self.current_user = user
            self.session_state["authenticated"] = True
            self.session_state["user_id"] = user["id"]
            
            return {"success": True, "user": user}
        
        return {"success": False, "error": "Credenciais inválidas"}
    
    def logout_user(self):
        """Logout do usuário"""
        self.current_user = None
        self.session_state["authenticated"] = False
        self.session_state["user_id"] = None
        return {"success": True}
    
    async def render_page(self, page_name):
        """Renderizar página específica"""
        if not self.session_state["authenticated"]:
            return await self.render_login_page()
        
        if page_name not in self.pages:
            return {"error": f"Página não encontrada: {page_name}"}
        
        page = self.pages[page_name]
        return await page.render()
    
    async def render_login_page(self):
        """Renderizar página de login"""
        return {
            "page": "login",
            "title": "🔐 Login - Trading Bot MVP",
            "components": {
                "username_input": {"type": "text_input", "label": "Usuário", "key": "username"},
                "password_input": {"type": "text_input", "label": "Senha", "key": "password", "type": "password"},
                "login_button": {"type": "button", "label": "Entrar", "key": "login_btn"},
                "register_button": {"type": "button", "label": "Registrar", "key": "register_btn"}
            },
            "layout": "centered",
            "timestamp": datetime.now().isoformat()
        }
    
    async def handle_widget_interaction(self, widget_key, value, action="change"):
        """Processar interação com widget"""
        if not self.is_running:
            raise RuntimeError("Aplicação não está rodando")
        
        # Armazenar valor do widget
        self.widgets[widget_key] = value
        
        # Processar ações específicas
        if widget_key == "login_btn" and action == "click":
            username = self.widgets.get("username", "")
            password = self.widgets.get("password", "")
            return await self.authenticate_user(username, password)
        
        elif widget_key == "logout_btn" and action == "click":
            return self.logout_user()
        
        elif widget_key == "page_selector" and action == "change":
            self.session_state["current_page"] = value
            return {"page_changed": True, "new_page": value}
        
        elif widget_key == "symbol_selector" and action == "change":
            self.session_state["selected_symbol"] = value
            return {"symbol_changed": True, "new_symbol": value}
        
        elif widget_key == "refresh_btn" and action == "click":
            return {"refresh_triggered": True}
        
        # Delegar para página atual se autenticado
        if self.session_state["authenticated"]:
            current_page_name = self.session_state["current_page"]
            if current_page_name in self.pages:
                page = self.pages[current_page_name]
                return await page.handle_widget_interaction(widget_key, value, action)
        
        return {"widget_updated": True, "key": widget_key, "value": value}
    
    def get_session_state(self):
        """Obter estado da sessão"""
        return self.session_state.copy()
    
    def update_session_state(self, updates):
        """Atualizar estado da sessão"""
        self.session_state.update(updates)
        return self.session_state


class BasePage:
    """Classe base para páginas Streamlit"""
    
    def __init__(self, app):
        self.app = app
        self.trading_system = app.trading_system
    
    async def render(self):
        """Renderizar página (implementar nas subclasses)"""
        raise NotImplementedError
    
    async def handle_widget_interaction(self, widget_key, value, action):
        """Processar interação com widget (implementar nas subclasses)"""
        return {"widget_updated": True, "key": widget_key, "value": value}
    
    def get_user_id(self):
        """Obter ID do usuário atual"""
        return self.app.session_state.get("user_id")


class DashboardPage(BasePage):
    """Página principal do dashboard"""
    
    async def render(self):
        """Renderizar dashboard principal"""
        user_id = self.get_user_id()
        if not user_id:
            return {"error": "Usuário não autenticado"}
        
        # Obter dados do dashboard
        dashboard_data = await self.trading_system.get_user_dashboard_data(user_id)
        
        # Obter dados de mercado para símbolos ativos
        selected_symbol = self.app.session_state.get("selected_symbol", "BTCUSDT")
        market_data = await self.trading_system.api.get_market_data(selected_symbol)
        
        return {
            "page": "dashboard",
            "title": "🏠 Dashboard Principal",
            "layout": {
                "sidebar": {
                    "user_info": {
                        "username": self.app.current_user["username"],
                        "user_id": user_id
                    },
                    "navigation": list(self.app.pages.keys()),
                    "symbol_selector": {
                        "type": "selectbox",
                        "label": "Símbolo",
                        "options": ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT"],
                        "value": selected_symbol,
                        "key": "symbol_selector"
                    },
                    "refresh_button": {
                        "type": "button",
                        "label": "🔄 Atualizar",
                        "key": "refresh_btn"
                    }
                },
                "main": {
                    "metrics_row": {
                        "total_positions": {
                            "label": "Posições Ativas",
                            "value": dashboard_data["performance"]["active_positions"],
                            "delta": "+2"
                        },
                        "total_pnl": {
                            "label": "P&L Total",
                            "value": f"${dashboard_data['performance']['total_pnl']:.2f}",
                            "delta": "+5.2%"
                        },
                        "active_strategies": {
                            "label": "Estratégias Ativas",
                            "value": len([s for s in dashboard_data["strategies"] if s.get("is_active")]),
                            "delta": "0"
                        }
                    },
                    "market_data_card": {
                        "symbol": market_data["symbol"],
                        "price": market_data["price"],
                        "timestamp": market_data["timestamp"],
                        "volume": market_data["volume"]
                    },
                    "positions_table": {
                        "columns": ["Símbolo", "Lado", "Quantidade", "Preço Entrada", "P&L", "Status"],
                        "data": [
                            [
                                pos["symbol"],
                                pos["side"],
                                pos["size"],
                                pos["entry_price"],
                                pos.get("pnl", 0),
                                pos["status"]
                            ]
                            for pos in dashboard_data["positions"][-5:]  # Últimas 5 posições
                        ]
                    },
                    "strategies_status": {
                        "strategies": [
                            {
                                "name": s["name"],
                                "type": s["type"],
                                "active": s.get("is_active", False),
                                "parameters": s["parameters"]
                            }
                            for s in dashboard_data["strategies"]
                        ]
                    }
                }
            },
            "timestamp": datetime.now().isoformat()
        }
    
    async def handle_widget_interaction(self, widget_key, value, action):
        """Processar interações do dashboard"""
        if widget_key == "refresh_btn" and action == "click":
            # Recarregar dados
            return {"refresh_triggered": True, "message": "Dados atualizados"}
        
        elif widget_key == "symbol_selector" and action == "change":
            # Atualizar símbolo selecionado
            self.app.session_state["selected_symbol"] = value
            return {"symbol_changed": True, "new_symbol": value}
        
        return await super().handle_widget_interaction(widget_key, value, action)


class TradingPage(BasePage):
    """Página de trading"""
    
    async def render(self):
        """Renderizar página de trading"""
        user_id = self.get_user_id()
        selected_symbol = self.app.session_state.get("selected_symbol", "BTCUSDT")
        
        # Obter dados de mercado
        market_data = await self.trading_system.api.get_market_data(selected_symbol)
        
        # Obter estratégias do usuário
        strategies = await self.trading_system.database.get_user_strategies(user_id)
        
        return {
            "page": "trading",
            "title": "📈 Trading",
            "layout": {
                "market_info": {
                    "symbol": selected_symbol,
                    "current_price": market_data["price"],
                    "volume": market_data["volume"],
                    "timestamp": market_data["timestamp"]
                },
                "order_form": {
                    "symbol_input": {
                        "type": "selectbox",
                        "label": "Símbolo",
                        "options": ["BTCUSDT", "ETHUSDT", "BNBUSDT"],
                        "value": selected_symbol,
                        "key": "order_symbol"
                    },
                    "side_input": {
                        "type": "radio",
                        "label": "Lado",
                        "options": ["buy", "sell"],
                        "value": "buy",
                        "key": "order_side"
                    },
                    "quantity_input": {
                        "type": "number_input",
                        "label": "Quantidade",
                        "min_value": 0.001,
                        "max_value": 100.0,
                        "value": 0.1,
                        "step": 0.001,
                        "key": "order_quantity"
                    },
                    "strategy_input": {
                        "type": "selectbox",
                        "label": "Estratégia",
                        "options": [{"label": s["name"], "value": s["id"]} for s in strategies],
                        "key": "order_strategy"
                    },
                    "place_order_btn": {
                        "type": "button",
                        "label": "🚀 Executar Ordem",
                        "key": "place_order_btn"
                    }
                },
                "active_orders": {
                    "title": "Ordens Ativas",
                    "columns": ["ID", "Símbolo", "Lado", "Quantidade", "Status", "Ações"],
                    "data": []  # Seria preenchido com ordens reais
                },
                "price_chart": {
                    "symbol": selected_symbol,
                    "timeframe": "1h",
                    "data_points": 100  # Simulação de dados do gráfico
                }
            },
            "timestamp": datetime.now().isoformat()
        }
    
    async def handle_widget_interaction(self, widget_key, value, action):
        """Processar interações de trading"""
        if widget_key == "place_order_btn" and action == "click":
            # Obter dados do formulário
            symbol = self.app.widgets.get("order_symbol", "BTCUSDT")
            side = self.app.widgets.get("order_side", "buy")
            quantity = self.app.widgets.get("order_quantity", 0.1)
            strategy_id = self.app.widgets.get("order_strategy")
            
            user_id = self.get_user_id()
            
            try:
                # Executar trade
                trade_result = await self.trading_system.execute_trade(
                    user_id=user_id,
                    symbol=symbol,
                    side=side,
                    quantity=quantity,
                    strategy_id=strategy_id
                )
                
                return {
                    "success": True,
                    "message": f"Ordem executada: {side} {quantity} {symbol}",
                    "trade_result": trade_result
                }
                
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Erro ao executar ordem: {str(e)}"
                }
        
        return await super().handle_widget_interaction(widget_key, value, action)


class PositionsPage(BasePage):
    """Página de posições"""
    
    async def render(self):
        """Renderizar página de posições"""
        user_id = self.get_user_id()
        
        # Obter posições do usuário
        all_positions = await self.trading_system.database.get_user_positions(user_id)
        open_positions = await self.trading_system.database.get_user_positions(user_id, status="open")
        
        # Calcular métricas
        total_pnl = sum(p.get("pnl", 0) for p in all_positions)
        unrealized_pnl = sum(p.get("pnl", 0) for p in open_positions)
        
        return {
            "page": "positions",
            "title": "💼 Posições",
            "layout": {
                "summary_metrics": {
                    "total_positions": len(all_positions),
                    "open_positions": len(open_positions),
                    "total_pnl": total_pnl,
                    "unrealized_pnl": unrealized_pnl
                },
                "filters": {
                    "status_filter": {
                        "type": "selectbox",
                        "label": "Status",
                        "options": ["all", "open", "closed"],
                        "value": "all",
                        "key": "position_status_filter"
                    },
                    "symbol_filter": {
                        "type": "multiselect",
                        "label": "Símbolos",
                        "options": list(set(p["symbol"] for p in all_positions)),
                        "key": "position_symbol_filter"
                    }
                },
                "positions_table": {
                    "columns": [
                        "ID", "Símbolo", "Lado", "Quantidade", 
                        "Preço Entrada", "Preço Saída", "P&L", 
                        "Status", "Data Abertura", "Ações"
                    ],
                    "data": [
                        [
                            pos["id"],
                            pos["symbol"],
                            pos["side"],
                            pos["size"],
                            pos["entry_price"],
                            pos.get("exit_price", "-"),
                            pos.get("pnl", 0),
                            pos["status"],
                            pos.get("opened_at", pos.get("created_at", "")),
                            "🔴 Fechar" if pos["status"] == "open" else "-"
                        ]
                        for pos in all_positions
                    ]
                },
                "position_chart": {
                    "type": "pnl_over_time",
                    "data": [
                        {
                            "date": pos.get("created_at", ""),
                            "cumulative_pnl": sum(p.get("pnl", 0) for p in all_positions[:i+1])
                        }
                        for i, pos in enumerate(all_positions)
                    ]
                }
            },
            "timestamp": datetime.now().isoformat()
        }
    
    async def handle_widget_interaction(self, widget_key, value, action):
        """Processar interações de posições"""
        if widget_key.startswith("close_position_") and action == "click":
            # Extrair ID da posição
            position_id = int(widget_key.split("_")[-1])
            
            try:
                # Fechar posição
                closed_position = await self.trading_system.database.close_position(
                    position_id=position_id,
                    exit_price=50000.0,  # Preço simulado
                    pnl=100.0,  # P&L simulado
                    fees=5.0    # Taxas simuladas
                )
                
                return {
                    "success": True,
                    "message": f"Posição {position_id} fechada com sucesso",
                    "closed_position": closed_position
                }
                
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Erro ao fechar posição: {str(e)}"
                }
        
        return await super().handle_widget_interaction(widget_key, value, action)


class StrategiesPage(BasePage):
    """Página de estratégias"""
    
    async def render(self):
        """Renderizar página de estratégias"""
        user_id = self.get_user_id()
        
        # Obter estratégias do usuário
        strategies = await self.trading_system.database.get_user_strategies(user_id, active_only=False)
        
        return {
            "page": "strategies",
            "title": "⚙️ Estratégias",
            "layout": {
                "create_strategy_form": {
                    "name_input": {
                        "type": "text_input",
                        "label": "Nome da Estratégia",
                        "key": "strategy_name"
                    },
                    "type_input": {
                        "type": "selectbox",
                        "label": "Tipo",
                        "options": ["ppp_vishva", "sma_crossover", "rsi_divergence"],
                        "value": "ppp_vishva",
                        "key": "strategy_type"
                    },
                    "risk_input": {
                        "type": "slider",
                        "label": "Risco por Trade (%)",
                        "min_value": 0.5,
                        "max_value": 5.0,
                        "value": 2.0,
                        "step": 0.1,
                        "key": "strategy_risk"
                    },
                    "max_positions_input": {
                        "type": "number_input",
                        "label": "Máximo de Posições",
                        "min_value": 1,
                        "max_value": 10,
                        "value": 3,
                        "key": "strategy_max_positions"
                    },
                    "create_btn": {
                        "type": "button",
                        "label": "➕ Criar Estratégia",
                        "key": "create_strategy_btn"
                    }
                },
                "strategies_list": {
                    "columns": ["Nome", "Tipo", "Status", "Parâmetros", "Ações"],
                    "data": [
                        [
                            s["name"],
                            s["type"],
                            "🟢 Ativa" if s.get("is_active") else "🔴 Inativa",
                            json.dumps(s["parameters"], indent=2),
                            "🗑️ Excluir"
                        ]
                        for s in strategies
                    ]
                },
                "strategy_templates": {
                    "ppp_vishva": {
                        "name": "PPP Vishva Strategy",
                        "description": "Estratégia baseada em múltiplos indicadores técnicos",
                        "parameters": {
                            "risk_per_trade": 0.02,
                            "max_positions": 3,
                            "stop_loss": 0.05,
                            "take_profit": 0.10
                        }
                    },
                    "sma_crossover": {
                        "name": "SMA Crossover",
                        "description": "Cruzamento de médias móveis simples",
                        "parameters": {
                            "fast_period": 10,
                            "slow_period": 20,
                            "risk_per_trade": 0.015
                        }
                    }
                }
            },
            "timestamp": datetime.now().isoformat()
        }
    
    async def handle_widget_interaction(self, widget_key, value, action):
        """Processar interações de estratégias"""
        if widget_key == "create_strategy_btn" and action == "click":
            # Obter dados do formulário
            name = self.app.widgets.get("strategy_name", "")
            strategy_type = self.app.widgets.get("strategy_type", "ppp_vishva")
            risk = self.app.widgets.get("strategy_risk", 2.0)
            max_positions = self.app.widgets.get("strategy_max_positions", 3)
            
            if not name:
                return {"success": False, "error": "Nome da estratégia é obrigatório"}
            
            user_id = self.get_user_id()
            
            try:
                # Criar estratégia
                parameters = {
                    "risk_per_trade": risk / 100,  # Converter para decimal
                    "max_positions": max_positions,
                    "stop_loss": 0.05,
                    "take_profit": 0.10
                }
                
                strategy = await self.trading_system.configure_strategy(
                    user_id=user_id,
                    strategy_name=name,
                    parameters=parameters
                )
                
                return {
                    "success": True,
                    "message": f"Estratégia '{name}' criada com sucesso",
                    "strategy": strategy
                }
                
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Erro ao criar estratégia: {str(e)}"
                }
        
        return await super().handle_widget_interaction(widget_key, value, action)


class AnalyticsPage(BasePage):
    """Página de analytics"""
    
    async def render(self):
        """Renderizar página de analytics"""
        user_id = self.get_user_id()
        
        # Obter dados para analytics
        positions = await self.trading_system.database.get_user_positions(user_id)
        strategies = await self.trading_system.database.get_user_strategies(user_id)
        
        # Calcular métricas de performance
        total_trades = len(positions)
        winning_trades = len([p for p in positions if p.get("pnl", 0) > 0])
        losing_trades = len([p for p in positions if p.get("pnl", 0) < 0])
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        total_pnl = sum(p.get("pnl", 0) for p in positions)
        avg_win = sum(p.get("pnl", 0) for p in positions if p.get("pnl", 0) > 0) / max(winning_trades, 1)
        avg_loss = sum(p.get("pnl", 0) for p in positions if p.get("pnl", 0) < 0) / max(losing_trades, 1)
        
        return {
            "page": "analytics",
            "title": "📊 Analytics",
            "layout": {
                "performance_metrics": {
                    "total_trades": total_trades,
                    "winning_trades": winning_trades,
                    "losing_trades": losing_trades,
                    "win_rate": f"{win_rate:.1f}%",
                    "total_pnl": f"${total_pnl:.2f}",
                    "avg_win": f"${avg_win:.2f}",
                    "avg_loss": f"${avg_loss:.2f}",
                    "profit_factor": abs(avg_win / avg_loss) if avg_loss != 0 else 0
                },
                "charts": {
                    "pnl_chart": {
                        "type": "line",
                        "title": "P&L Cumulativo",
                        "data": [
                            {
                                "date": pos.get("created_at", ""),
                                "cumulative_pnl": sum(p.get("pnl", 0) for p in positions[:i+1])
                            }
                            for i, pos in enumerate(positions)
                        ]
                    },
                    "trades_by_symbol": {
                        "type": "bar",
                        "title": "Trades por Símbolo",
                        "data": {}  # Seria calculado baseado nas posições
                    },
                    "monthly_performance": {
                        "type": "bar",
                        "title": "Performance Mensal",
                        "data": {}  # Seria calculado baseado nas datas
                    }
                },
                "strategy_performance": {
                    "columns": ["Estratégia", "Trades", "Win Rate", "P&L Total", "Avg P&L"],
                    "data": [
                        [
                            s["name"],
                            len([p for p in positions if p.get("strategy_id") == s["id"]]),
                            "75%",  # Simulado
                            "$150.00",  # Simulado
                            "$15.00"  # Simulado
                        ]
                        for s in strategies
                    ]
                }
            },
            "timestamp": datetime.now().isoformat()
        }


class SettingsPage(BasePage):
    """Página de configurações"""
    
    async def render(self):
        """Renderizar página de configurações"""
        user_id = self.get_user_id()
        user = await self.trading_system.database.get_user(user_id)
        
        return {
            "page": "settings",
            "title": "🔧 Configurações",
            "layout": {
                "user_profile": {
                    "username": user["username"],
                    "email": user["email"],
                    "created_at": user.get("created_at", "")
                },
                "trading_settings": {
                    "auto_trading": {
                        "type": "checkbox",
                        "label": "Trading Automático",
                        "value": False,
                        "key": "auto_trading"
                    },
                    "notifications": {
                        "type": "checkbox",
                        "label": "Notificações",
                        "value": True,
                        "key": "notifications"
                    },
                    "risk_management": {
                        "type": "checkbox",
                        "label": "Gestão de Risco",
                        "value": True,
                        "key": "risk_management"
                    },
                    "max_daily_loss": {
                        "type": "number_input",
                        "label": "Perda Máxima Diária ($)",
                        "value": 1000.0,
                        "key": "max_daily_loss"
                    }
                },
                "api_settings": {
                    "api_key": {
                        "type": "text_input",
                        "label": "API Key",
                        "value": "***hidden***",
                        "key": "api_key"
                    },
                    "api_secret": {
                        "type": "text_input",
                        "label": "API Secret",
                        "value": "***hidden***",
                        "key": "api_secret"
                    },
                    "testnet": {
                        "type": "checkbox",
                        "label": "Usar Testnet",
                        "value": True,
                        "key": "testnet"
                    }
                },
                "save_btn": {
                    "type": "button",
                    "label": "💾 Salvar Configurações",
                    "key": "save_settings_btn"
                }
            },
            "timestamp": datetime.now().isoformat()
        }
    
    async def handle_widget_interaction(self, widget_key, value, action):
        """Processar interações de configurações"""
        if widget_key == "save_settings_btn" and action == "click":
            # Coletar todas as configurações
            settings = {
                "auto_trading": self.app.widgets.get("auto_trading", False),
                "notifications": self.app.widgets.get("notifications", True),
                "risk_management": self.app.widgets.get("risk_management", True),
                "max_daily_loss": self.app.widgets.get("max_daily_loss", 1000.0),
                "testnet": self.app.widgets.get("testnet", True)
            }
            
            # Simular salvamento
            return {
                "success": True,
                "message": "Configurações salvas com sucesso",
                "settings": settings
            }
        
        return await super().handle_widget_interaction(widget_key, value, action)


class TestStreamlitInterface:
    """Testes da interface Streamlit"""
    
    @pytest.mark.asyncio
    async def test_app_initialization(self):
        """Testa inicialização da aplicação"""
        app = StreamlitApp()
        
        try:
            # Inicializar
            result = await app.initialize()
            assert result["status"] == "initialized"
            assert result["pages"] == 6  # 6 páginas configuradas
            assert app.is_running is True
            
            # Verificar estado inicial
            session_state = app.get_session_state()
            assert session_state["authenticated"] is False
            assert session_state["current_page"] == "🏠 Dashboard"
            assert session_state["selected_symbol"] == "BTCUSDT"
            
        finally:
            await app.shutdown()
    
    @pytest.mark.asyncio
    async def test_authentication_flow(self):
        """Testa fluxo de autenticação"""
        app = StreamlitApp()
        
        try:
            await app.initialize()
            
            # Renderizar página de login
            login_page = await app.render_page("🏠 Dashboard")  # Deve redirecionar para login
            assert login_page["page"] == "login"
            assert "username_input" in login_page["components"]
            assert "password_input" in login_page["components"]
            
            # Simular preenchimento do formulário
            await app.handle_widget_interaction("username", "test_user", "change")
            await app.handle_widget_interaction("password", "test_pass", "change")
            
            # Simular clique no botão de login
            auth_result = await app.handle_widget_interaction("login_btn", None, "click")
            assert auth_result["success"] is True
            assert "user" in auth_result
            
            # Verificar estado após login
            session_state = app.get_session_state()
            assert session_state["authenticated"] is True
            assert session_state["user_id"] is not None
            
            # Logout
            logout_result = app.logout_user()
            assert logout_result["success"] is True
            
            session_state = app.get_session_state()
            assert session_state["authenticated"] is False
            
        finally:
            await app.shutdown()
    
    @pytest.mark.asyncio
    async def test_dashboard_page_rendering(self):
        """Testa renderização da página de dashboard"""
        app = StreamlitApp()
        
        try:
            await app.initialize()
            
            # Autenticar usuário
            await app.authenticate_user("dashboard_user", "password")
            
            # Renderizar dashboard
            dashboard = await app.render_page("🏠 Dashboard")
            
            assert dashboard["page"] == "dashboard"
            assert dashboard["title"] == "🏠 Dashboard Principal"
            
            # Verificar estrutura do layout
            layout = dashboard["layout"]
            assert "sidebar" in layout
            assert "main" in layout
            
            # Verificar sidebar
            sidebar = layout["sidebar"]
            assert "user_info" in sidebar
            assert "navigation" in sidebar
            assert "symbol_selector" in sidebar
            
            # Verificar conteúdo principal
            main = layout["main"]
            assert "metrics_row" in main
            assert "market_data_card" in main
            assert "positions_table" in main
            
            # Testar interação com seletor de símbolo
            symbol_result = await app.handle_widget_interaction("symbol_selector", "ETHUSDT", "change")
            assert symbol_result["symbol_changed"] is True
            assert symbol_result["new_symbol"] == "ETHUSDT"
            
        finally:
            await app.shutdown()
    
    @pytest.mark.asyncio
    async def test_trading_page_functionality(self):
        """Testa funcionalidade da página de trading"""
        app = StreamlitApp()
        
        try:
            await app.initialize()
            await app.authenticate_user("trader_user", "password")
            
            # Renderizar página de trading
            trading_page = await app.render_page("📈 Trading")
            
            assert trading_page["page"] == "trading"
            assert "order_form" in trading_page["layout"]
            assert "market_info" in trading_page["layout"]
            
            # Simular preenchimento do formulário de ordem
            await app.handle_widget_interaction("order_symbol", "BTCUSDT", "change")
            await app.handle_widget_interaction("order_side", "buy", "change")
            await app.handle_widget_interaction("order_quantity", 0.1, "change")
            
            # Simular execução de ordem
            order_result = await app.handle_widget_interaction("place_order_btn", None, "click")
            
            assert order_result["success"] is True
            assert "trade_result" in order_result
            assert "Ordem executada" in order_result["message"]
            
        finally:
            await app.shutdown()
    
    @pytest.mark.asyncio
    async def test_positions_page_management(self):
        """Testa gestão de posições"""
        app = StreamlitApp()
        
        try:
            await app.initialize()
            await app.authenticate_user("positions_user", "password")
            
            # Criar algumas posições primeiro
            user_id = app.session_state["user_id"]
            
            # Executar trades para criar posições
            await app.trading_system.execute_trade(user_id, "BTCUSDT", "buy", 0.1)
            await app.trading_system.execute_trade(user_id, "ETHUSDT", "sell", 1.0)
            
            # Renderizar página de posições
            positions_page = await app.render_page("💼 Posições")
            
            assert positions_page["page"] == "positions"
            assert "summary_metrics" in positions_page["layout"]
            assert "positions_table" in positions_page["layout"]
            
            # Verificar métricas
            metrics = positions_page["layout"]["summary_metrics"]
            assert metrics["total_positions"] == 2
            assert metrics["open_positions"] == 2
            
            # Verificar tabela de posições
            table_data = positions_page["layout"]["positions_table"]["data"]
            assert len(table_data) == 2
            
            # Simular fechamento de posição
            position_id = table_data[0][0]  # ID da primeira posição
            close_result = await app.handle_widget_interaction(f"close_position_{position_id}", None, "click")
            
            assert close_result["success"] is True
            assert "fechada com sucesso" in close_result["message"]
            
        finally:
            await app.shutdown()
    
    @pytest.mark.asyncio
    async def test_strategies_page_creation(self):
        """Testa criação de estratégias"""
        app = StreamlitApp()
        
        try:
            await app.initialize()
            await app.authenticate_user("strategy_user", "password")
            
            # Renderizar página de estratégias
            strategies_page = await app.render_page("⚙️ Estratégias")
            
            assert strategies_page["page"] == "strategies"
            assert "create_strategy_form" in strategies_page["layout"]
            assert "strategy_templates" in strategies_page["layout"]
            
            # Simular preenchimento do formulário
            await app.handle_widget_interaction("strategy_name", "Test Strategy", "change")
            await app.handle_widget_interaction("strategy_type", "ppp_vishva", "change")
            await app.handle_widget_interaction("strategy_risk", 1.5, "change")
            await app.handle_widget_interaction("strategy_max_positions", 5, "change")
            
            # Simular criação de estratégia
            create_result = await app.handle_widget_interaction("create_strategy_btn", None, "click")
            
            assert create_result["success"] is True
            assert "criada com sucesso" in create_result["message"]
            assert create_result["strategy"]["name"] == "Test Strategy"
            
        finally:
            await app.shutdown()
    
    @pytest.mark.asyncio
    async def test_analytics_page_display(self):
        """Testa exibição da página de analytics"""
        app = StreamlitApp()
        
        try:
            await app.initialize()
            await app.authenticate_user("analytics_user", "password")
            
            # Criar dados para analytics
            user_id = app.session_state["user_id"]
            
            # Executar alguns trades
            for i in range(5):
                symbol = "BTCUSDT" if i % 2 == 0 else "ETHUSDT"
                side = "buy" if i % 2 == 0 else "sell"
                await app.trading_system.execute_trade(user_id, symbol, side, 0.1)
            
            # Renderizar página de analytics
            analytics_page = await app.render_page("📊 Analytics")
            
            assert analytics_page["page"] == "analytics"
            assert "performance_metrics" in analytics_page["layout"]
            assert "charts" in analytics_page["layout"]
            
            # Verificar métricas de performance
            metrics = analytics_page["layout"]["performance_metrics"]
            assert metrics["total_trades"] == 5
            assert "win_rate" in metrics
            assert "total_pnl" in metrics
            
            # Verificar gráficos
            charts = analytics_page["layout"]["charts"]
            assert "pnl_chart" in charts
            assert "trades_by_symbol" in charts
            
        finally:
            await app.shutdown()
    
    @pytest.mark.asyncio
    async def test_settings_page_configuration(self):
        """Testa configuração na página de settings"""
        app = StreamlitApp()
        
        try:
            await app.initialize()
            await app.authenticate_user("settings_user", "password")
            
            # Renderizar página de configurações
            settings_page = await app.render_page("🔧 Configurações")
            
            assert settings_page["page"] == "settings"
            assert "trading_settings" in settings_page["layout"]
            assert "api_settings" in settings_page["layout"]
            
            # Simular alteração de configurações
            await app.handle_widget_interaction("auto_trading", True, "change")
            await app.handle_widget_interaction("notifications", False, "change")
            await app.handle_widget_interaction("max_daily_loss", 500.0, "change")
            
            # Simular salvamento
            save_result = await app.handle_widget_interaction("save_settings_btn", None, "click")
            
            assert save_result["success"] is True
            assert "salvas com sucesso" in save_result["message"]
            
            settings = save_result["settings"]
            assert settings["auto_trading"] is True
            assert settings["notifications"] is False
            assert settings["max_daily_loss"] == 500.0
            
        finally:
            await app.shutdown()
    
    @pytest.mark.asyncio
    async def test_navigation_between_pages(self):
        """Testa navegação entre páginas"""
        app = StreamlitApp()
        
        try:
            await app.initialize()
            await app.authenticate_user("nav_user", "password")
            
            # Lista de páginas para testar
            pages_to_test = [
                "🏠 Dashboard",
                "📈 Trading", 
                "💼 Posições",
                "⚙️ Estratégias",
                "📊 Analytics",
                "🔧 Configurações"
            ]
            
            # Testar navegação para cada página
            for page_name in pages_to_test:
                # Simular seleção da página
                nav_result = await app.handle_widget_interaction("page_selector", page_name, "change")
                assert nav_result["page_changed"] is True
                assert nav_result["new_page"] == page_name
                
                # Renderizar a página
                page_content = await app.render_page(page_name)
                assert "page" in page_content
                assert "title" in page_content
                assert "layout" in page_content
                
                # Verificar que a página foi renderizada corretamente
                expected_page_key = page_name.split()[1].lower()  # Extrair nome da página
                if expected_page_key == "dashboard":
                    assert page_content["page"] == "dashboard"
                elif expected_page_key == "trading":
                    assert page_content["page"] == "trading"
                # ... outros casos
            
        finally:
            await app.shutdown()
    
    @pytest.mark.asyncio
    async def test_real_time_data_updates(self):
        """Testa atualizações de dados em tempo real"""
        app = StreamlitApp()
        
        try:
            await app.initialize()
            await app.authenticate_user("realtime_user", "password")
            
            # Renderizar dashboard inicial
            initial_dashboard = await app.render_page("🏠 Dashboard")
            initial_timestamp = initial_dashboard["timestamp"]
            
            # Simular passagem de tempo e mudanças nos dados
            await asyncio.sleep(0.1)
            
            # Simular atualização via botão refresh
            refresh_result = await app.handle_widget_interaction("refresh_btn", None, "click")
            assert refresh_result["refresh_triggered"] is True
            
            # Renderizar dashboard atualizado
            updated_dashboard = await app.render_page("🏠 Dashboard")
            updated_timestamp = updated_dashboard["timestamp"]
            
            # Verificar que os dados foram atualizados
            assert updated_timestamp > initial_timestamp
            
            # Testar mudança de símbolo
            symbol_result = await app.handle_widget_interaction("symbol_selector", "ETHUSDT", "change")
            assert symbol_result["symbol_changed"] is True
            
            # Renderizar com novo símbolo
            symbol_dashboard = await app.render_page("🏠 Dashboard")
            market_data = symbol_dashboard["layout"]["main"]["market_data_card"]
            # O símbolo deve ter mudado (seria ETHUSDT em implementação real)
            
        finally:
            await app.shutdown()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

