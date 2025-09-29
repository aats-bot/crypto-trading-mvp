# 📈 Componentes de Trading - Dashboard
"""
Componentes reutilizáveis para funcionalidades de trading
Localização: /src/dashboard/components/trading_components.py
"""
import streamlit as st
import pandas as pd
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px


def bot_status_card(api_url: str = "http://localhost:8000") -> Dict[str, Any]:
    """
    Componente de card de status do bot
    
    Args:
        api_url: URL base da API
        
    Returns:
        Dict com status do bot
    """
    if not _is_authenticated():
        st.error("❌ Autenticação necessária")
        return {}
    
    try:
        headers = _get_auth_headers()
        response = requests.get(f"{api_url}/api/trading/status", headers=headers, timeout=10)
        
        if response.status_code == 200:
            status_data = response.json()
            
            # Card principal de status
            with st.container():
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    status_color = {
                        "running": "🟢",
                        "paused": "🟡", 
                        "stopped": "🔴",
                        "error": "🚨"
                    }.get(status_data.get("bot_status", "unknown"), "⚪")
                    
                    st.metric(
                        "Status do Bot",
                        f"{status_color} {status_data.get('bot_status', 'Unknown').title()}"
                    )
                
                with col2:
                    uptime_seconds = status_data.get("uptime", 0)
                    uptime_str = _format_uptime(uptime_seconds)
                    st.metric("Tempo Ativo", uptime_str)
                
                with col3:
                    daily_pnl = status_data.get("daily_pnl", 0)
                    pnl_color = "normal" if daily_pnl >= 0 else "inverse"
                    st.metric(
                        "P&L Diário",
                        f"${daily_pnl:.2f}",
                        delta=f"{daily_pnl:.2f}",
                        delta_color=pnl_color
                    )
                
                with col4:
                    positions_count = status_data.get("positions_count", 0)
                    st.metric("Posições Abertas", positions_count)
            
            # Informações adicionais
            with st.expander("📊 Detalhes do Status", expanded=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Configuração Atual:**")
                    st.write(f"• Estratégia: {status_data.get('strategy', 'N/A')}")
                    st.write(f"• Símbolos: {', '.join(status_data.get('symbols', []))}")
                    st.write(f"• Trades Hoje: {status_data.get('total_trades_today', 0)}")
                
                with col2:
                    st.write("**Saldo da Conta:**")
                    account_balance = status_data.get("account_balance", {})
                    for asset, balance in account_balance.items():
                        st.write(f"• {asset}: {balance:.6f}")
            
            return status_data
            
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Erro de conexão: {str(e)}")
    except Exception as e:
        st.error(f"❌ Erro inesperado: {str(e)}")
    
    return {}


def trading_controls(api_url: str = "http://localhost:8000") -> None:
    """
    Componente de controles de trading
    
    Args:
        api_url: URL base da API
    """
    if not _is_authenticated():
        st.error("❌ Autenticação necessária")
        return
    
    st.subheader("🎮 Controles do Bot")
    
    col1, col2, col3, col4 = st.columns(4)
    
    headers = _get_auth_headers()
    
    with col1:
        if st.button("▶️ Iniciar", type="primary", use_container_width=True):
            try:
                response = requests.post(f"{api_url}/api/trading/start", headers=headers, timeout=10)
                if response.status_code == 200:
                    st.success("✅ Bot iniciado com sucesso!")
                    st.rerun()
                else:
                    error_data = response.json()
                    st.error(f"❌ {error_data.get('detail', 'Erro ao iniciar bot')}")
            except Exception as e:
                st.error(f"❌ Erro: {str(e)}")
    
    with col2:
        if st.button("⏸️ Pausar", use_container_width=True):
            try:
                response = requests.post(f"{api_url}/api/trading/pause", headers=headers, timeout=10)
                if response.status_code == 200:
                    st.success("✅ Bot pausado com sucesso!")
                    st.rerun()
                else:
                    error_data = response.json()
                    st.error(f"❌ {error_data.get('detail', 'Erro ao pausar bot')}")
            except Exception as e:
                st.error(f"❌ Erro: {str(e)}")
    
    with col3:
        if st.button("▶️ Retomar", use_container_width=True):
            try:
                response = requests.post(f"{api_url}/api/trading/resume", headers=headers, timeout=10)
                if response.status_code == 200:
                    st.success("✅ Bot retomado com sucesso!")
                    st.rerun()
                else:
                    error_data = response.json()
                    st.error(f"❌ {error_data.get('detail', 'Erro ao retomar bot')}")
            except Exception as e:
                st.error(f"❌ Erro: {str(e)}")
    
    with col4:
        if st.button("⏹️ Parar", use_container_width=True):
            if st.session_state.get('confirm_stop', False):
                try:
                    response = requests.post(f"{api_url}/api/trading/stop", headers=headers, timeout=10)
                    if response.status_code == 200:
                        st.success("✅ Bot parado com sucesso!")
                        st.session_state.confirm_stop = False
                        st.rerun()
                    else:
                        error_data = response.json()
                        st.error(f"❌ {error_data.get('detail', 'Erro ao parar bot')}")
                except Exception as e:
                    st.error(f"❌ Erro: {str(e)}")
            else:
                st.session_state.confirm_stop = True
                st.warning("⚠️ Clique novamente para confirmar")


def position_table(api_url: str = "http://localhost:8000") -> pd.DataFrame:
    """
    Componente de tabela de posições
    
    Args:
        api_url: URL base da API
        
    Returns:
        DataFrame com posições
    """
    if not _is_authenticated():
        st.error("❌ Autenticação necessária")
        return pd.DataFrame()
    
    st.subheader("📊 Posições Abertas")
    
    try:
        headers = _get_auth_headers()
        response = requests.get(f"{api_url}/api/trading/positions", headers=headers, timeout=10)
        
        if response.status_code == 200:
            positions = response.json()
            
            if not positions:
                st.info("ℹ️ Nenhuma posição aberta no momento")
                return pd.DataFrame()
            
            # Converter para DataFrame
            df = pd.DataFrame(positions)
            
            # Formatação das colunas
            df['entry_price'] = df['entry_price'].apply(lambda x: f"${x:.4f}")
            df['current_price'] = df['current_price'].apply(lambda x: f"${x:.4f}")
            df['unrealized_pnl'] = df['unrealized_pnl'].apply(lambda x: f"${x:.2f}")
            df['unrealized_pnl_pct'] = df['unrealized_pnl_pct'].apply(lambda x: f"{x:.2f}%")
            df['size'] = df['size'].apply(lambda x: f"{x:.6f}")
            
            # Renomear colunas
            df = df.rename(columns={
                'symbol': 'Símbolo',
                'side': 'Lado',
                'size': 'Tamanho',
                'entry_price': 'Preço Entrada',
                'current_price': 'Preço Atual',
                'unrealized_pnl': 'P&L',
                'unrealized_pnl_pct': 'P&L %',
                'opened_at': 'Aberta em'
            })
            
            # Exibir tabela
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )
            
            return df
            
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Erro de conexão: {str(e)}")
    except Exception as e:
        st.error(f"❌ Erro inesperado: {str(e)}")
    
    return pd.DataFrame()


