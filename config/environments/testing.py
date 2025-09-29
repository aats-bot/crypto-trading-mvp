# 🧪 Configuração de Ambiente de Testes - MVP Bot de Trading
"""
Configurações específicas para ambiente de testes
Localização: /config/environments/testing.py
"""
import os
import tempfile
from typing import Dict, Any


class TestingConfig:
    """Configurações para ambiente de testes"""
    
    # Identificação do ambiente
    ENVIRONMENT = "testing"
    DEBUG = False  # Desabilitado para performance nos testes
    TESTING = True
    
    # Banco de dados em memória para testes rápidos
    DATABASE_URL = "sqlite:///:memory:"
    DATABASE_ECHO = False  # Desabilitar logs SQL nos testes
    
    # Redis em memória (fakeredis)
    REDIS_URL = "redis://localhost:6379/15"  # DB 15 para testes
    USE_FAKE_REDIS = True
    
    # JWT para testes
    JWT_SECRET_KEY = "test-secret-key-not-for-production"
    JWT_ALGORITHM = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS = 7
    
    # Criptografia para testes
    ENCRYPTION_KEY = "test-encryption-key-32-bytes-long"
    
    # APIs externas - usar mocks
    BYBIT_API_KEY = "test_api_key"
    BYBIT_API_SECRET = "test_api_secret"
    BYBIT_TESTNET = True
    USE_MOCK_EXCHANGE = True  # Usar exchange mockada
    
    # Configurações de trading para testes
    PAPER_TRADING = True  # Sempre paper trading em testes
    MAX_POSITION_SIZE = 100.0  # Posições pequenas para testes
    MAX_DAILY_LOSS = 50.0  # Limite baixo para testes
    
    # Logging - mínimo para performance
    LOG_LEVEL = "WARNING"  # Apenas warnings e erros
    LOG_TO_FILE = False
    LOG_TO_CONSOLE = False
    AUDIT_LOG_ENABLED = False
    
    # Diretórios temporários
    DATA_DIR = tempfile.mkdtemp(prefix="trading_test_")
    LOG_DIR = os.path.join(DATA_DIR, "logs")
    BACKUP_DIR = os.path.join(DATA_DIR, "backups")
    
    # Métricas e monitoramento - desabilitados
    METRICS_ENABLED = False
    PROMETHEUS_PORT = 8081  # Porta diferente para evitar conflitos
    HEALTH_CHECK_ENABLED = False
    
    # Rate limiting - mais permissivo para testes
    RATE_LIMIT_ENABLED = False
    API_RATE_LIMIT = "1000/minute"
    
    # Segurança - relaxada para testes
    CORS_ORIGINS = ["*"]
    ALLOWED_HOSTS = ["*"]
    SSL_REQUIRED = False
    SECURE_COOKIES = False
    
    # Email - usar mock
    EMAIL_ENABLED = False
    EMAIL_BACKEND = "mock"
    
    # Configurações específicas de teste
    TEST_DATABASE_CLEANUP = True  # Limpar DB após cada teste
    TEST_FIXTURES_ENABLED = True  # Carregar dados de teste
    TEST_MOCK_EXTERNAL_APIS = True  # Mockar APIs externas
    TEST_FAST_MODE = True  # Pular delays desnecessários
    
    # Timeouts reduzidos para testes rápidos
    HTTP_TIMEOUT = 5  # 5 segundos
    DATABASE_TIMEOUT = 5
    REDIS_TIMEOUT = 2
    
    # Configurações de estratégias para testes
    STRATEGY_CONFIG = {
        "sma": {
            "short_period": 5,  # Períodos menores para testes rápidos
            "long_period": 10,
            "enabled": True
        },
        "rsi": {
            "period": 7,  # Período menor
            "oversold": 30,
            "overbought": 70,
            "enabled": True
        },
        "ppp_vishva": {
            "enabled": True,
            "test_mode": True,  # Modo de teste específico
            "fast_execution": True
        }
    }
    
    # Dados de teste
    TEST_DATA = {
        "users": [
            {
                "email": "test@example.com",
                "password": "testpass123",
                "is_active": True
            },
            {
                "email": "admin@example.com", 
                "password": "adminpass123",
                "is_admin": True
            }
        ],
        "symbols": ["BTCUSDT", "ETHUSDT", "ADAUSDT"],
        "sample_prices": [
            {"symbol": "BTCUSDT", "price": 50000.0, "timestamp": "2024-01-01T00:00:00Z"},
            {"symbol": "ETHUSDT", "price": 3000.0, "timestamp": "2024-01-01T00:00:00Z"}
        ]
    }
    
    # Configurações de performance para testes
    ASYNC_POOL_SIZE = 5  # Pool menor para testes
    MAX_CONCURRENT_REQUESTS = 10
    CACHE_TTL = 60  # Cache curto para testes
    
    @classmethod
    def get_database_url(cls) -> str:
        """Obter URL do banco de dados para testes"""
        return cls.DATABASE_URL
    
    @classmethod
    def get_redis_url(cls) -> str:
        """Obter URL do Redis para testes"""
        return cls.REDIS_URL
    
    @classmethod
    def setup_test_environment(cls) -> Dict[str, Any]:
        """Configurar ambiente de teste"""
        # Criar diretórios temporários
        os.makedirs(cls.LOG_DIR, exist_ok=True)
        os.makedirs(cls.BACKUP_DIR, exist_ok=True)
        
        # Configurar variáveis de ambiente para testes
        test_env = {
            "ENVIRONMENT": cls.ENVIRONMENT,
            "TESTING": "true",
            "DATABASE_URL": cls.DATABASE_URL,
            "REDIS_URL": cls.REDIS_URL,
            "JWT_SECRET_KEY": cls.JWT_SECRET_KEY,
            "LOG_LEVEL": cls.LOG_LEVEL,
            "PAPER_TRADING": "true",
            "USE_MOCK_EXCHANGE": "true"
        }
        
        # Aplicar variáveis de ambiente
        for key, value in test_env.items():
            os.environ[key] = str(value)
        
        return {
            "status": "configured",
            "environment": cls.ENVIRONMENT,
            "database": "in-memory",
            "redis": "fake" if cls.USE_FAKE_REDIS else "real",
            "data_dir": cls.DATA_DIR,
            "mock_apis": cls.TEST_MOCK_EXTERNAL_APIS
        }
    
    @classmethod
    def cleanup_test_environment(cls):
        """Limpar ambiente de teste"""
        import shutil
        
        try:
            # Remover diretório temporário
            if os.path.exists(cls.DATA_DIR):
                shutil.rmtree(cls.DATA_DIR)
            
            # Limpar variáveis de ambiente de teste
            test_vars = [
                "TESTING", "USE_MOCK_EXCHANGE", "PAPER_TRADING"
            ]
            
            for var in test_vars:
                if var in os.environ:
                    del os.environ[var]
                    
        except Exception as e:
            print(f"Warning: Failed to cleanup test environment: {e}")
    
    @classmethod
    def get_test_fixtures(cls) -> Dict[str, Any]:
        """Obter dados de teste (fixtures)"""
        return cls.TEST_DATA
    
    @classmethod
    def is_fast_mode(cls) -> bool:
        """Verificar se está em modo rápido"""
        return cls.TEST_FAST_MODE
    
    @classmethod
    def get_mock_config(cls) -> Dict[str, Any]:
        """Configuração para mocks"""
        return {
            "exchange": {
                "name": "mock_bybit",
                "balance": 10000.0,
                "positions": [],
                "orders": [],
                "latency": 0.1  # Latência simulada baixa
            },
            "market_data": {
                "symbols": cls.TEST_DATA["symbols"],
                "price_range": {"min": 1000, "max": 100000},
                "volatility": 0.02  # 2% de volatilidade
            },
            "responses": {
                "success_rate": 0.95,  # 95% de sucesso
                "error_types": ["network", "rate_limit", "invalid_order"]
            }
        }
    
    @classmethod
    def validate_test_config(cls) -> Dict[str, Any]:
        """Validar configuração de teste"""
        issues = []
        
        # Verificar configurações críticas
        if not cls.TESTING:
            issues.append("TESTING flag not set")
        
        if not cls.PAPER_TRADING:
            issues.append("PAPER_TRADING should be enabled in tests")
        
        if cls.DATABASE_URL != "sqlite:///:memory:":
            issues.append("Should use in-memory database for tests")
        
        if cls.LOG_LEVEL not in ["WARNING", "ERROR", "CRITICAL"]:
            issues.append("Log level too verbose for tests")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "config": {
                "environment": cls.ENVIRONMENT,
                "testing": cls.TESTING,
                "paper_trading": cls.PAPER_TRADING,
                "database": "in-memory" if ":memory:" in cls.DATABASE_URL else "persistent",
                "mocks_enabled": cls.TEST_MOCK_EXTERNAL_APIS
            }
        }


