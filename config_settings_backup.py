"""
Configuration settings for the Crypto Trading MVP
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings"""
    
    # Database Configuration
    database_url: str = Field(
        default="sqlite+aiosqlite:///./crypto_trading.db",
        env="DATABASE_URL"
    )
    database_url_sync: str = Field(
        default="sqlite:///./crypto_trading.db",
        env="DATABASE_URL_SYNC"
    )
    
    # Redis Configuration
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    
    # Bybit API Configuration
    bybit_api_key: Optional[str] = Field(default=None, env="BYBIT_API_KEY")
    bybit_api_secret: Optional[str] = Field(default=None, env="BYBIT_API_SECRET")
    bybit_testnet: bool = Field(default=True, env="BYBIT_TESTNET")
    bybit_base_url: str = Field(
        default="https://api-testnet.bybit.com",
        env="BYBIT_BASE_URL"
    )
    
    # Security
    secret_key: str = Field(
        default="your-super-secret-key-change-this-in-production",
        env="SECRET_KEY"
    )
    encryption_key: str = Field(
        default="your-encryption-key-for-api-keys",
        env="ENCRYPTION_KEY"
    )
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_expire_minutes: int = Field(default=30, env="JWT_EXPIRE_MINUTES")
    
    # Email Configuration
    sendgrid_api_key: Optional[str] = Field(default=None, env="SENDGRID_API_KEY")
    from_email: str = Field(default="noreply@yourdomain.com", env="FROM_EMAIL")
    
    # SMS Configuration
    twilio_account_sid: Optional[str] = Field(default=None, env="TWILIO_ACCOUNT_SID")
    twilio_auth_token: Optional[str] = Field(default=None, env="TWILIO_AUTH_TOKEN")
    twilio_phone_number: Optional[str] = Field(default=None, env="TWILIO_PHONE_NUMBER")
    
    # Monitoring
    sentry_dsn: Optional[str] = Field(default=None, env="SENTRY_DSN")
    prometheus_port: int = Field(default=8000, env="PROMETHEUS_PORT")
    
    # Application Settings
    debug: bool = Field(default=True, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    environment: str = Field(default="development", env="ENVIRONMENT")
    
    # Dashboard Configuration
    streamlit_port: int = Field(default=8501, env="STREAMLIT_PORT")
    streamlit_server_address: str = Field(default="0.0.0.0", env="STREAMLIT_SERVER_ADDRESS")
    
    # API Configuration
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    
    # Rate Limiting
    rate_limit_per_minute: int = Field(default=100, env="RATE_LIMIT_PER_MINUTE")
    login_rate_limit_per_minute: int = Field(default=10, env="LOGIN_RATE_LIMIT_PER_MINUTE")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

