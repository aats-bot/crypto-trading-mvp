"""
Enterprise Settings Configuration
Compatible with all environment variables
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """Enterprise settings with full environment variable support"""
    
    # Database Configuration
    database_url: str = "sqlite:///./crypto_trading.db"
    postgres_db: Optional[str] = None
    postgres_user: Optional[str] = None
    postgres_password: Optional[str] = None
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    
    # Redis Configuration
    redis_url: str = "redis://localhost:6379/0"
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: Optional[str] = None
    redis_db: int = 0
    
    # Security Configuration
    secret_key: str = "dev-secret-key-change-in-production"
    jwt_secret_key: Optional[str] = None
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440
    encryption_key: str = "dev-encryption-key-change-in-production"
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_url: Optional[str] = None
    debug: bool = False
    log_level: str = "INFO"
    
    # Worker Configuration
    worker_concurrency: Optional[str] = None
    worker_log_level: Optional[str] = None
    
    # Streamlit Configuration
    streamlit_server_port: Optional[str] = None
    streamlit_server_address: str = "0.0.0.0"
    streamlit_server_headless: str = "true"
    streamlit_browser_gather_usage_stats: str = "false"
    streamlit_server_enable_cors: str = "false"
    streamlit_server_enable_xsrf_protection: str = "false"
    streamlit_server_max_upload_size: str = "200"
    
    # Grafana Configuration
    gf_security_admin_password: Optional[str] = None
    gf_users_allow_sign_up: Optional[str] = None
    gf_install_plugins: Optional[str] = None
    
    # Environment
    environment: str = "development"
    
    # Trading Configuration
    bybit_api_key: Optional[str] = None
    bybit_api_secret: Optional[str] = None
    
    # Monitoring
    prometheus_port: int = 9090
    grafana_port: int = 3000
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"  # Permite variáveis extras
        case_sensitive = False
        
    def __init__(self, **kwargs):
        """Initialize with environment variables"""
        # Carregar todas as variáveis de ambiente
        env_vars = {}
        for key, value in os.environ.items():
            # Converter para lowercase para compatibilidade
            env_vars[key.lower()] = value
            
        # Merge com kwargs
        env_vars.update(kwargs)
        
        super().__init__(**env_vars)
    
    @property
    def database_url_async(self) -> str:
        """Get async database URL"""
        if self.postgres_db and self.postgres_user and self.postgres_password:
            return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        return self.database_url.replace("sqlite://", "sqlite+aiosqlite://")
    
    @property
    def redis_url_full(self) -> str:
        """Get full Redis URL"""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

# Create settings instance
settings = Settings()
