# 🌍 Configurações de Ambiente - Inicialização
"""
Sistema de configuração por ambiente para o MVP Bot de Trading
Localização: /config/environments/__init__.py
"""
import os
from typing import Any, Dict, Type, Union


def get_environment() -> str:
    """
    Determina o ambiente atual baseado em variáveis de ambiente
    
    Returns:
        str: Nome do ambiente ('development', 'production', 'testing')
    """
    # Verificar variável de ambiente explícita
    env = os.getenv("ENVIRONMENT", "").lower()
    if env in ["development", "production", "testing"]:
        return env
    
    # Verificar se está em modo de teste
    if os.getenv("TESTING", "").lower() in ["true", "1", "yes"]:
        return "testing"
    
    # Verificar se está em produção (baseado em outras variáveis)
    prod_indicators = [
        os.getenv("PRODUCTION", "").lower() in ["true", "1", "yes"],
        os.getenv("DEBUG", "").lower() in ["false", "0", "no"],
        "prod" in os.getenv("DATABASE_URL", "").lower(),
        os.getenv("SECRET_KEY", "") != "",
    ]
    
    if any(prod_indicators):
        return "production"
    
    # Padrão: desenvolvimento
    return "development"


def load_config() -> Any:
    """
    Carrega a configuração apropriada baseada no ambiente atual
    
    Returns:
        Config object: Instância da configuração do ambiente
    """
    environment = get_environment()
    
    if environment == "production":
        from .production import config
        return config
    elif environment == "testing":
        from .testing import config
        return config
    else:  # development (padrão)
        from .development import config
        return config


def load_config_class() -> Type:
    """
    Carrega a classe de configuração apropriada
    
    Returns:
        Type: Classe de configuração do ambiente
    """
    environment = get_environment()
    
    if environment == "production":
        from .production import ProductionConfig
        return ProductionConfig
    elif environment == "testing":
        from .testing import TestingConfig
        return TestingConfig
    else:  # development (padrão)
        from .development import DevelopmentConfig
        return DevelopmentConfig


def get_config_summary() -> Dict[str, Any]:
    """
    Retorna resumo das configurações atuais
    
    Returns:
        Dict: Resumo das configurações principais
    """
    config = load_config()
    
    return {
        "environment": config.ENVIRONMENT,
        "debug": config.DEBUG,
        "testing": config.TESTING,
        "database_type": "PostgreSQL" if "postgresql" in config.DATABASE_URL else "SQLite",
        "api_port": config.API_PORT,
        "dashboard_port": config.STREAMLIT_PORT,
        "bybit_testnet": config.BYBIT_TESTNET,
        "log_level": config.LOG_LEVEL,
        "monitoring_enabled": getattr(config, 'MONITORING_ENABLED', False),
        "backup_enabled": getattr(config, 'BACKUP_ENABLED', False),
        "ssl_enabled": getattr(config, 'SSL_ENABLED', False),
    }


def validate_environment() -> Dict[str, Any]:
    """
    Valida o ambiente atual e retorna status
    
    Returns:
        Dict: Status da validação
    """
    environment = get_environment()
    config = load_config()
    
    # Executar validação específica do ambiente
    errors = config.validate_config()
    
    return {
        "environment": environment,
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": [],
        "config_loaded": True,
    }


def switch_environment(new_environment: str) -> bool:
    """
    Muda o ambiente atual (apenas para desenvolvimento/testes)
    
    Args:
        new_environment: Novo ambiente ('development', 'production', 'testing')
        
    Returns:
        bool: True se mudança foi bem-sucedida
    """
    if new_environment not in ["development", "production", "testing"]:
        return False
    
    # Só permitir mudança em desenvolvimento ou testes
    current_env = get_environment()
    if current_env == "production":
        return False
    
    os.environ["ENVIRONMENT"] = new_environment
    return True


def print_environment_info() -> None:
    """Imprime informações detalhadas do ambiente atual"""
    environment = get_environment()
    config = load_config()
    validation = validate_environment()
    
    print(f"""
🌍 Informações do Ambiente de Configuração

Ambiente Atual: {environment.upper()}
Status: {'✅ VÁLIDO' if validation['valid'] else '❌ INVÁLIDO'}

Configurações Principais:
- Debug Mode: {config.DEBUG}
- Testing Mode: {config.TESTING}
- Database: {config.DATABASE_URL}
- API: {config.API_HOST}:{config.API_PORT}
- Dashboard: {config.STREAMLIT_HOST}:{config.STREAMLIT_PORT}
- Bybit Testnet: {config.BYBIT_TESTNET}
- Log Level: {config.LOG_LEVEL}

Recursos Habilitados:
- Monitoring: {getattr(config, 'MONITORING_ENABLED', 'N/A')}
- Backup: {getattr(config, 'BACKUP_ENABLED', 'N/A')}
- SSL: {getattr(config, 'SSL_ENABLED', 'N/A')}
- Cache: {getattr(config, 'CACHE_ENABLED', 'N/A')}
- Rate Limiting: {getattr(config, 'RATE_LIMIT_ENABLED', 'N/A')}
""")
    
    if validation['errors']:
        print("❌ Erros de Configuração:")
        for error in validation['errors']:
            print(f"   - {error}")
    
    if validation['warnings']:
        print("⚠️  Avisos:")
        for warning in validation['warnings']:
            print(f"   - {warning}")
    
    print()


# Configuração global (carregada automaticamente)
current_config = load_config()
current_environment = get_environment()

# Imprimir informações na importação (apenas em desenvolvimento)
if current_environment == "development":
    current_config.print_config_summary()
elif current_environment == "production":
    current_config.print_config_summary()
elif current_environment == "testing":
    # Não imprimir em testes para manter output limpo
    pass

# Exportar configuração e utilitários
__all__ = [
    "get_environment",
    "load_config",
    "load_config_class", 
    "get_config_summary",
    "validate_environment",
    "switch_environment",
    "print_environment_info",
    "current_config",
    "current_environment",
]

