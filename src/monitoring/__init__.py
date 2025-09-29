# 📊 Sistema de Monitoramento - Inicialização
"""
Sistema completo de monitoramento e métricas para o MVP Bot de Trading
Localização: /src/monitoring/__init__.py
"""

# Importar componentes principais de monitoramento
from .metrics import (
    MetricsCollector,
    PrometheusMetrics,
    BusinessMetrics,
    SystemMetrics,
    TradingMetrics,
    get_metrics_collector,
    track_http_requests,
)

# Lista de todos os componentes disponíveis
__all__ = [
    # Métricas
    "MetricsCollector",
    "PrometheusMetrics", 
    "BusinessMetrics",
    "SystemMetrics",
    "TradingMetrics",
    "get_metrics_collector",
    "track_http_requests",
]

# Versão do sistema de monitoramento
__version__ = "1.0.0"

# Configurações padrão
DEFAULT_METRICS_PORT = 8080
DEFAULT_HEALTH_CHECK_INTERVAL = 30
DEFAULT_ALERT_CHECK_INTERVAL = 60
DEFAULT_LOG_LEVEL = "INFO"

# Inicialização automática (se necessário)
def initialize_monitoring(
    metrics_enabled: bool = True,
    log_level: str = DEFAULT_LOG_LEVEL
):
    """
    Inicializa sistema de monitoramento completo
    
    Args:
        metrics_enabled: Habilitar coleta de métricas
        log_level: Nível de log
    """
    import logging
    
    # Setup de logging
    logging.basicConfig(level=getattr(logging, log_level.upper()))
    logger = logging.getLogger(__name__)
    
    logger.info("Inicializando sistema de monitoramento...")
    
    components = []
    
    # Inicializar métricas
    if metrics_enabled:
        metrics = get_metrics_collector()
        metrics.start()
        components.append("metrics")
        logger.info("✅ Sistema de métricas inicializado")
    
    logger.info(f"🎉 Sistema de monitoramento inicializado com componentes: {', '.join(components)}")
    
    return {
        "status": "initialized",
        "components": components,
        "version": __version__
    }

