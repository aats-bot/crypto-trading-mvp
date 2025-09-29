# 🔧 Configuração de Ambiente - Desenvolvimento
"""
Configurações específicas para ambiente de desenvolvimento
Localização: /config/environments/development.py
"""
import os
from typing import Dict, Any, List


class DevelopmentConfig:
    """Configurações para ambiente de desenvolvimento"""
    
    # Identificação do ambiente
    ENVIRONMENT = "development"
    DEBUG = True
    TESTING = False
    
    # Configurações de banco de dados
    DATABASE_URL = os.getenv(
        "DATABASE_URL", 
        "sqlite:///./data/database/trading_bot_dev.db"
    )
    DATABASE_ECHO = True  # Log de queries SQL
    DATABASE_POOL_SIZE = 5
    DATABASE_MAX_OVERFLOW = 10
    
    # Configurações da API
    API_HOST = "0.0.0.0"
    API_PORT = 8000
    API_RELOAD = True  # Auto-reload em desenvolvimento
    API_WORKERS = 1
    API_LOG_LEVEL = "debug"
    
    # Configurações do Dashboard
    STREAMLIT_HOST = "0.0.0.0"
    STREAMLIT_PORT = 8501
    STREAMLIT_DEBUG = True
    
    # Configurações de segurança (menos restritivas em dev)
    SECRET_KEY = os.getenv(
        "SECRET_KEY", 
        "dev-secret-key-not-for-production-use-only"
    )
    ENCRYPTION_KEY = os.getenv(
        "ENCRYPTION_KEY",
        "dev-encryption-key-32-bytes-long"
    )
    JWT_EXPIRATION_HOURS = 24  # Token válido por 24h em dev
    CORS_ORIGINS = ["*"]  # Permitir todas as origens em dev
    
    # Configurações da Bybit (testnet)
    BYBIT_TESTNET = True
    BYBIT_API_KEY = os.getenv("BYBIT_API_KEY", "")
    BYBIT_API_SECRET = os.getenv("BYBIT_API_SECRET", "")
    BYBIT_TIMEOUT = 30
    BYBIT_RATE_LIMIT = 10  # Requests por segundo
    
    # Configurações de logging
    LOG_LEVEL = "DEBUG"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE = "logs/development.log"
    LOG_MAX_SIZE = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 5
    LOG_TO_CONSOLE = True
    
    # Configurações de cache (desabilitado em dev)
    CACHE_ENABLED = False
    CACHE_TTL = 300  # 5 minutos
    
    # Configurações de rate limiting (mais permissivas)
    RATE_LIMIT_ENABLED = False
    RATE_LIMIT_PER_MINUTE = 1000
    RATE_LIMIT_PER_HOUR = 10000
    
    # Configurações de trading
    TRADING_CONFIG = {
        "default_risk_per_trade": 0.01,  # 1% em desenvolvimento
        "max_position_size": 100.0,     # Menor em dev
        "max_daily_loss": 20.0,         # Menor em dev
        "max_open_positions": 3,        # Menos posições em dev
        "default_symbols": ["BTCUSDT"], # Apenas BTC em dev
        "update_interval": 30,          # 30 segundos
        "enable_paper_trading": True,   # Paper trading em dev
    }
    
    # Configurações de monitoramento
    MONITORING_ENABLED = True
    METRICS_ENDPOINT = "/metrics"
    HEALTH_CHECK_ENDPOINT = "/health"
    
    # Configurações de email (mock em desenvolvimento)
    EMAIL_ENABLED = False
    EMAIL_BACKEND = "console"  # Imprimir emails no console
    EMAIL_HOST = "localhost"
    EMAIL_PORT = 1025
    EMAIL_USE_TLS = False
    EMAIL_FROM = "dev@trading-bot.local"
    
    # Configurações de notificações
    NOTIFICATIONS_ENABLED = True
    NOTIFICATION_CHANNELS = ["console", "log"]  # Apenas console e log em dev
    
    # Configurações de backup
    BACKUP_ENABLED = False  # Desabilitado em dev
    BACKUP_INTERVAL_HOURS = 24
    BACKUP_RETENTION_DAYS = 7
    
    # Configurações de performance
    PERFORMANCE_MONITORING = True
    SLOW_QUERY_THRESHOLD = 1.0  # 1 segundo
    
    # Configurações específicas de desenvolvimento
    DEV_CONFIG = {
        "auto_migrate": True,           # Migrar DB automaticamente
        "seed_data": True,             # Inserir dados de exemplo
        "mock_external_apis": False,   # Usar APIs reais mesmo em dev
        "enable_debug_toolbar": True,  # Toolbar de debug
        "profile_requests": True,      # Profiling de requisições
        "validate_schemas": True,      # Validação rigorosa de schemas
    }
    
    # Símbolos permitidos para trading (limitado em dev)
    ALLOWED_SYMBOLS = [
        "BTCUSDT", "ETHUSDT", "ADAUSDT"
    ]
    
    # Configurações de WebSocket (se implementado)
    WEBSOCKET_ENABLED = True
    WEBSOCKET_HOST = "0.0.0.0"
    WEBSOCKET_PORT = 8765
    
    # Configurações de testes
    TEST_DATABASE_URL = "sqlite:///:memory:"
    TEST_API_KEY = "test_api_key"
    TEST_API_SECRET = "test_api_secret"
    
    @classmethod
    def get_database_config(cls) -> Dict[str, Any]:
        """Retorna configurações específicas do banco de dados"""
        return {
            "url": cls.DATABASE_URL,
            "echo": cls.DATABASE_ECHO,
            "pool_size": cls.DATABASE_POOL_SIZE,
            "max_overflow": cls.DATABASE_MAX_OVERFLOW,
            "pool_pre_ping": True,
            "pool_recycle": 3600,
        }
    
    @classmethod
    def get_api_config(cls) -> Dict[str, Any]:
        """Retorna configurações específicas da API"""
        return {
            "host": cls.API_HOST,
            "port": cls.API_PORT,
            "reload": cls.API_RELOAD,
            "workers": cls.API_WORKERS,
            "log_level": cls.API_LOG_LEVEL,
            "access_log": True,
        }
    
    @classmethod
    def get_logging_config(cls) -> Dict[str, Any]:
        """Retorna configurações de logging"""
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": cls.LOG_FORMAT,
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                },
                "detailed": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": cls.LOG_LEVEL,
                    "formatter": "default",
                    "stream": "ext://sys.stdout",
                },
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": cls.LOG_LEVEL,
                    "formatter": "detailed",
                    "filename": cls.LOG_FILE,
                    "maxBytes": cls.LOG_MAX_SIZE,
                    "backupCount": cls.LOG_BACKUP_COUNT,
                },
            },
            "loggers": {
                "": {  # Root logger
                    "level": cls.LOG_LEVEL,
                    "handlers": ["console", "file"] if cls.LOG_TO_CONSOLE else ["file"],
                },
                "uvicorn": {
                    "level": "INFO",
                    "handlers": ["console", "file"],
                    "propagate": False,
                },
                "sqlalchemy": {
                    "level": "INFO",
                    "handlers": ["file"],
                    "propagate": False,
                },
            },
        }
    
    @classmethod
    def get_bybit_config(cls) -> Dict[str, Any]:
        """Retorna configurações da Bybit"""
        return {
            "api_key": cls.BYBIT_API_KEY,
            "api_secret": cls.BYBIT_API_SECRET,
            "testnet": cls.BYBIT_TESTNET,
            "timeout": cls.BYBIT_TIMEOUT,
            "rate_limit": cls.BYBIT_RATE_LIMIT,
        }
    
    @classmethod
    def get_trading_config(cls) -> Dict[str, Any]:
        """Retorna configurações de trading"""
        return cls.TRADING_CONFIG.copy()
    
    @classmethod
    def validate_config(cls) -> List[str]:
        """Valida configurações e retorna lista de erros"""
        errors = []
        
        # Validar chaves obrigatórias
        if not cls.SECRET_KEY or cls.SECRET_KEY == "dev-secret-key-not-for-production-use-only":
            errors.append("SECRET_KEY deve ser definida para desenvolvimento")
        
        if not cls.BYBIT_API_KEY:
            errors.append("BYBIT_API_KEY é obrigatória")
        
        if not cls.BYBIT_API_SECRET:
            errors.append("BYBIT_API_SECRET é obrigatória")
        
        # Validar configurações de trading
        if cls.TRADING_CONFIG["default_risk_per_trade"] <= 0:
            errors.append("default_risk_per_trade deve ser maior que 0")
        
        if cls.TRADING_CONFIG["max_position_size"] <= 0:
            errors.append("max_position_size deve ser maior que 0")
        
        # Validar portas
        if not (1024 <= cls.API_PORT <= 65535):
            errors.append("API_PORT deve estar entre 1024 e 65535")
        
        if not (1024 <= cls.STREAMLIT_PORT <= 65535):
            errors.append("STREAMLIT_PORT deve estar entre 1024 e 65535")
        
        return errors
    
    @classmethod
    def setup_directories(cls) -> None:
        """Cria diretórios necessários"""
        import os
        
        directories = [
            "logs",
            "data/database",
            "data/backups",
            "data/exports",
            "data/temp",
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    @classmethod
    def get_cors_config(cls) -> Dict[str, Any]:
        """Retorna configurações de CORS"""
        return {
            "allow_origins": cls.CORS_ORIGINS,
            "allow_credentials": True,
            "allow_methods": ["*"],
            "allow_headers": ["*"],
        }
    
    @classmethod
    def get_security_config(cls) -> Dict[str, Any]:
        """Retorna configurações de segurança"""
        return {
            "secret_key": cls.SECRET_KEY,
            "encryption_key": cls.ENCRYPTION_KEY,
            "jwt_expiration_hours": cls.JWT_EXPIRATION_HOURS,
            "password_min_length": 8,
            "password_require_special": False,  # Menos restritivo em dev
            "session_timeout_minutes": 60,
        }
    
    @classmethod
    def print_config_summary(cls) -> None:
        """Imprime resumo das configurações"""
        print(f"""
🔧 Configuração de Desenvolvimento Carregada

Ambiente: {cls.ENVIRONMENT}
Debug: {cls.DEBUG}
Database: {cls.DATABASE_URL}
API: {cls.API_HOST}:{cls.API_PORT}
Dashboard: {cls.STREAMLIT_HOST}:{cls.STREAMLIT_PORT}
Bybit Testnet: {cls.BYBIT_TESTNET}
Log Level: {cls.LOG_LEVEL}

Configurações de Trading:
- Risk per Trade: {cls.TRADING_CONFIG['default_risk_per_trade']}
- Max Position Size: {cls.TRADING_CONFIG['max_position_size']} USDT
- Max Daily Loss: {cls.TRADING_CONFIG['max_daily_loss']} USDT
- Símbolos: {', '.join(cls.ALLOWED_SYMBOLS)}

⚠️  Esta é uma configuração de DESENVOLVIMENTO
   Não use em produção!
        """)


# Instância global da configuração
config = DevelopmentConfig()

# Validar configuração na importação
validation_errors = config.validate_config()
if validation_errors:
    print("⚠️  Erros de configuração encontrados:")
    for error in validation_errors:
        print(f"   - {error}")

# Criar diretórios necessários
config.setup_directories()

# Exportar configurações principais
__all__ = [
    "DevelopmentConfig",
    "config",
]