# Configuração global para testes
config = TestingConfig()

# Função de conveniência para pytest
def pytest_configure():
    """Configuração automática para pytest"""
    return TestingConfig.setup_test_environment()

def pytest_unconfigure():
    """Limpeza automática após pytest"""
    TestingConfig.cleanup_test_environment()


# Fixtures comuns para testes
TEST_FIXTURES = {
    "sample_ohlcv": [
        {"open": 50000, "high": 51000, "low": 49000, "close": 50500, "volume": 1000},
        {"open": 50500, "high": 52000, "low": 50000, "close": 51500, "volume": 1200},
        {"open": 51500, "high": 52500, "low": 51000, "close": 52000, "volume": 900},
        {"open": 52000, "high": 53000, "low": 51500, "close": 52500, "volume": 1100},
        {"open": 52500, "high": 53500, "low": 52000, "close": 53000, "volume": 1300}
    ],
    
    "sample_trades": [
        {"symbol": "BTCUSDT", "side": "buy", "quantity": 0.1, "price": 50000, "pnl": 50},
        {"symbol": "BTCUSDT", "side": "sell", "quantity": 0.1, "price": 50500, "pnl": 50},
        {"symbol": "ETHUSDT", "side": "buy", "quantity": 1.0, "price": 3000, "pnl": -30},
        {"symbol": "ETHUSDT", "side": "sell", "quantity": 1.0, "price": 2970, "pnl": -30}
    ],
    
    "sample_indicators": {
        "sma_5": [50100, 50300, 50500, 50700, 50900],
        "sma_10": [50000, 50200, 50400, 50600, 50800],
        "rsi": [45.5, 52.3, 58.7, 61.2, 55.8],
        "atr": [500, 520, 480, 510, 490]
    }
}


# Exportar configuração
__all__ = [
    "TestingConfig",
    "config",
    "pytest_configure", 
    "pytest_unconfigure",
    "TEST_FIXTURES"
]

