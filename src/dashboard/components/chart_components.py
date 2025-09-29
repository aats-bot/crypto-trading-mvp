# 📊 Componentes de Gráficos - Dashboard
"""
Componentes reutilizáveis para visualização de dados
Localização: /src/dashboard/components/chart_components.py
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import numpy as np


def price_chart(
    symbol: str = "BTCUSDT",
    timeframe: str = "1h",
    api_url: str = "http://localhost:8000"
) -> go.Figure:
    """
    Componente de gráfico de preços com indicadores técnicos
    
    Args:
        symbol: Símbolo para exibir
        timeframe: Timeframe do gráfico
        api_url: URL base da API
        
    Returns:
        Figura do Plotly
    """
    st.subheader(f"📈 Gráfico de Preços - {symbol}")
    
    # Controles do gráfico
    col1, col2, col3 = st.columns(3)
    
    with col1:
        symbol = st.selectbox(
            "Símbolo",
            ["BTCUSDT", "ETHUSDT", "ADAUSDT", "SOLUSDT"],
            index=0,
            key="price_chart_symbol"
        )
    
    with col2:
        timeframe = st.selectbox(
            "Timeframe",
            ["5m", "15m", "1h", "4h", "1d"],
            index=2,
            key="price_chart_timeframe"
        )
    
    with col3:
        show_indicators = st.checkbox(
            "Mostrar Indicadores",
            value=True,
            key="price_chart_indicators"
        )
    
    try:
        # Gerar dados simulados (em produção, viria da API)
        df = _generate_mock_price_data(symbol, timeframe)
        
        # Criar subplot com volume
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            subplot_titles=(f'{symbol} - {timeframe}', 'Volume'),
            row_width=[0.7, 0.3]
        )
        
        # Candlestick principal
        fig.add_trace(
            go.Candlestick(
                x=df['timestamp'],
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'],
                name='Preço',
                increasing_line_color='#00D4AA',
                decreasing_line_color='#FF6B6B'
            ),
            row=1, col=1
        )
        
        # Indicadores técnicos
        if show_indicators:
            # SMA 20
            sma_20 = df['close'].rolling(window=20).mean()
            fig.add_trace(
                go.Scatter(
                    x=df['timestamp'],
                    y=sma_20,
                    mode='lines',
                    name='SMA 20',
                    line=dict(color='#FFA500', width=1)
                ),
                row=1, col=1
            )
            
            # SMA 50
            sma_50 = df['close'].rolling(window=50).mean()
            fig.add_trace(
                go.Scatter(
                    x=df['timestamp'],
                    y=sma_50,
                    mode='lines',
                    name='SMA 50',
                    line=dict(color='#9370DB', width=1)
                ),
                row=1, col=1
            )
        
        # Volume
        colors = ['#00D4AA' if close >= open else '#FF6B6B' 
                 for close, open in zip(df['close'], df['open'])]
        
        fig.add_trace(
            go.Bar(
                x=df['timestamp'],
                y=df['volume'],
                name='Volume',
                marker_color=colors,
                opacity=0.7
            ),
            row=2, col=1
        )
        
        # Layout
        fig.update_layout(
            title=f'{symbol} - {timeframe}',
            yaxis_title='Preço (USDT)',
            template='plotly_dark',
            showlegend=True,
            height=600,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        fig.update_xaxes(rangeslider_visible=False)
        
        st.plotly_chart(fig, use_container_width=True)
        
        return fig
        
    except Exception as e:
        st.error(f"❌ Erro ao carregar gráfico: {str(e)}")
        return go.Figure()


def performance_chart(api_url: str = "http://localhost:8000") -> go.Figure:
    """
    Componente de gráfico de performance da conta
    
    Args:
        api_url: URL base da API
        
    Returns:
        Figura do Plotly
    """
    if not _is_authenticated():
        st.error("❌ Autenticação necessária")
        return go.Figure()
    
    st.subheader("📊 Performance da Conta")
    
    # Seletor de período
    period = st.selectbox(
        "Período",
        ["7d", "30d", "90d", "all"],
        index=1,
        format_func=lambda x: {
            "7d": "7 dias",
            "30d": "30 dias",
            "90d": "90 dias",
            "all": "Todo período"
        }[x],
        key="performance_chart_period"
    )
    
    try:
        # Gerar dados simulados de performance
        df = _generate_mock_performance_data(period)
        
        # Calcular equity curve
        df['cumulative_pnl'] = df['daily_pnl'].cumsum()
        df['equity'] = 10000 + df['cumulative_pnl']  # Capital inicial de $10,000
        
        # Criar gráfico
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=('Equity Curve', 'P&L Diário'),
            row_heights=[0.7, 0.3]
        )
        
        # Equity curve
        fig.add_trace(
            go.Scatter(
                x=df['date'],
                y=df['equity'],
                mode='lines',
                name='Equity',
                line=dict(color='#00D4AA', width=2),
                fill='tonexty'
            ),
            row=1, col=1
        )
        
        # Linha base do capital inicial
        fig.add_hline(
            y=10000,
            line_dash="dash",
            line_color="gray",
            annotation_text="Capital Inicial",
            row=1, col=1
        )
        
        # P&L diário como barras
        colors = ['#00D4AA' if pnl >= 0 else '#FF6B6B' for pnl in df['daily_pnl']]
        fig.add_trace(
            go.Bar(
                x=df['date'],
                y=df['daily_pnl'],
                name='P&L Diário',
                marker_color=colors,
                opacity=0.8
            ),
            row=2, col=1
        )
        
        # Layout
        fig.update_layout(
            title='Performance da Conta',
            template='plotly_dark',
            showlegend=False,
            height=500,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        fig.update_yaxes(title_text="Equity (USD)", row=1, col=1)
        fig.update_yaxes(title_text="P&L (USD)", row=2, col=1)
        fig.update_xaxes(title_text="Data", row=2, col=1)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Métricas resumidas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_return = (df['equity'].iloc[-1] - 10000) / 10000 * 100
            st.metric("Retorno Total", f"{total_return:.2f}%")
        
        with col2:
            max_equity = df['equity'].max()
            current_equity = df['equity'].iloc[-1]
            drawdown = (current_equity - max_equity) / max_equity * 100
            st.metric("Drawdown Atual", f"{drawdown:.2f}%")
        
        with col3:
            winning_days = len(df[df['daily_pnl'] > 0])
            total_days = len(df)
            win_rate = winning_days / total_days * 100
            st.metric("Dias Positivos", f"{win_rate:.1f}%")
        
        with col4:
            volatility = df['daily_pnl'].std()
            st.metric("Volatilidade Diária", f"${volatility:.2f}")
        
        return fig
        
    except Exception as e:
        st.error(f"❌ Erro ao carregar gráfico de performance: {str(e)}")
        return go.Figure()


def portfolio_distribution_chart(api_url: str = "http://localhost:8000") -> go.Figure:
    """
    Componente de gráfico de distribuição do portfólio
    
    Args:
        api_url: URL base da API
        
    Returns:
        Figura do Plotly
    """
    if not _is_authenticated():
        st.error("❌ Autenticação necessária")
        return go.Figure()
    
    st.subheader("🥧 Distribuição do Portfólio")
    
    try:
        # Dados simulados de distribuição
        portfolio_data = {
            'USDT': 7500.0,
            'BTC': 1200.0,
            'ETH': 800.0,
            'ADA': 300.0,
            'SOL': 200.0
        }
        
        # Criar DataFrame
        df = pd.DataFrame([
            {'Asset': asset, 'Value': value, 'Percentage': value/sum(portfolio_data.values())*100}
            for asset, value in portfolio_data.items()
        ])
        
        # Gráfico de pizza
        fig = px.pie(
            df,
            values='Value',
            names='Asset',
            title='Distribuição por Ativo',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>Valor: $%{value:.2f}<br>Percentual: %{percent}<extra></extra>'
        )
        
        fig.update_layout(
            template='plotly_dark',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Tabela detalhada
        st.subheader("💰 Detalhes do Portfólio")
        
        # Adicionar preços simulados
        df['Price'] = [1.0, 50000.0, 3000.0, 0.5, 100.0]  # Preços simulados
        df['Quantity'] = df['Value'] / df['Price']
        
        # Formatação
        df['Value'] = df['Value'].apply(lambda x: f"${x:.2f}")
        df['Price'] = df['Price'].apply(lambda x: f"${x:.4f}")
        df['Quantity'] = df['Quantity'].apply(lambda x: f"{x:.6f}")
        df['Percentage'] = df['Percentage'].apply(lambda x: f"{x:.1f}%")
        
        # Renomear colunas
        df = df.rename(columns={
            'Asset': 'Ativo',
            'Value': 'Valor',
            'Price': 'Preço',
            'Quantity': 'Quantidade',
            'Percentage': 'Percentual'
        })
        
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        return fig
        
    except Exception as e:
        st.error(f"❌ Erro ao carregar distribuição do portfólio: {str(e)}")
        return go.Figure()


def strategy_comparison_chart() -> go.Figure:
    """
    Componente de gráfico de comparação de estratégias
    
    Returns:
        Figura do Plotly
    """
    st.subheader("⚖️ Comparação de Estratégias")
    
    try:
        # Dados simulados de performance das estratégias
        strategies_data = {
            'SMA': {'return': 15.2, 'win_rate': 58.3, 'max_drawdown': 12.8, 'sharpe': 1.23},
            'RSI': {'return': 12.7, 'win_rate': 62.1, 'max_drawdown': 15.2, 'sharpe': 1.15},
            'PPP Vishva': {'return': 28.9, 'win_rate': 67.4, 'max_drawdown': 9.3, 'sharpe': 1.67}
        }
        
        # Criar DataFrame
        df = pd.DataFrame(strategies_data).T
        df.reset_index(inplace=True)
        df.rename(columns={'index': 'Strategy'}, inplace=True)
        
        # Gráfico de barras agrupadas
        fig = go.Figure()
        
        metrics = ['return', 'win_rate', 'sharpe']
        metric_names = ['Retorno (%)', 'Taxa de Acerto (%)', 'Sharpe Ratio']
        colors = ['#00D4AA', '#FFA500', '#9370DB']
        
        for i, (metric, name, color) in enumerate(zip(metrics, metric_names, colors)):
            fig.add_trace(
                go.Bar(
                    name=name,
                    x=df['Strategy'],
                    y=df[metric],
                    marker_color=color,
                    opacity=0.8,
                    yaxis=f'y{i+1}' if i > 0 else 'y'
                )
            )
        
        # Layout com múltiplos eixos Y
        fig.update_layout(
            title='Comparação de Performance das Estratégias',
            xaxis_title='Estratégia',
            template='plotly_dark',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=500,
            barmode='group'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Tabela de comparação detalhada
        st.subheader("📊 Métricas Detalhadas")
        
        # Formatação da tabela
        display_df = df.copy()
        display_df['return'] = display_df['return'].apply(lambda x: f"{x:.1f}%")
        display_df['win_rate'] = display_df['win_rate'].apply(lambda x: f"{x:.1f}%")
        display_df['max_drawdown'] = display_df['max_drawdown'].apply(lambda x: f"{x:.1f}%")
        display_df['sharpe'] = display_df['sharpe'].apply(lambda x: f"{x:.2f}")
        
        # Renomear colunas
        display_df = display_df.rename(columns={
            'Strategy': 'Estratégia',
            'return': 'Retorno',
            'win_rate': 'Taxa de Acerto',
            'max_drawdown': 'Max Drawdown',
            'sharpe': 'Sharpe Ratio'
        })
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        return fig
        
    except Exception as e:
        st.error(f"❌ Erro ao carregar comparação de estratégias: {str(e)}")
        return go.Figure()


def risk_metrics_chart(api_url: str = "http://localhost:8000") -> go.Figure:
    """
    Componente de gráfico de métricas de risco
    
    Args:
        api_url: URL base da API
        
    Returns:
        Figura do Plotly
    """
    st.subheader("⚠️ Métricas de Risco")
    
    try:
        # Dados simulados de risco
        risk_data = _generate_mock_risk_data()
        
        # Criar subplot com múltiplas métricas
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('VaR Histórico', 'Drawdown', 'Volatilidade Rolling', 'Correlação'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"type": "heatmap"}]]
        )
        
        # VaR (Value at Risk)
        fig.add_trace(
            go.Scatter(
                x=risk_data['date'],
                y=risk_data['var_95'],
                mode='lines',
                name='VaR 95%',
                line=dict(color='#FF6B6B', width=2)
            ),
            row=1, col=1
        )
        
        # Drawdown
        fig.add_trace(
            go.Scatter(
                x=risk_data['date'],
                y=risk_data['drawdown'],
                mode='lines',
                name='Drawdown',
                line=dict(color='#FFA500', width=2),
                fill='tonexty'
            ),
            row=1, col=2
        )
        
        # Volatilidade rolling
        fig.add_trace(
            go.Scatter(
                x=risk_data['date'],
                y=risk_data['volatility'],
                mode='lines',
                name='Volatilidade',
                line=dict(color='#9370DB', width=2)
            ),
            row=2, col=1
        )
        
        # Matriz de correlação (simulada)
        corr_matrix = np.array([
            [1.0, 0.7, 0.5, 0.3],
            [0.7, 1.0, 0.6, 0.4],
            [0.5, 0.6, 1.0, 0.2],
            [0.3, 0.4, 0.2, 1.0]
        ])
        
        fig.add_trace(
            go.Heatmap(
                z=corr_matrix,
                x=['BTC', 'ETH', 'ADA', 'SOL'],
                y=['BTC', 'ETH', 'ADA', 'SOL'],
                colorscale='RdYlBu',
                zmid=0
            ),
            row=2, col=2
        )
        
        # Layout
        fig.update_layout(
            title='Análise de Risco',
            template='plotly_dark',
            showlegend=False,
            height=600,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Métricas de risco resumidas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            current_var = risk_data['var_95'].iloc[-1]
            st.metric("VaR 95% Atual", f"${current_var:.2f}")
        
        with col2:
            current_drawdown = risk_data['drawdown'].iloc[-1]
            st.metric("Drawdown Atual", f"{current_drawdown:.2f}%")
        
        with col3:
            current_vol = risk_data['volatility'].iloc[-1]
            st.metric("Volatilidade Atual", f"{current_vol:.2f}%")
        
        with col4:
            max_drawdown = risk_data['drawdown'].min()
            st.metric("Max Drawdown", f"{max_drawdown:.2f}%")
        
        return fig
        
    except Exception as e:
        st.error(f"❌ Erro ao carregar métricas de risco: {str(e)}")
        return go.Figure()


# Funções auxiliares privadas
def _is_authenticated() -> bool:
    """Verifica se usuário está autenticado"""
    return (
        hasattr(st.session_state, 'authenticated') and
        st.session_state.authenticated and
        hasattr(st.session_state, 'access_token') and
        st.session_state.access_token
    )


def _generate_mock_price_data(symbol: str, timeframe: str) -> pd.DataFrame:
    """Gera dados simulados de preço"""
    # Configurações baseadas no símbolo
    base_prices = {
        'BTCUSDT': 50000,
        'ETHUSDT': 3000,
        'ADAUSDT': 0.5,
        'SOLUSDT': 100
    }
    
    base_price = base_prices.get(symbol, 50000)
    
    # Gerar dados simulados
    periods = 200
    dates = pd.date_range(end=datetime.now(), periods=periods, freq='1H')
    
    # Simulação de random walk
    np.random.seed(42)
    returns = np.random.normal(0, 0.02, periods)
    prices = [base_price]
    
    for ret in returns[1:]:
        prices.append(prices[-1] * (1 + ret))
    
    # Criar OHLCV
    df = pd.DataFrame({
        'timestamp': dates,
        'close': prices
    })
    
    df['open'] = df['close'].shift(1)
    df['high'] = df[['open', 'close']].max(axis=1) * (1 + np.random.uniform(0, 0.01, len(df)))
    df['low'] = df[['open', 'close']].min(axis=1) * (1 - np.random.uniform(0, 0.01, len(df)))
    df['volume'] = np.random.uniform(1000, 10000, len(df))
    
    df.fillna(method='bfill', inplace=True)
    
    return df


def _generate_mock_performance_data(period: str) -> pd.DataFrame:
    """Gera dados simulados de performance"""
    days_map = {'7d': 7, '30d': 30, '90d': 90, 'all': 365}
    days = days_map.get(period, 30)
    
    dates = pd.date_range(end=datetime.now(), periods=days, freq='1D')
    
    # Simulação de P&L diário
    np.random.seed(42)
    daily_pnl = np.random.normal(5, 50, days)  # Média de $5/dia, desvio $50
    
    return pd.DataFrame({
        'date': dates,
        'daily_pnl': daily_pnl
    })


def _generate_mock_risk_data() -> pd.DataFrame:
    """Gera dados simulados de risco"""
    days = 90
    dates = pd.date_range(end=datetime.now(), periods=days, freq='1D')
    
    np.random.seed(42)
    
    # Simulação de métricas de risco
    var_95 = np.random.uniform(-200, -50, days)
    drawdown = np.cummin(np.random.uniform(-20, 0, days))
    volatility = np.random.uniform(10, 30, days)
    
    return pd.DataFrame({
        'date': dates,
        'var_95': var_95,
        'drawdown': drawdown,
        'volatility': volatility
    })


# Exportar funções principais
__all__ = [
    "price_chart",
    "performance_chart",
    "portfolio_distribution_chart",
    "strategy_comparison_chart",
    "risk_metrics_chart",
]

