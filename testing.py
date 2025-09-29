# 🧪 Configuração de Ambiente - Testes
"""
Configurações específicas para ambiente de testes
Localização: /config/environments/testing.py
"""
import os
import tempfile
from typing import Dict, Any, List


class TestingConfig:
    """Configurações para ambiente de testes"""
    
    # Identificação do ambiente
    ENVIRONMENT = "testing"
    DEBUG = True
    TESTING = True
    
    # Configurações de banco de dados (em memória para testes)
    DATABASE_URL = "sqlite:///:memory:"
    DATABASE_ECHO = False  # Não logar queries em testes
    DATABASE_POOL_SIZE = 1
    DATABASE_MAX_OVERFLOW = 0
    
    # Configurações da API
    API_HOST = "127.0.0.1"
    API_PORT = 8888  # Porta diferente para testes
    API_RELOAD = False
    API_WORKERS = 1
    API_LOG_LEVEL = "critical"  # Mínimo de logs em testes
    
    # Configurações do Dashboard
    STREAMLIT_HOST = "127.0.0.1"
    STREAMLIT_PORT = 8889  # Porta diferente para testes
    STREAMLIT_DEBUG = False
    
    # Configurações de segurança (simplificadas para testes)
    SECRET_KEY = "test-secret-key-not-for-production"
    ENCRYPTION_KEY = "test-encryption-key-32-bytes-long"
    JWT_EXPIRATION_HOURS = 1  # Token válido por 1h em testes
    CORS_ORIGINS = ["*"]  # Permitir todas as origens em testes
    
    # Configurações da Bybit (mock/testnet)
    BYBIT_TESTNET = True
    BYBIT_API_KEY = "test_api_key"
    BYBIT_API_SECRET = "test_api_secret"
    BYBIT_TIMEOUT = 5
    BYBIT_RATE_LIMIT = 100  # Sem limite em testes
    BYBIT_MOCK_MODE = True  # Usar dados mockados
    
    # Configurações de logging (mínimas em testes)
    LOG_LEVEL = "CRITICAL"
    LOG_FORMAT = "%(levelname)s - %(message)s"
    LOG_FILE = None  # Não salvar em arquivo durante testes
    LOG_TO_CONSOLE = False  # Não imprimir logs em testes
    
    # Configurações de cache (desabilitado em testes)
    CACHE_ENABLED = False
    CACHE_TTL = 0
    
    # Configurações de rate limiting (desabilitado em testes)
    RATE_LIMIT_ENABLED = False
    RATE_LIMIT_PER_MINUTE = 999999
    RATE_LIMIT_PER_HOUR = 999999
    
    # Configurações de trading (valores seguros para testes)
    TRADING_CONFIG = {
        "default_risk_per_trade": 0.001,   # 0.1% para testes
        "max_position_size": 10.0,         # Muito pequeno para testes
        "max_daily_loss": 1.0,             # Muito pequeno para testes
        "max_open_positions": 2,           # Poucas posições em testes
        "default_symbols": ["BTCUSDT"],    # Apenas um símbolo
        "update_interval": 1,              # 1 segundo para testes rápidos
        "enable_paper_trading": True,      # Sempre paper trading em testes
        "mock_market_data": True,          # Usar dados mockados
    }
    
    # Configurações de monitoramento (simplificadas)
    MONITORING_ENABLED = False
    METRICS_ENDPOINT = "/test-metrics"
    HEALTH_CHECK_ENDPOINT = "/test-health"
    
    # Configurações de email (mock em testes)
    EMAIL_ENABLED = False
    EMAIL_BACKEND = "mock"
    EMAIL_HOST = "localhost"
    EMAIL_PORT = 1025
    EMAIL_USE_TLS = False
    EMAIL_FROM = "test@trading-bot.test"
    
    # Configurações de notificações (desabilitadas em testes)
    NOTIFICATIONS_ENABLED = False
    NOTIFICATION_CHANNELS = []
    
    # Configurações de backup (desabilitado em testes)
    BACKUP_ENABLED = False
    BACKUP_INTERVAL_HOURS = 999999
    BACKUP_RETENTION_DAYS = 1
    
    # Configurações de performance (relaxadas em testes)
    PERFORMANCE_MONITORING = False
    SLOW_QUERY_THRESHOLD = 999.0  # Não alertar em testes
    
    # Configurações específicas de testes
    TEST_CONFIG = {
        "fast_mode": True,              # Pular delays desnecessários
        "mock_external_apis": True,     # Mockar todas as APIs externas
        "use_fixtures": True,           # Usar dados de fixture
        "parallel_execution": False,    # Não executar testes em paralelo
        "cleanup_after_test": True,     # Limpar dados após cada teste
        "seed_random": 42,              # Seed fixo para reprodutibilidade
        "timeout_seconds": 30,          # Timeout para testes
    }
    
    # Símbolos permitidos para testes (limitado)
    ALLOWED_SYMBOLS = ["BTCUSDT", "ETHUSDT"]
    
    # Configurações de WebSocket (desabilitado em testes)
    WEBSOCKET_ENABLED = False
    WEBSOCKET_HOST = "127.0.0.1"
    WEBSOCKET_PORT = 8890
    
    # Dados de teste mockados
    MOCK_DATA = {
        "market_data": {
            "BTCUSDT": {
                "price": 50000.0,
                "volume": 1000.0,
                "high": 51000.0,
                "low": 49000.0,
                "change": 0.02,
            },
            "ETHUSDT": {
                "price": 3000.0,
                "volume": 500.0,
                "high": 3100.0,
                "low": 2900.0,
                "change": 0.015,
            },
        },
        "account_balance": {
            "USDT": 10000.0,
            "BTC": 0.0,
            "ETH": 0.0,
        },
        "positions": [],
        "orders": [],
    }
    
    # Configurações de fixtures de teste
    FIXTURES = {
        "clients": [
            {
                "id": 1,
                "email": "test1@example.com",
                "password": "test_password_123",
                "bybit_api_key": "test_key_1",
                "bybit_api_secret": "test_secret_1",
            },
            {
                "id": 2,
                "email": "test2@example.com",
                "password": "test_password_456",
                "bybit_api_key": "test_key_2",
                "bybit_api_secret": "test_secret_2",
            },
        ],
        "trading_configs": [
            {
                "client_id": 1,
                "strategy": "sma",
                "symbols": ["BTCUSDT"],
                "risk_per_trade": 0.01,
            },
            {
                "client_id": 2,
                "strategy": "rsi",
                "symbols": ["ETHUSDT"],
                "risk_per_trade": 0.015,
            },
        ],
    }
    
    @classmethod
    def get_database_config(cls) -> Dict[str, Any]:
        """Retorna configurações específicas do banco de dados para testes"""
        return {
            "url": cls.DATABASE_URL,
            "echo": cls.DATABASE_ECHO,
            "pool_size": cls.DATABASE_POOL_SIZE,
            "max_overflow": cls.DATABASE_MAX_OVERFLOW,
            "pool_pre_ping": False,  # Não necessário para SQLite em memória
        }
    
    @classmethod
    def get_api_config(cls) -> Dict[str, Any]:
        """Retorna configurações específicas da API para testes"""
        return {
            "host": cls.API_HOST,
            "port": cls.API_PORT,
            "reload": cls.API_RELOAD,
            "workers": cls.API_WORKERS,
            "log_level": cls.API_LOG_LEVEL,
            "access_log": False,
        }
    
    @classmethod
    def get_logging_config(cls) -> Dict[str, Any]:
        """Retorna configurações de logging para testes"""
        return {
            "version": 1,
            "disable_existing_loggers": True,  # Desabilitar todos os logs
            "formatters": {
                "simple": {
                    "format": cls.LOG_FORMAT,
                },
            },
            "handlers": {
                "null": {
                    "class": "logging.NullHandler",
                },
            },
            "loggers": {
                "": {  # Root logger
                    "level": cls.LOG_LEVEL,
                    "handlers": ["null"],
                },
                "uvicorn": {
                    "level": "CRITICAL",
                    "handlers": ["null"],
                    "propagate": False,
                },
                "sqlalchemy": {
                    "level": "CRITICAL",
                    "handlers": ["null"],
                    "propagate": False,
                },
            },
        }
    
    @classmethod
    def get_bybit_config(cls) -> Dict[str, Any]:
        """Retorna configurações da Bybit para testes"""
        return {
            "api_key": cls.BYBIT_API_KEY,
            "api_secret": cls.BYBIT_API_SECRET,
            "testnet": cls.BYBIT_TESTNET,
            "timeout": cls.BYBIT_TIMEOUT,
            "rate_limit": cls.BYBIT_RATE_LIMIT,
            "mock_mode": cls.BYBIT_MOCK_MODE,
        }
    
    @classmethod
    def get_trading_config(cls) -> Dict[str, Any]:
        """Retorna configurações de trading para testes"""
        return cls.TRADING_CONFIG.copy()
    
    @classmethod
    def get_mock_data(cls, data_type: str) -> Any:
        """Retorna dados mockados para testes"""
        return cls.MOCK_DATA.get(data_type, {})
    
    @classmethod
    def get_fixtures(cls, fixture_type: str) -> List[Dict[str, Any]]:
        """Retorna fixtures para testes"""
        return cls.FIXTURES.get(fixture_type, [])
    
    @classmethod
    def validate_config(cls) -> List[str]:
        """Valida configurações de teste"""
        errors = []
        
        # Verificar se está usando banco em memória
        if ":memory:" not in cls.DATABASE_URL:
            errors.append("Testes devem usar banco de dados em memória")
        
        # Verificar se está em modo de teste
        if not cls.TESTING:
            errors.append("TESTING deve ser True em ambiente de testes")
        
        # Verificar se paper trading está habilitado
        if not cls.TRADING_CONFIG["enable_paper_trading"]:
            errors.append("Paper trading deve estar habilitado em testes")
        
        # Verificar se valores de risco são seguros
        if cls.TRADING_CONFIG["default_risk_per_trade"] > 0.01:
            errors.append("Risk per trade deve ser <= 1% em testes")
        
        return errors
    
    @classmethod
    def setup_test_environment(cls) -> None:
        """Configura ambiente de teste"""
        import logging
        
        # Desabilitar todos os logs
        logging.disable(logging.CRITICAL)
        
        # Configurar diretório temporário
        cls.TEMP_DIR = tempfile.mkdtemp(prefix="trading_bot_test_")
        
        # Configurar variáveis de ambiente para testes
        os.environ["TESTING"] = "true"
        os.environ["DATABASE_URL"] = cls.DATABASE_URL
        os.environ["SECRET_KEY"] = cls.SECRET_KEY
    
    @classmethod
    def cleanup_test_environment(cls) -> None:
        """Limpa ambiente de teste"""
        import shutil
        import logging
        
        # Reabilitar logs
        logging.disable(logging.NOTSET)
        
        # Limpar diretório temporário
        if hasattr(cls, 'TEMP_DIR'):
            shutil.rmtree(cls.TEMP_DIR, ignore_errors=True)
        
        # Limpar variáveis de ambiente
        test_vars = ["TESTING", "DATABASE_URL", "SECRET_KEY"]
        for var in test_vars:
            os.environ.pop(var, None)
    
    @classmethod
    def get_cors_config(cls) -> Dict[str, Any]:
        """Retorna configurações de CORS para testes"""
        return {
            "allow_origins": cls.CORS_ORIGINS,
            "allow_credentials": True,
            "allow_methods": ["*"],
            "allow_headers": ["*"],
        }
    
    @classmethod
    def get_security_config(cls) -> Dict[str, Any]:
        """Retorna configurações de segurança para testes"""
        return {
            "secret_key": cls.SECRET_KEY,
            "encryption_key": cls.ENCRYPTION_KEY,
            "jwt_expiration_hours": cls.JWT_EXPIRATION_HOURS,
            "password_min_length": 6,  # Mais permissivo em testes
            "password_require_special": False,
            "session_timeout_minutes": 60,
        }
    
    @classmethod
    def create_test_client_data(cls) -> Dict[str, Any]:
        """Cria dados de cliente para testes"""
        return {
            "email": "test@example.com",
            "password": "test123",
            "bybit_api_key": "test_key",
            "bybit_api_secret": "test_secret",
            "trading_config": {
                "strategy": "sma",
                "symbols": ["BTCUSDT"],
                "risk_per_trade": 0.01,
            }
        }
    
    @classmethod
    def create_test_market_data(cls, symbol: str = "BTCUSDT") -> Dict[str, Any]:
        """Cria dados de mercado para testes"""
        base_data = cls.MOCK_DATA["market_data"].get(symbol, cls.MOCK_DATA["market_data"]["BTCUSDT"])
        
        return {
            "symbol": symbol,
            "timestamp": 1640995200000,  # 2022-01-01 00:00:00 UTC
            "open": base_data["price"] * 0.99,
            "high": base_data["high"],
            "low": base_data["low"],
            "close": base_data["price"],
            "volume": base_data["volume"],
        }
    
    @classmethod
    def create_test_order_data(cls, symbol: str = "BTCUSDT") -> Dict[str, Any]:
        """Cria dados de ordem para testes"""
        return {
            "symbol": symbol,
            "side": "BUY",
            "type": "MARKET",
            "quantity": 0.001,
            "price": None,
            "client_order_id": "test_order_123",
        }
    
    @classmethod
    def print_config_summary(cls) -> None:
        """Imprime resumo das configurações de teste"""
        print(f"""
🧪 Configuração de Testes Carregada

Ambiente: {cls.ENVIRONMENT}
Testing: {cls.TESTING}
Database: In-Memory SQLite
API Port: {cls.API_PORT}
Dashboard Port: {cls.STREAMLIT_PORT}
Mock Mode: {cls.BYBIT_MOCK_MODE}
Log Level: {cls.LOG_LEVEL}

Configurações de Trading:
- Risk per Trade: {cls.TRADING_CONFIG['default_risk_per_trade']}
- Max Position Size: {cls.TRADING_CONFIG['max_position_size']} USDT
- Paper Trading: {cls.TRADING_CONFIG['enable_paper_trading']}
- Mock Data: {cls.TRADING_CONFIG['mock_market_data']}

🔬 Ambiente OTIMIZADO para TESTES
        """)


# Instância global da configuração
config = TestingConfig()

# Validar configuração na importação
validation_errors = config.validate_config()
if validation_errors:
    print("⚠️  Avisos de configuração de teste:")
    for error in validation_errors:
        print(f"   - {error}")

# Configurar ambiente de teste
config.setup_test_environment()

# Exportar configurações principais
__all__ = [
    "TestingConfig",
    "config",
]

