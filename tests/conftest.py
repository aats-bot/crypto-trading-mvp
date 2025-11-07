"""
Fixtures globais para testes do Crypto Trading MVP
"""
import pytest
import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, UTC
from typing import Dict, List, Any
from unittest.mock import Mock, AsyncMock, MagicMock
import json
import os
from pathlib import Path

# Configuração de ambiente para testes
os.environ["ENVIRONMENT"] = "testing"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["REDIS_URL"] = "redis://localhost:6379/15"  # DB 15 para testes
os.environ["BYBIT_TESTNET"] = "true"


@pytest.fixture(scope="session")
def event_loop():
    """Fixture para loop de eventos assíncronos"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_market_data():
    """Fixture com dados de mercado simulados para testes"""
    dates = pd.date_range(start='2024-01-01', periods=1000, freq='1min')
    
    # Gerar dados OHLCV realistas
    np.random.seed(42)  # Para reprodutibilidade
    base_price = 50000  # Preço base do Bitcoin
    
    prices = []
    current_price = base_price
    
    for i in range(len(dates)):
        # Simulação de movimento de preço com tendência e volatilidade
        change_pct = np.random.normal(0, 0.002)  # 0.2% de volatilidade média
        current_price *= (1 + change_pct)
        prices.append(current_price)
    
    # Criar dados OHLCV
    data = []
    for i, (date, price) in enumerate(zip(dates, prices)):
        volatility = abs(np.random.normal(0, 0.001))
        high = price * (1 + volatility)
        low = price * (1 - volatility)
        open_price = prices[i-1] if i > 0 else price
        close_price = price
        volume = np.random.uniform(100, 1000)
        
        data.append({
            'timestamp': date,
            'open': open_price,
            'high': high,
            'low': low,
            'close': close_price,
            'volume': volume
        })
    
    return pd.DataFrame(data)


@pytest.fixture
def sample_trading_config():
    """Fixture com configuração de trading para testes"""
    return {
        "strategy": "PPP_Vishva",
        "symbol": "BTCUSDT",
        "timeframe": "1m",
        "risk_per_trade": 0.02,
        "max_position_size": 1000.0,
        "stop_loss_pct": 0.03,
        "take_profit_pct": 0.06,
        "max_open_positions": 3,
        "sl_ratio": 1.25,
        "pyramid_levels": 5,
        "indicators": {
            "ema_period": 100,
            "atr_period": 14,
            "ut_bot_factor": 3.0,
            "ewo_fast": 5,
            "ewo_slow": 35,
            "stoch_rsi_period": 14
        }
    }


@pytest.fixture
def sample_client_data():
    """Fixture com dados de cliente para testes"""
    return {
        "id": "test-client-123",
        "name": "Test Client",
        "email": "test@example.com",
        "bybit_api_key": "test_api_key",
        "bybit_api_secret": "test_api_secret",
        "is_active": True,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    }


@pytest.fixture
def mock_bybit_api():
    """Mock da API da Bybit para testes"""
    mock = Mock()
    
    # Mock de resposta de account info
    mock.get_wallet_balance.return_value = {
        "retCode": 0,
        "retMsg": "OK",
        "result": {
            "list": [{
                "accountType": "UNIFIED",
                "coin": [{
                    "coin": "USDT",
                    "walletBalance": "10000.00",
                    "availableBalance": "9500.00"
                }]
            }]
        }
    }
    
    # Mock de resposta de posições
    mock.get_positions.return_value = {
        "retCode": 0,
        "retMsg": "OK",
        "result": {
            "list": []
        }
    }
    
    # Mock de resposta de ordem
    mock.place_order.return_value = {
        "retCode": 0,
        "retMsg": "OK",
        "result": {
            "orderId": "test-order-123",
            "orderLinkId": "test-link-123"
        }
    }
    
    # Mock de dados de mercado
    mock.get_kline.return_value = {
        "retCode": 0,
        "retMsg": "OK",
        "result": {
            "list": [
                ["1640995200000", "50000", "50100", "49900", "50050", "100.5", "5005000"]
            ]
        }
    }
    
    return mock


@pytest.fixture
def mock_redis():
    """Mock do Redis para testes"""
    mock = AsyncMock()
    mock.get.return_value = None
    mock.set.return_value = True
    mock.delete.return_value = 1
    mock.exists.return_value = False
    mock.expire.return_value = True
    return mock


@pytest.fixture
def mock_database():
    """Mock do banco de dados para testes"""
    mock = AsyncMock()
    
    # Mock de sessão
    session_mock = AsyncMock()
    session_mock.add.return_value = None
    session_mock.commit.return_value = None
    session_mock.rollback.return_value = None
    session_mock.close.return_value = None
    
    mock.return_value = session_mock
    return mock


@pytest.fixture
def jwt_token():
    """Fixture com token JWT válido para testes"""
    return "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ0ZXN0LWNsaWVudC0xMjMiLCJleHAiOjk5OTk5OTk5OTl9.test_signature"


@pytest.fixture
def api_headers(jwt_token):
    """Headers para requisições autenticadas"""
    return {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }


@pytest.fixture
def sample_order_data():
    """Dados de ordem para testes"""
    return {
        "symbol": "BTCUSDT",
        "side": "Buy",
        "orderType": "Market",
        "qty": "0.001",
        "timeInForce": "IOC",
        "orderLinkId": f"test-order-{datetime.now(UTC).timestamp()}"
    }


@pytest.fixture
def sample_indicators_data():
    """Dados de indicadores calculados para testes"""
    return {
        "ema_100": 50000.0,
        "atr": 500.0,
        "ut_bot_signal": "buy",
        "ewo": 150.0,
        "stoch_rsi": 0.3,
        "heikin_ashi": {
            "open": 49950.0,
            "high": 50100.0,
            "low": 49900.0,
            "close": 50050.0
        }
    }


@pytest.fixture
def performance_metrics():
    """Métricas de performance para testes"""
    return {
        "total_trades": 100,
        "winning_trades": 65,
        "losing_trades": 35,
        "win_rate": 0.65,
        "profit_factor": 1.85,
        "max_drawdown": 0.12,
        "sharpe_ratio": 1.45,
        "total_pnl": 1250.50,
        "avg_win": 35.20,
        "avg_loss": -18.75
    }


@pytest.fixture
def mock_streamlit():
    """Mock do Streamlit para testes de dashboard"""
    mock = MagicMock()
    
    # Mock de componentes básicos
    mock.title.return_value = None
    mock.header.return_value = None
    mock.subheader.return_value = None
    mock.write.return_value = None
    mock.markdown.return_value = None
    
    # Mock de inputs
    mock.text_input.return_value = "test_input"
    mock.number_input.return_value = 100
    mock.selectbox.return_value = "option1"
    mock.button.return_value = False
    
    # Mock de layout
    mock.columns.return_value = [mock, mock, mock]
    mock.sidebar = mock
    
    # Mock de session state
    mock.session_state = {}
    
    return mock


@pytest.fixture
def test_data_dir():
    """Diretório para dados de teste"""
    data_dir = Path(__file__).parent / "fixtures" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


@pytest.fixture
def cleanup_test_files():
    """Fixture para limpeza de arquivos de teste"""
    created_files = []
    
    def _create_file(filepath):
        created_files.append(filepath)
        return filepath
    
    yield _create_file
    
    # Cleanup após o teste
    for filepath in created_files:
        if os.path.exists(filepath):
            os.remove(filepath)


# Fixtures para diferentes cenários de mercado
@pytest.fixture
def bullish_market_data(sample_market_data):
    """Dados de mercado em tendência de alta"""
    df = sample_market_data.copy()
    # Adicionar tendência de alta
    trend = np.linspace(0, 0.2, len(df))
    df['close'] = df['close'] * (1 + trend)
    df['high'] = df['high'] * (1 + trend)
    df['low'] = df['low'] * (1 + trend)
    df['open'] = df['open'] * (1 + trend)
    return df


@pytest.fixture
def bearish_market_data(sample_market_data):
    """Dados de mercado em tendência de baixa"""
    df = sample_market_data.copy()
    # Adicionar tendência de baixa
    trend = np.linspace(0, -0.15, len(df))
    df['close'] = df['close'] * (1 + trend)
    df['high'] = df['high'] * (1 + trend)
    df['low'] = df['low'] * (1 + trend)
    df['open'] = df['open'] * (1 + trend)
    return df


@pytest.fixture
def sideways_market_data(sample_market_data):
    """Dados de mercado lateral (sem tendência)"""
    df = sample_market_data.copy()
    # Manter preços em range lateral
    mean_price = df['close'].mean()
    df['close'] = mean_price + (df['close'] - mean_price) * 0.1
    df['high'] = mean_price + (df['high'] - mean_price) * 0.1
    df['low'] = mean_price + (df['low'] - mean_price) * 0.1
    df['open'] = mean_price + (df['open'] - mean_price) * 0.1
    return df


@pytest.fixture
def high_volatility_data(sample_market_data):
    """Dados de mercado com alta volatilidade"""
    df = sample_market_data.copy()
    # Aumentar volatilidade
    volatility_multiplier = 3.0
    mean_price = df['close'].mean()
    df['close'] = mean_price + (df['close'] - mean_price) * volatility_multiplier
    df['high'] = mean_price + (df['high'] - mean_price) * volatility_multiplier
    df['low'] = mean_price + (df['low'] - mean_price) * volatility_multiplier
    df['open'] = mean_price + (df['open'] - mean_price) * volatility_multiplier
    return df


# Configuração de pytest plugins
pytest_plugins = [
    "pytest_asyncio",
    "pytest_mock",
    "pytest_cov"
]

