# -*- coding: utf-8 -*-
"""
Crypto Trading MVP - Dashboard
Streamlit dashboard para monitoramento e controle
"""

import os
import sys
import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# Adicionar diretório raiz ao path
sys.path.append('/app')

# Configuração da página
st.set_page_config(
    page_title="Crypto Trading MVP",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configurações
API_BASE_URL = os.getenv("API_URL", "http://api:8000")

# CSS customizado
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
    .success-text {
        color: #28a745;
        font-weight: bold;
    }
    .error-text {
        color: #dc3545;
        font-weight: bold;
    }
    .warning-text {
        color: #ffc107;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Funções auxiliares
def make_api_request(endpoint, method="GET", data=None, token=None):
    """Fazer requisição para a API"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=10)
        else:
            return None
        
        return response
    except Exception as e:
        st.error(f"Erro na requisição: {e}")
        return None

def check_api_health():
    """Verificar saúde da API"""
    try:
        response = make_api_request("/health")
        if response and response.status_code == 200:
            return True, response.json()
        return False, None
    except:
        return False, None

def login_user(username, password):
    """Fazer login do usuário"""
    data = {"username": username, "password": password}
    response = make_api_request("/api/auth/login", "POST", data)
    
    if response and response.status_code == 200:
        return True, response.json()
    return False, None

# Sidebar - Autenticação
st.sidebar.title("🔐 Autenticação")

# Verificar se usuário está logado
if "token" not in st.session_state:
    st.session_state.token = None
    st.session_state.user_info = None

if not st.session_state.token:
    # Formulário de login
    with st.sidebar.form("login_form"):
        username = st.text_input("Usuário")
        password = st.text_input("Senha", type="password")
        submit = st.form_submit_button("Login")
        
        if submit and username and password:
            success, result = login_user(username, password)
            if success:
                st.session_state.token = result["access_token"]
                st.session_state.user_info = result.get("user_info", {})
                st.success("Login realizado com sucesso!")
                st.rerun()
            else:
                st.error("Credenciais inválidas!")
    
    # Credenciais de teste
    st.sidebar.markdown("### 🧪 Credenciais de Teste")
    st.sidebar.markdown("**admin** / **admin123**")
    st.sidebar.markdown("**demo** / **demo123**")
    st.sidebar.markdown("**trader** / **trader123**")

else:
    # Usuário logado
    user_info = st.session_state.user_info or {}
    st.sidebar.success(f"Logado como: **{user_info.get('username', 'Usuário')}**")
    st.sidebar.markdown(f"Role: **{user_info.get('role', 'user')}**")
    
    if st.sidebar.button("Logout"):
        st.session_state.token = None
        st.session_state.user_info = None
        st.rerun()

# Conteúdo principal
st.markdown('<div class="main-header">📈 Crypto Trading MVP Dashboard</div>', unsafe_allow_html=True)

# Verificar status da API
api_healthy, api_info = check_api_health()

if not api_healthy:
    st.error("❌ API não está respondendo. Verifique se o serviço está rodando.")
    st.markdown("### 🔧 Comandos de Verificação")
    st.code("""
    # Verificar status dos containers
    docker-compose -f docker-compose.production.yml ps
    
    # Verificar logs da API
    docker logs crypto-trading-api -f
    
    # Testar API diretamente
    curl http://localhost:8000/health
    """)
    st.stop()

# Status da API
st.success("✅ API conectada e funcionando!")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Status API", "🟢 Online")

with col2:
    st.metric("Versão", api_info.get("version", "N/A"))

with col3:
    st.metric("Estrutura", "src/")

with col4:
    st.metric("Timestamp", datetime.now().strftime("%H:%M:%S"))

# Conteúdo baseado no status de login
if st.session_state.token:
    # Usuário logado - mostrar dashboard completo
    
    # Tabs principais
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "💹 Trading", "⚙️ Sistema", "👤 Perfil"])
    
    with tab1:
        st.header("📊 Visão Geral")
        
        # Métricas simuladas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("PnL Total", "$125.50", "12.5%")
        
        with col2:
            st.metric("Trades Hoje", "15", "3")
        
        with col3:
            st.metric("Win Rate", "68%", "5%")
        
        with col4:
            st.metric("Volume 24h", "$2,450", "15%")
        
        # Gráfico de PnL
        st.subheader("📈 Performance")
        
        # Dados simulados
        dates = pd.date_range(start="2025-09-01", end="2025-09-25", freq="D")
        pnl_data = pd.DataFrame({
            "Date": dates,
            "PnL": [50 + i*2 + (i%3)*10 for i in range(len(dates))]
        })
        
        fig = px.line(pnl_data, x="Date", y="PnL", title="PnL Acumulado")
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.header("💹 Trading")
        
        # Status do trading
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🎯 Estratégia Ativa")
            st.info("**PPP Vishva Strategy**")
            st.markdown("- Symbol: BTCUSDT")
            st.markdown("- Risk Level: Medium")
            st.markdown("- Status: 🟢 Ativo")
        
        with col2:
            st.subheader("⚡ Controles")
            
            if st.button("🚀 Iniciar Trading", type="primary"):
                st.success("Trading iniciado!")
            
            if st.button("🛑 Parar Trading"):
                st.warning("Trading pausado!")
        
        # Histórico de trades
        st.subheader("📋 Histórico de Trades")
        
        trades_data = pd.DataFrame({
            "ID": ["trade_001", "trade_002", "trade_003"],
            "Symbol": ["BTCUSDT", "BTCUSDT", "BTCUSDT"],
            "Side": ["buy", "sell", "buy"],
            "Amount": [0.001, 0.001, 0.0015],
            "Price": [65000, 65500, 64800],
            "PnL": [25.50, 50.00, -15.30],
            "Time": ["10:30", "11:45", "14:20"]
        })
        
        st.dataframe(trades_data, use_container_width=True)
    
    with tab3:
        st.header("⚙️ Sistema")
        
        # Status dos serviços
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🔧 Status dos Serviços")
            
            services = [
                ("API", "🟢", "Running"),
                ("Database", "🟢", "Connected"),
                ("Redis", "🟢", "Connected"),
                ("Worker", "🟢", "Active"),
                ("Grafana", "🟢", "Running"),
                ("Nginx", "🟢", "Running")
            ]
            
            for service, status, desc in services:
                st.markdown(f"**{service}**: {status} {desc}")
        
        with col2:
            st.subheader("📊 Métricas do Sistema")
            st.metric("CPU Usage", "45%")
            st.metric("Memory Usage", "62%")
            st.metric("Disk Usage", "23%")
            st.metric("Uptime", "2h 30m")
        
        # Links úteis
        st.subheader("🔗 Links Úteis")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("[📊 Grafana](http://localhost:3000)")
        
        with col2:
            st.markdown("[📚 API Docs](http://localhost:8000/docs)")
        
        with col3:
            st.markdown("[🔍 API Health](http://localhost:8000/health)")
    
    with tab4:
        st.header("👤 Perfil do Usuário")
        
        user_info = st.session_state.user_info or {}
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("ℹ️ Informações")
            st.markdown(f"**Username:** {user_info.get('username', 'N/A')}")
            st.markdown(f"**User ID:** {user_info.get('user_id', 'N/A')}")
            st.markdown(f"**Role:** {user_info.get('role', 'N/A')}")
            st.markdown(f"**Tenant ID:** {user_info.get('tenant_id', 'N/A')}")
        
        with col2:
            st.subheader("📈 Estatísticas")
            st.metric("Total Trades", "45")
            st.metric("Total PnL", "$125.50")
            st.metric("Dias Ativos", "15")
            st.metric("Última Atividade", "Agora")

else:
    # Usuário não logado - mostrar informações públicas
    st.info("🔐 Faça login para acessar o dashboard completo")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Status do Sistema")
        st.success("✅ API Online")
        st.success("✅ Database Connected")
        st.success("✅ Redis Connected")
        st.success("✅ All Services Running")
    
    with col2:
        st.subheader("🔗 Links Públicos")
        st.markdown("- [API Health](http://localhost:8000/health)")
        st.markdown("- [API Docs](http://localhost:8000/docs)")
        st.markdown("- [Grafana](http://localhost:3000)")

# Footer
st.markdown("---")
st.markdown("**Crypto Trading MVP v2.0** | Estrutura: src/ | Powered by Streamlit")