def order_history_table(api_url: str = "http://localhost:8000", limit: int = 50) -> pd.DataFrame:
    """
    Componente de tabela de histórico de ordens
    
    Args:
        api_url: URL base da API
        limit: Número máximo de ordens a exibir
        
    Returns:
        DataFrame com histórico de ordens
    """
    if not _is_authenticated():
        st.error("❌ Autenticação necessária")
        return pd.DataFrame()
    
    st.subheader("📋 Histórico de Ordens")
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    
    with col1:
        symbol_filter = st.selectbox(
            "Símbolo",
            ["Todos", "BTCUSDT", "ETHUSDT", "ADAUSDT"],
            key="order_symbol_filter"
        )
    
    with col2:
        status_filter = st.selectbox(
            "Status",
            ["Todos", "filled", "cancelled", "pending"],
            key="order_status_filter"
        )
    
    with col3:
        limit_filter = st.selectbox(
            "Limite",
            [10, 25, 50, 100],
            index=2,
            key="order_limit_filter"
        )
    
    try:
        headers = _get_auth_headers()
        params = {"limit": limit_filter}
        
        if symbol_filter != "Todos":
            params["symbol"] = symbol_filter
        if status_filter != "Todos":
            params["status"] = status_filter
        
        response = requests.get(
            f"{api_url}/api/trading/orders",
            headers=headers,
            params=params,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            orders = data.get("orders", [])
            
            if not orders:
                st.info("ℹ️ Nenhuma ordem encontrada")
                return pd.DataFrame()
            
            # Converter para DataFrame
            df = pd.DataFrame(orders)
            
            # Formatação das colunas
            if 'filled_price' in df.columns:
                df['filled_price'] = df['filled_price'].apply(lambda x: f"${x:.4f}" if x else "N/A")
            if 'quantity' in df.columns:
                df['quantity'] = df['quantity'].apply(lambda x: f"{x:.6f}")
            if 'commission' in df.columns:
                df['commission'] = df['commission'].apply(lambda x: f"{x:.4f}")
            
            # Renomear colunas
            df = df.rename(columns={
                'symbol': 'Símbolo',
                'side': 'Lado',
                'type': 'Tipo',
                'quantity': 'Quantidade',
                'filled_price': 'Preço',
                'status': 'Status',
                'created_at': 'Criada em',
                'commission': 'Taxa'
            })
            
            # Exibir informações resumidas
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total de Ordens", len(orders))
            with col2:
                filled_orders = len([o for o in orders if o.get('status') == 'filled'])
                st.metric("Ordens Executadas", filled_orders)
            with col3:
                total_orders = data.get("total", len(orders))
                st.metric("Total Disponível", total_orders)
            
            # Exibir tabela
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )
            
            return df
            
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Erro de conexão: {str(e)}")
    except Exception as e:
        st.error(f"❌ Erro inesperado: {str(e)}")
    
    return pd.DataFrame()


