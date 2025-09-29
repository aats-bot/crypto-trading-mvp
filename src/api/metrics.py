# -*- coding: utf-8 -*-
"""
Crypto Trading MVP - Metrics
Implementa métricas Prometheus para monitoramento
"""

import time
from typing import Dict, Any
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
import psutil

# Métricas HTTP
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

# Métricas de Trading
trading_orders_total = Counter(
    'trading_orders_total',
    'Total trading orders',
    ['symbol', 'side', 'status']
)

trading_pnl_total = Gauge(
    'trading_pnl_total',
    'Total P&L in USD'
)

trading_positions_count = Gauge(
    'trading_positions_count',
    'Number of open positions',
    ['symbol']
)

trading_balance_usd = Gauge(
    'trading_balance_usd',
    'Account balance in USD'
)

# Métricas de Sistema
system_cpu_usage_percent = Gauge(
    'system_cpu_usage_percent',
    'CPU usage percentage'
)

system_memory_usage_percent = Gauge(
    'system_memory_usage_percent',
    'Memory usage percentage'
)

api_health_status = Gauge(
    'api_health_status',
    'API health status (1=healthy, 0=unhealthy)'
)

# Dados simulados para demonstração
DEMO_TRADING_DATA = {
    'pnl_total': 125.50,
    'orders_count': 15,
    'positions_count': 3,
    'balance_usd': 10000.00,
    'win_rate': 0.68
}

class MetricsCollector:
    """Coletor de métricas do sistema"""
    
    def __init__(self):
        self.start_time = time.time()
        self.active_users = set()
    
    def record_http_request(self, method: str, endpoint: str, status: int, duration: float):
        """Registra métricas de requisição HTTP"""
        http_requests_total.labels(method=method, endpoint=endpoint, status=status).inc()
        http_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(duration)
    
    def update_trading_metrics(self):
        """Atualiza métricas de trading com dados simulados"""
        trading_pnl_total.set(DEMO_TRADING_DATA['pnl_total'])
        trading_positions_count.labels(symbol='BTCUSDT').set(DEMO_TRADING_DATA['positions_count'])
        trading_balance_usd.set(DEMO_TRADING_DATA['balance_usd'])
    
    def update_system_metrics(self):
        """Atualiza métricas de sistema"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=0.1)
            system_cpu_usage_percent.set(cpu_percent)
            
            # Memory usage
            memory = psutil.virtual_memory()
            system_memory_usage_percent.set(memory.percent)
            
        except Exception as e:
            print(f"Error updating system metrics: {e}")
    
    def set_api_health(self, healthy: bool):
        """Define status de saúde da API"""
        api_health_status.set(1 if healthy else 0)
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Retorna resumo das métricas"""
        return {
            'uptime_seconds': time.time() - self.start_time,
            'active_users': len(self.active_users),
            'trading_pnl': DEMO_TRADING_DATA['pnl_total'],
            'trading_orders': DEMO_TRADING_DATA['orders_count'],
            'system_cpu': psutil.cpu_percent(),
            'system_memory': psutil.virtual_memory().percent,
            'api_healthy': True
        }

# Instância global do coletor
metrics_collector = MetricsCollector()

def get_prometheus_metrics():
    """Retorna métricas no formato Prometheus"""
    # Atualizar métricas antes de retornar
    metrics_collector.update_system_metrics()
    metrics_collector.update_trading_metrics()
    metrics_collector.set_api_health(True)
    
    return generate_latest()
