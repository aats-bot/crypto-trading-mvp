# 🚀 Configuração de Ambiente - Produção
"""
Configurações específicas para ambiente de produção
Localização: /config/environments/production.py
"""
import os
from typing import Dict, Any, List
import secrets


class ProductionConfig:
    """Configurações para ambiente de produção"""
    
    # Identificação do ambiente
    ENVIRONMENT = "production"
    DEBUG = False
    TESTING = False
    
    # Configurações de banco de dados
    DATABASE_URL = os.getenv(
        "DATABASE_URL", 
        "postgresql://trading_user:password@localhost:5432/trading_bot"
    )
    DATABASE_ECHO = False  # Não logar queries em produção
    DATABASE_POOL_SIZE = 20
    DATABASE_MAX_OVERFLOW = 30
    DATABASE_POOL_TIMEOUT = 30
    DATABASE_POOL_RECYCLE = 3600
    
    # Configurações da API
    API_HOST = "0.0.0.0"
    API_PORT = int(os.getenv("API_PORT", "8000"))
    API_RELOAD = False  # Nunca auto-reload em produção
    API_WORKERS = int(os.getenv("API_WORKERS", "4"))
    API_LOG_LEVEL = "warning"
    
    # Configurações do Dashboard
    STREAMLIT_HOST = "0.0.0.0"
    STREAMLIT_PORT = int(os.getenv("STREAMLIT_PORT", "8501"))
    STREAMLIT_DEBUG = False
    
    # Configurações de segurança (muito restritivas)
    SECRET_KEY = os.getenv("SECRET_KEY")
    ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
    JWT_EXPIRATION_HOURS = 8  # Token válido por 8h em produção
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "").split(",") if os.getenv("CORS_ORIGINS") else []
    
    # Configurações da Bybit (mainnet)
    BYBIT_TESTNET = False
    BYBIT_API_KEY = os.getenv("BYBIT_API_KEY")
    BYBIT_API_SECRET = os.getenv("BYBIT_API_SECRET")
    BYBIT_TIMEOUT = 10
    BYBIT_RATE_LIMIT = 5  # Mais conservador em produção
    
    # Configurações de logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "WARNING")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE = os.getenv("LOG_FILE", "/var/log/trading-bot/production.log")
    LOG_MAX_SIZE = 50 * 1024 * 1024  # 50MB
    LOG_BACKUP_COUNT = 10
    LOG_TO_CONSOLE = False  # Apenas arquivo em produção
    
    # Configurações de cache (habilitado em produção)
    CACHE_ENABLED = True
    CACHE_TTL = 600  # 10 minutos
    CACHE_MAX_SIZE = 1000
    
    # Configurações de rate limiting
    RATE_LIMIT_ENABLED = True
    RATE_LIMIT_PER_MINUTE = 60
    RATE_LIMIT_PER_HOUR = 1000
    RATE_LIMIT_BURST = 10
    
    # Configurações de trading
    TRADING_CONFIG = {
        "default_risk_per_trade": 0.02,     # 2% em produção
        "max_position_size": 5000.0,        # Maior em produção
        "max_daily_loss": 500.0,            # Maior em produção
        "max_open_positions": 10,           # Mais posições em produção
        "default_symbols": [                # Mais símbolos em produção
            "BTCUSDT", "ETHUSDT", "ADAUSDT", 
            "SOLUSDT", "DOTUSDT", "LINKUSDT"
        ],
        "update_interval": 10,              # 10 segundos
        "enable_paper_trading": False,      # Trading real em produção
        "emergency_stop_loss": 0.10,        # 10% emergency stop
        "daily_loss_reset_hour": 0,         # Reset às 00:00 UTC
    }
    
    # Configurações de monitoramento
    MONITORING_ENABLED = True
    METRICS_ENDPOINT = "/metrics"
    HEALTH_CHECK_ENDPOINT = "/health"
    PROMETHEUS_PORT = int(os.getenv("PROMETHEUS_PORT", "9090"))
    
    # Configurações de email
    EMAIL_ENABLED = True
    EMAIL_BACKEND = "smtp"
    EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
    EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
    EMAIL_USE_TLS = True
    EMAIL_USERNAME = os.getenv("EMAIL_USERNAME")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    EMAIL_FROM = os.getenv("EMAIL_FROM", "noreply@trading-bot.com")
    
    # Configurações de notificações
    NOTIFICATIONS_ENABLED = True
    NOTIFICATION_CHANNELS = ["email", "webhook", "log"]
    WEBHOOK_URL = os.getenv("WEBHOOK_URL")
    WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
    
    # Configurações de backup
    BACKUP_ENABLED = True
    BACKUP_INTERVAL_HOURS = 6  # A cada 6 horas
    BACKUP_RETENTION_DAYS = 30
    BACKUP_S3_BUCKET = os.getenv("BACKUP_S3_BUCKET")
    BACKUP_S3_REGION = os.getenv("BACKUP_S3_REGION", "us-east-1")
    
    # Configurações de performance
    PERFORMANCE_MONITORING = True
    SLOW_QUERY_THRESHOLD = 0.5  # 500ms
    REQUEST_TIMEOUT = 30
    
    # Configurações de SSL/TLS
    SSL_ENABLED = True
    SSL_CERT_PATH = os.getenv("SSL_CERT_PATH", "/etc/ssl/certs/trading-bot.crt")
    SSL_KEY_PATH = os.getenv("SSL_KEY_PATH", "/etc/ssl/private/trading-bot.key")
    
    # Símbolos permitidos para trading (completo em produção)
    ALLOWED_SYMBOLS = [
        "BTCUSDT", "ETHUSDT", "ADAUSDT", "SOLUSDT", "DOTUSDT",
        "LINKUSDT", "AVAXUSDT", "MATICUSDT", "ATOMUSDT", "NEARUSDT",
        "FTMUSDT", "ALGOUSDT", "VETUSDT", "ICPUSDT", "FILUSDT"
    ]
    
    # Configurações de WebSocket
    WEBSOCKET_ENABLED = True
    WEBSOCKET_HOST = "0.0.0.0"
    WEBSOCKET_PORT = int(os.getenv("WEBSOCKET_PORT", "8765"))
    WEBSOCKET_MAX_CONNECTIONS = 1000
    
    # Configurações de Redis (se usado)
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    REDIS_MAX_CONNECTIONS = 50
    
    # Configurações de segurança avançada
    SECURITY_CONFIG = {
        "password_min_length": 12,
        "password_require_special": True,
        "password_require_uppercase": True,
        "password_require_numbers": True,
        "session_timeout_minutes": 30,
        "max_login_attempts": 3,
        "lockout_duration_minutes": 15,
        "require_2fa": False,  # Pode ser habilitado futuramente
    }
    
    # Configurações de auditoria
    AUDIT_ENABLED = True
    AUDIT_LOG_FILE = "/var/log/trading-bot/audit.log"
    AUDIT_EVENTS = [
        "login", "logout", "trade_executed", "config_changed",
        "api_key_changed", "password_changed", "emergency_stop"
    ]
    
    @classmethod
    def get_database_config(cls) -> Dict[str, Any]:
        """Retorna configurações específicas do banco de dados"""
        return {
            "url": cls.DATABASE_URL,
            "echo": cls.DATABASE_ECHO,
            "pool_size": cls.DATABASE_POOL_SIZE,
            "max_overflow": cls.DATABASE_MAX_OVERFLOW,
            "pool_timeout": cls.DATABASE_POOL_TIMEOUT,
            "pool_recycle": cls.DATABASE_POOL_RECYCLE,
            "pool_pre_ping": True,
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
            "access_log": False,  # Desabilitar em produção
            "timeout_keep_alive": 5,
            "timeout_graceful_shutdown": 30,
        }
    
    @classmethod
    def get_logging_config(cls) -> Dict[str, Any]:
        """Retorna configurações de logging para produção"""
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "production": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                },
                "json": {
                    "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
                    "format": "%(asctime)s %(name)s %(levelname)s %(filename)s %(lineno)d %(message)s"
                },
            },
            "handlers": {
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": cls.LOG_LEVEL,
                    "formatter": "production",
                    "filename": cls.LOG_FILE,
                    "maxBytes": cls.LOG_MAX_SIZE,
                    "backupCount": cls.LOG_BACKUP_COUNT,
                },
                "error_file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": "ERROR",
                    "formatter": "json",
                    "filename": cls.LOG_FILE.replace(".log", "_errors.log"),
                    "maxBytes": cls.LOG_MAX_SIZE,
                    "backupCount": cls.LOG_BACKUP_COUNT,
                },
                "syslog": {
                    "class": "logging.handlers.SysLogHandler",
                    "level": "WARNING",
                    "formatter": "production",
                    "address": "/dev/log",
                },
            },
            "loggers": {
                "": {  # Root logger
                    "level": cls.LOG_LEVEL,
                    "handlers": ["file", "error_file", "syslog"],
                },
                "uvicorn": {
                    "level": "WARNING",
                    "handlers": ["file"],
                    "propagate": False,
                },
                "sqlalchemy": {
                    "level": "WARNING",
                    "handlers": ["file"],
                    "propagate": False,
                },
                "trading_bot": {
                    "level": "INFO",
                    "handlers": ["file", "error_file"],
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
            "retry_attempts": 3,
            "retry_delay": 1.0,
        }
    
    @classmethod
    def get_trading_config(cls) -> Dict[str, Any]:
        """Retorna configurações de trading"""
        return cls.TRADING_CONFIG.copy()
    
    @classmethod
    def validate_config(cls) -> List[str]:
        """Valida configurações críticas para produção"""
        errors = []
        
        # Validar chaves obrigatórias
        if not cls.SECRET_KEY:
            errors.append("SECRET_KEY é obrigatória em produção")
        elif len(cls.SECRET_KEY) < 32:
            errors.append("SECRET_KEY deve ter pelo menos 32 caracteres")
        
        if not cls.ENCRYPTION_KEY:
            errors.append("ENCRYPTION_KEY é obrigatória em produção")
        elif len(cls.ENCRYPTION_KEY) < 32:
            errors.append("ENCRYPTION_KEY deve ter pelo menos 32 caracteres")
        
        if not cls.BYBIT_API_KEY:
            errors.append("BYBIT_API_KEY é obrigatória")
        
        if not cls.BYBIT_API_SECRET:
            errors.append("BYBIT_API_SECRET é obrigatória")
        
        # Validar configurações de banco
        if not cls.DATABASE_URL or "sqlite" in cls.DATABASE_URL.lower():
            errors.append("DATABASE_URL deve usar PostgreSQL em produção")
        
        # Validar configurações de email
        if cls.EMAIL_ENABLED:
            if not cls.EMAIL_USERNAME:
                errors.append("EMAIL_USERNAME é obrigatório quando email está habilitado")
            if not cls.EMAIL_PASSWORD:
                errors.append("EMAIL_PASSWORD é obrigatório quando email está habilitado")
        
        # Validar SSL
        if cls.SSL_ENABLED:
            import os
            if not os.path.exists(cls.SSL_CERT_PATH):
                errors.append(f"Certificado SSL não encontrado: {cls.SSL_CERT_PATH}")
            if not os.path.exists(cls.SSL_KEY_PATH):
                errors.append(f"Chave SSL não encontrada: {cls.SSL_KEY_PATH}")
        
        # Validar CORS
        if not cls.CORS_ORIGINS:
            errors.append("CORS_ORIGINS deve ser definido em produção")
        
        # Validar configurações de trading
        if cls.TRADING_CONFIG["default_risk_per_trade"] > 0.05:
            errors.append("default_risk_per_trade não deve exceder 5% em produção")
        
        return errors
    
    @classmethod
    def setup_directories(cls) -> None:
        """Cria diretórios necessários para produção"""
        import os
        
        directories = [
            "/var/log/trading-bot",
            "/var/lib/trading-bot/data",
            "/var/lib/trading-bot/backups",
            "/var/lib/trading-bot/exports",
            "/etc/trading-bot",
        ]
        
        for directory in directories:
            try:
                os.makedirs(directory, exist_ok=True, mode=0o755)
            except PermissionError:
                print(f"⚠️  Não foi possível criar diretório: {directory}")
                print("   Execute como root ou ajuste permissões")
    
    @classmethod
    def get_cors_config(cls) -> Dict[str, Any]:
        """Retorna configurações de CORS para produção"""
        return {
            "allow_origins": cls.CORS_ORIGINS,
            "allow_credentials": True,
            "allow_methods": ["GET", "POST", "PUT", "DELETE"],
            "allow_headers": ["Authorization", "Content-Type"],
            "expose_headers": ["X-Total-Count", "X-Rate-Limit-Remaining"],
        }
    
    @classmethod
    def get_security_config(cls) -> Dict[str, Any]:
        """Retorna configurações de segurança"""
        return {
            "secret_key": cls.SECRET_KEY,
            "encryption_key": cls.ENCRYPTION_KEY,
            "jwt_expiration_hours": cls.JWT_EXPIRATION_HOURS,
            **cls.SECURITY_CONFIG
        }
    
    @classmethod
    def get_monitoring_config(cls) -> Dict[str, Any]:
        """Retorna configurações de monitoramento"""
        return {
            "enabled": cls.MONITORING_ENABLED,
            "metrics_endpoint": cls.METRICS_ENDPOINT,
            "health_endpoint": cls.HEALTH_CHECK_ENDPOINT,
            "prometheus_port": cls.PROMETHEUS_PORT,
            "performance_monitoring": cls.PERFORMANCE_MONITORING,
            "slow_query_threshold": cls.SLOW_QUERY_THRESHOLD,
        }
    
    @classmethod
    def get_backup_config(cls) -> Dict[str, Any]:
        """Retorna configurações de backup"""
        return {
            "enabled": cls.BACKUP_ENABLED,
            "interval_hours": cls.BACKUP_INTERVAL_HOURS,
            "retention_days": cls.BACKUP_RETENTION_DAYS,
            "s3_bucket": cls.BACKUP_S3_BUCKET,
            "s3_region": cls.BACKUP_S3_REGION,
        }
    
    @classmethod
    def generate_secret_key(cls) -> str:
        """Gera uma chave secreta segura"""
        return secrets.token_urlsafe(32)
    
    @classmethod
    def generate_encryption_key(cls) -> str:
        """Gera uma chave de criptografia segura"""
        return secrets.token_urlsafe(32)
    
    @classmethod
    def print_config_summary(cls) -> None:
        """Imprime resumo das configurações de produção"""
        print(f"""
🚀 Configuração de Produção Carregada

Ambiente: {cls.ENVIRONMENT}
Debug: {cls.DEBUG}
Database: PostgreSQL
API Workers: {cls.API_WORKERS}
Bybit Testnet: {cls.BYBIT_TESTNET}
Log Level: {cls.LOG_LEVEL}
SSL Enabled: {cls.SSL_ENABLED}

Configurações de Trading:
- Risk per Trade: {cls.TRADING_CONFIG['default_risk_per_trade']}
- Max Position Size: {cls.TRADING_CONFIG['max_position_size']} USDT
- Max Daily Loss: {cls.TRADING_CONFIG['max_daily_loss']} USDT
- Símbolos: {len(cls.ALLOWED_SYMBOLS)} disponíveis

Segurança:
- Rate Limiting: {cls.RATE_LIMIT_ENABLED}
- CORS Origins: {len(cls.CORS_ORIGINS)} configuradas
- Backup: {cls.BACKUP_ENABLED}
- Monitoring: {cls.MONITORING_ENABLED}

🔒 Configuração SEGURA para PRODUÇÃO
        """)


# Instância global da configuração
config = ProductionConfig()

# Validar configuração na importação
validation_errors = config.validate_config()
if validation_errors:
    print("🚨 ERROS CRÍTICOS DE CONFIGURAÇÃO:")
    for error in validation_errors:
        print(f"   ❌ {error}")
    print("\n⚠️  CORRIJA ESTES ERROS ANTES DE USAR EM PRODUÇÃO!")
    exit(1)

# Criar diretórios necessários
config.setup_directories()

# Exportar configurações principais
__all__ = [
    "ProductionConfig",
    "config",
]