def performance_metrics(api_url: str = "http://localhost:8000") -> Dict[str, Any]:
    """
    Componente de métricas de performance
    
    Args:
        api_url: URL base da API
        
    Returns:
        Dict com métricas de performance
    """
    if not _is_authenticated():
        st.error("❌ Autenticação necessária")
        return {}
    
    st.subheader("📈 Métricas de Performance")
    
    # Seletor de período
    period = st.selectbox(
        "Período",
        ["1d", "7d", "30d", "all"],
        index=1,
        format_func=lambda x: {
            "1d": "Último dia",
            "7d": "Últimos 7 dias", 
            "30d": "Últimos 30 dias",
            "all": "Todo período"
        }[x]
    )
    
    try:
        headers = _get_auth_headers()
        response = requests.get(
            f"{api_url}/api/trading/performance",
            headers=headers,
            params={"period": period},
            timeout=10
        )
        
        if response.status_code == 200:
            perf_data = response.json()
            
            # Métricas principais
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_pnl = perf_data.get("total_pnl", 0)
                pnl_pct = perf_data.get("total_pnl_pct", 0)
                st.metric(
                    "P&L Total",
                    f"${total_pnl:.2f}",
                    delta=f"{pnl_pct:.2f}%"
                )
            
            with col2:
                win_rate = perf_data.get("win_rate", 0)
                st.metric("Taxa de Acerto", f"{win_rate:.1f}%")
            
            with col3:
                total_trades = perf_data.get("total_trades", 0)
                st.metric("Total de Trades", total_trades)
            
            with col4:
                sharpe_ratio = perf_data.get("sharpe_ratio", 0)
                st.metric("Sharpe Ratio", f"{sharpe_ratio:.2f}")
            
            # Métricas detalhadas
            with st.expander("📊 Métricas Detalhadas", expanded=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Estatísticas de Trading:**")
                    st.write(f"• Trades Vencedores: {perf_data.get('winning_trades', 0)}")
                    st.write(f"• Trades Perdedores: {perf_data.get('losing_trades', 0)}")
                    st.write(f"• Melhor Trade: ${perf_data.get('best_trade', 0):.2f}")
                    st.write(f"• Pior Trade: ${perf_data.get('worst_trade', 0):.2f}")
                    st.write(f"• Trade Médio: ${perf_data.get('average_trade', 0):.2f}")
                
                with col2:
                    st.write("**Métricas de Risco:**")
                    st.write(f"• Profit Factor: {perf_data.get('profit_factor', 0):.2f}")
                    st.write(f"• Max Drawdown: ${perf_data.get('max_drawdown', 0):.2f}")
                    st.write(f"• Max Drawdown %: {perf_data.get('max_drawdown_pct', 0):.2f}%")
            
            # Gráfico de P&L diário
            daily_pnl = perf_data.get("daily_pnl", [])
            if daily_pnl:
                df_pnl = pd.DataFrame(daily_pnl)
                df_pnl['date'] = pd.to_datetime(df_pnl['date'])
                
                fig = px.line(
                    df_pnl,
                    x='date',
                    y='pnl',
                    title='P&L Diário',
                    labels={'pnl': 'P&L (USD)', 'date': 'Data'}
                )
                fig.update_traces(line_color='#00D4AA')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            return perf_data
            
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Erro de conexão: {str(e)}")
    except Exception as e:
        st.error(f"❌ Erro inesperado: {str(e)}")
    
    return {}


# Funções auxiliares privadas
def _is_authenticated() -> bool:
    """Verifica se usuário está autenticado"""
    return (
        hasattr(st.session_state, 'authenticated') and
        st.session_state.authenticated and
        hasattr(st.session_state, 'access_token') and
        st.session_state.access_token
    )


def _get_auth_headers() -> Dict[str, str]:
    """Retorna headers de autenticação"""
    if _is_authenticated():
        return {"Authorization": f"Bearer {st.session_state.access_token}"}
    return {}


def _format_uptime(seconds: int) -> str:
    """Formata tempo de atividade"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes}m"
    elif seconds < 86400:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"
    else:
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        return f"{days}d {hours}h"


# Exportar funções principais
__all__ = [
    "bot_status_card",
    "trading_controls",
    "position_table",
    "order_history_table",
    "performance_metrics",
]

