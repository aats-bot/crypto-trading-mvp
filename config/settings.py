# -*- coding: utf-8 -*-
"""
Crypto Trading MVP - Settings
Configurações flexíveis com Pydantic
"""

import os
from typing import Optional
from pydantic import BaseSettings

class Settings(BaseSettings):
    """
    Configurações do sistema com Pydantic flexível
    Permite campos extras para compatibilidade
    """
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_url: str = "http://api:8000"
    
    # Database Configuration
    postgres_host: str = "postgres"
    postgres_port: int = 5432
    postgres_db: str = "crypto_trading"
    postgres_user: str = "trading_user"
    postgres_password: str = "trading_password_2024"
    
    # Redis Configuration
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_password: str = "redis_password_2024"
    
    # JWT Configuration
    jwt_secret_key: str = "jwt-crypto-trading-mvp-secret-key-2024-very-secure"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440
    
    # Worker Configuration
    worker_concurrency: int = 2
    worker_log_level: str = "INFO"
    
    # Streamlit Configuration
    streamlit_server_port: int = 8501
    streamlit_server_address: str = "0.0.0.0"
    
    # Grafana Configuration
    gf_security_admin_password: str = "admin123"
    gf_users_allow_sign_up: str = "false"
    
    # Trading Configuration
    bybit_api_key: Optional[str] = None
    bybit_api_secret: Optional[str] = None
    bybit_testnet: bool = True
    
    class Config:
        # IMPORTANTE: Permite campos extras para compatibilidade
        extra = "allow"
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

# Instância global das configurações
settings = Settings()
