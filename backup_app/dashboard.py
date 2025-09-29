"""
Main Streamlit dashboard application
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import requests
import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from config.settings import settings

# Page configuration
st.set_page_config(
    page_title="Crypto Trading Bot MVP",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .status-running {
        color: #28a745;
        font-weight: bold;
    }
    .status-stopped {
        color: #dc3545;
        font-weight: bold;
    }
    .status-paused {
        color: #ffc107;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# API base URL
API_BASE_URL = f"http://localhost:{settings.api_port}/api"

# Session state initialization
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'access_token' not in st.session_state:
    st.session_state.access_token = None
if 'client_data' not in st.session_state:
    st.session_state.client_data = None


def make_api_request(endpoint, method="GET", data=None, auth_required=True):
    """Make API request with authentication"""
    try:
        headers = {"Content-Type": "application/json"}
        
        if auth_required and st.session_state.access_token:
            headers["Authorization"] = f"Bearer {st.session_state.access_token}"
        
        url = f"{API_BASE_URL}{endpoint}"
        
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        
        if response.status_code == 401:
            st.session_state.authenticated = False
            st.session_state.access_token = None
            st.error("Sessão expirada. Faça login novamente.")
            return None
        
        return response.json() if response.status_code < 400 else None
        
    except requests.exceptions.ConnectionError:
        st.error("❌ Não foi possível conectar à API. Verifique se o servidor está rodando.")
        return None
    except Exception as e:
        st.error(f"Erro na requisição: {e}")
        return None


def login_page():
    """Login page"""
    st.markdown('<h1 class="main-header">🤖 Crypto Trading Bot MVP</h1>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 🔐 Login")
        
        with st.form("login_form"):
            email = st.text_input("📧 Email")
            password = st.text_input("🔒 Senha", type="password")
            submit_button = st.form_submit_button("Entrar", use_container_width=True)
            
            if submit_button:
                if email and password:
                    login_data = {"email": email, "password": password}
                    response = make_api_request("/api/auth/login", "POST", login_data, auth_required=False)
                    
                    if response:
                        st.session_state.authenticated = True
                        st.session_state.access_token = response["access_token"]
                        st.session_state.client_data = response["client"]
                        st.success("✅ Login realizado com sucesso!")
                        st.rerun()
                    else:
                        st.error("❌ Email ou senha incorretos")
                else:
                    st.error("❌ Preencha todos os campos")
        
        st.markdown("---")
        
        with st.expander("📝 Criar Nova Conta"):
            with st.form("register_form"):
                reg_name = st.text_input("👤 Nome Completo")
                reg_email = st.text_input("📧 Email")
                reg_password = st.text_input("🔒 Senha", type="password")
                reg_api_key = st.text_input("🔑 Bybit API Key (opcional)")
                reg_api_secret = st.text_input("🔐 Bybit API Secret (opcional)", type="password")
                register_button = st.form_submit_button("Criar Conta", use_container_width=True)
                
                if register_button:
                    if reg_name and reg_email and reg_password:
                        register_data = {
                            "name": reg_name,
                            "email": reg_email,
                            "password": reg_password,
                            "bybit_api_key": reg_api_key if reg_api_key else None,
                            "bybit_api_secret": reg_api_secret if reg_api_secret else None
                        }
                        response = make_api_request("/api/auth/register", "POST", register_data, auth_required=False)
                        
                        if response:
                            st.success("✅ Conta criada com sucesso! Faça login para continuar.")
                        else:
                            st.error("❌ Erro ao criar conta. Email pode já estar em uso.")
                    else:
                        st.error("❌ Preencha os campos obrigatórios")


def dashboard_page():
    """Main dashboard page"""
    st.markdown('<h1 class="main-header">🤖 Dashboard de Trading</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"### 👋 Olá, {st.session_state.client_data['name']}")
        st.markdown(f"📧 {st.session_state.client_data['email']}")
        
        if st.button("🚪 Logout", use_container_width=True):
            make_api_request("/api/auth/logout", "POST")
            st.session_state.authenticated = False
            st.session_state.access_token = None
            st.session_state.client_data = None
            st.rerun()
        
        st.markdown("---")
        
        # Navigation
        page = st.selectbox(
            "📍 Navegação",
            ["Dashboard", "Configurações", "Performance", "Histórico"]
        )
    
    if page == "Dashboard":
        show_main_dashboard()
    elif page == "Configurações":
        show_settings_page()
    elif page == "Performance":
        show_performance_page()
    elif page == "Histórico":
        show_history_page()


def show_main_dashboard():
    """Show main dashboard"""
    # Get bot status
    bot_status = make_api_request("/trading/status")
    
    if bot_status:
        # Bot control section
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if bot_status["is_running"]:
                status_class = "status-running"
                status_text = "🟢 Rodando"
            elif bot_status["is_paused"]:
                status_class = "status-paused"
                status_text = "🟡 Pausado"
            else:
                status_class = "status-stopped"
                status_text = "🔴 Parado"
            
            st.markdown(f'<div class="metric-card"><h4>Status do Bot</h4><p class="{status_class}">{status_text}</p></div>', unsafe_allow_html=True)
        
        with col2:
            if st.button("▶️ Iniciar", disabled=bot_status["is_running"]):
                response = make_api_request("/trading/control", "POST", {"action": "start"})
                if response:
                    st.success("Bot iniciado!")
                    st.rerun()
        
        with col3:
            if st.button("⏸️ Pausar", disabled=not bot_status["is_running"]):
                response = make_api_request("/trading/control", "POST", {"action": "pause"})
                if response:
                    st.success("Bot pausado!")
                    st.rerun()
        
        with col4:
            if st.button("⏹️ Parar", disabled=not bot_status["is_running"]):
                response = make_api_request("/trading/control", "POST", {"action": "stop"})
                if response:
                    st.success("Bot parado!")
                    st.rerun()
        
        st.markdown("---")
        
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total de Trades", bot_status["stats"]["total_trades"])
        
        with col2:
            st.metric("Trades Vencedores", bot_status["stats"]["winning_trades"])
        
        with col3:
            st.metric("PnL Total", f"${bot_status['stats']['total_pnl']:.2f}")
        
        with col4:
            st.metric("Max Drawdown", f"${bot_status['stats']['max_drawdown']:.2f}")
        
        # Strategy info
        st.markdown("### 📊 Informações da Estratégia")
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"**Estratégia:** {bot_status['strategy_info']['name']}")
            st.info(f"**Símbolos:** {', '.join(bot_status['strategy_info']['symbols'])}")
        
        with col2:
            st.info(f"**Nível de Risco:** {bot_status['risk_metrics']['risk_level']}")
    
    # Balance section
    balance_data = make_api_request("/trading/balance")
    if balance_data:
        st.markdown("### 💰 Saldo da Conta")
        
        balance_df = pd.DataFrame(balance_data["balance"])
        st.dataframe(balance_df, use_container_width=True)
    
    # Positions section
    positions_data = make_api_request("/trading/positions")
    if positions_data:
        st.markdown("### 📈 Posições Abertas")
        
        if positions_data["positions"]:
            positions_df = pd.DataFrame(positions_data["positions"])
            st.dataframe(positions_df, use_container_width=True)
        else:
            st.info("Nenhuma posição aberta no momento.")


def show_settings_page():
    """Show settings page"""
    st.markdown("### ⚙️ Configurações")
    
    # Get current config
    config_data = make_api_request("/clients/trading-config")
    
    if config_data:
        trading_config = config_data.get("trading_config", {})
        risk_config = config_data.get("risk_config", {})
        
        # Trading configuration
        st.markdown("#### 📊 Configuração de Trading")
        
        with st.form("trading_config_form"):
            strategy = st.selectbox(
                "Estratégia",
                ["sma", "rsi", "ppp_vishva"],
                index=0 if trading_config.get("strategy") == "sma" else 1 if trading_config.get("strategy") == "rsi" else 2
            )
            
            symbols = st.multiselect(
                "Símbolos para Trading",
                ["BTCUSDT", "ETHUSDT", "ADAUSDT", "DOTUSDT"],
                default=trading_config.get("symbols", ["BTCUSDT"])
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                if strategy == "sma":
                    fast_period = st.number_input(
                        "Período MA Rápida",
                        min_value=5,
                        max_value=50,
                        value=trading_config.get("fast_period", 10)
                    )
                    slow_period = st.number_input(
                        "Período MA Lenta",
                        min_value=10,
                        max_value=100,
                        value=trading_config.get("slow_period", 20)
                    )
                elif strategy == "rsi":
                    rsi_period = st.number_input(
                        "Período RSI",
                        min_value=5,
                        max_value=50,
                        value=trading_config.get("rsi_period", 14)
                    )
                    oversold = st.number_input(
                        "Nível Oversold",
                        min_value=10,
                        max_value=40,
                        value=trading_config.get("oversold", 30)
                    )
                    overbought = st.number_input(
                        "Nível Overbought",
                        min_value=60,
                        max_value=90,
                        value=trading_config.get("overbought", 70)
                    )
                elif strategy == "ppp_vishva":
                    sl_ratio = st.number_input(
                        "SL Ratio (ATR)",
                        min_value=0.5,
                        max_value=3.0,
                        value=trading_config.get("sl_ratio", 1.25),
                        step=0.25
                    )
                    max_pyramid_levels = st.number_input(
                        "Níveis de Piramidação",
                        min_value=1,
                        max_value=10,
                        value=trading_config.get("max_pyramid_levels", 5)
                    )
                    st.info("🔬 **Estratégia Avançada PPP Vishva**\n\n"
                           "• Filtro de tendência EMA100\n"
                           "• Sinais UT Bot (ATR-based)\n"
                           "• Confirmação EWO + Stoch RSI\n"
                           "• Validação multi-timeframe\n"
                           "• Gerenciamento de risco dinâmico")
            
            with col2:
                risk_per_trade = st.number_input(
                    "Risco por Trade (%)",
                    min_value=0.01,
                    max_value=0.10,
                    value=trading_config.get("risk_per_trade", 0.02),
                    format="%.3f"
                )
                
                update_interval = st.number_input(
                    "Intervalo de Atualização (s)",
                    min_value=10,
                    max_value=300,
                    value=trading_config.get("update_interval", 30)
                )
            
            if st.form_submit_button("💾 Salvar Configuração de Trading"):
                new_config = {
                    "strategy": strategy,
                    "symbols": symbols,
                    "risk_per_trade": risk_per_trade,
                    "update_interval": update_interval
                }
                
                if strategy == "sma":
                    new_config.update({
                        "fast_period": fast_period,
                        "slow_period": slow_period
                    })
                elif strategy == "rsi":
                    new_config.update({
                        "rsi_period": rsi_period,
                        "oversold": oversold,
                        "overbought": overbought
                    })
                elif strategy == "ppp_vishva":
                    new_config.update({
                        "sl_ratio": sl_ratio,
                        "max_pyramid_levels": max_pyramid_levels
                    })
                
                response = make_api_request("/clients/trading-config", "PUT", new_config)
                if response:
                    st.success("✅ Configuração de trading salva!")
                else:
                    st.error("❌ Erro ao salvar configuração")
        
        st.markdown("---")
        
        # Risk configuration
        st.markdown("#### ⚠️ Configuração de Risco")
        
        with st.form("risk_config_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                max_position_size = st.number_input(
                    "Tamanho Máximo da Posição (USD)",
                    min_value=100.0,
                    max_value=10000.0,
                    value=risk_config.get("max_position_size_usd", 1000.0)
                )
                
                max_daily_loss = st.number_input(
                    "Perda Máxima Diária (USD)",
                    min_value=10.0,
                    max_value=1000.0,
                    value=risk_config.get("max_daily_loss_usd", 100.0)
                )
                
                max_open_positions = st.number_input(
                    "Máximo de Posições Abertas",
                    min_value=1,
                    max_value=10,
                    value=risk_config.get("max_open_positions", 3)
                )
            
            with col2:
                stop_loss_pct = st.number_input(
                    "Stop Loss (%)",
                    min_value=0.01,
                    max_value=0.10,
                    value=risk_config.get("stop_loss_pct", 0.02),
                    format="%.3f"
                )
                
                take_profit_pct = st.number_input(
                    "Take Profit (%)",
                    min_value=0.01,
                    max_value=0.20,
                    value=risk_config.get("take_profit_pct", 0.04),
                    format="%.3f"
                )
                
                max_leverage = st.number_input(
                    "Alavancagem Máxima",
                    min_value=1.0,
                    max_value=10.0,
                    value=risk_config.get("max_leverage", 3.0)
                )
            
            if st.form_submit_button("💾 Salvar Configuração de Risco"):
                new_risk_config = {
                    "max_position_size_usd": max_position_size,
                    "max_daily_loss_usd": max_daily_loss,
                    "max_open_positions": max_open_positions,
                    "stop_loss_pct": stop_loss_pct,
                    "take_profit_pct": take_profit_pct,
                    "max_leverage": max_leverage
                }
                
                response = make_api_request("/clients/risk-config", "PUT", new_risk_config)
                if response:
                    st.success("✅ Configuração de risco salva!")
                else:
                    st.error("❌ Erro ao salvar configuração")


def show_performance_page():
    """Show performance page"""
    st.markdown("### 📊 Performance")
    
    # Get performance data
    performance_data = make_api_request("/trading/performance")
    
    if performance_data:
        perf = performance_data["performance"]
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Saldo Total", f"${perf['total_balance']:.2f}")
        
        with col2:
            st.metric("PnL Não Realizado", f"${perf['total_unrealized_pnl']:.2f}")
        
        with col3:
            st.metric("Taxa de Vitória", f"{perf['win_rate']:.1f}%")
        
        with col4:
            st.metric("Uptime", f"{perf['uptime']:.0f}s")
        
        # Mock performance chart
        st.markdown("#### 📈 Evolução do PnL")
        
        # Generate mock data for demonstration
        dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
        mock_pnl = [0]
        
        for i in range(1, len(dates)):
            change = np.random.normal(0, 10)  # Random daily change
            mock_pnl.append(mock_pnl[-1] + change)
        
        chart_data = pd.DataFrame({
            'Data': dates,
            'PnL Acumulado': mock_pnl
        })
        
        fig = px.line(chart_data, x='Data', y='PnL Acumulado', title='Evolução do PnL (Últimos 30 dias)')
        st.plotly_chart(fig, use_container_width=True)
        
        # Risk metrics
        st.markdown("#### ⚠️ Métricas de Risco")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"**Nível de Risco:** {perf['risk_level']}")
            st.info(f"**Posições Abertas:** {perf['positions']}")
        
        with col2:
            st.info(f"**Max Drawdown:** ${perf['max_drawdown']:.2f}")
            st.info(f"**Estratégia:** {perf['strategy']}")


def show_history_page():
    """Show history page"""
    st.markdown("### 📜 Histórico")
    
    # Get orders history
    orders_data = make_api_request("/trading/orders")
    
    if orders_data:
        st.markdown("#### 📋 Histórico de Ordens")
        
        if orders_data["orders"]:
            orders_df = pd.DataFrame(orders_data["orders"])
            st.dataframe(orders_df, use_container_width=True)
        else:
            st.info("Nenhuma ordem encontrada.")
    
    # Mock trading history chart
    st.markdown("#### 📊 Atividade de Trading")
    
    # Generate mock trading activity
    dates = pd.date_range(start=datetime.now() - timedelta(days=7), end=datetime.now(), freq='H')
    mock_trades = np.random.poisson(0.5, len(dates))  # Random number of trades per hour
    
    activity_data = pd.DataFrame({
        'Hora': dates,
        'Número de Trades': mock_trades
    })
    
    fig = px.bar(activity_data, x='Hora', y='Número de Trades', title='Atividade de Trading (Últimos 7 dias)')
    st.plotly_chart(fig, use_container_width=True)


def main():
    """Main application"""
    if not st.session_state.authenticated:
        login_page()
    else:
        dashboard_page()


if __name__ == "__main__":
    # Import numpy for mock data generation
    import numpy as np
    main()

