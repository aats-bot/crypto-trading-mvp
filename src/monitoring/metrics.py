# 📊 Sistema de Métricas - MVP Bot de Trading
"""
Sistema completo de coleta e exposição de métricas
Localização: /src/monitoring/metrics.py
"""
import time
import threading
import psutil
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from prometheus_client import (
    Counter, Histogram, Gauge, Summary, Info,
    CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST,
    start_http_server
)
import logging
from dataclasses import dataclass


logger = logging.getLogger(__name__)


@dataclass
class MetricDefinition:
    """Definição de uma métrica"""
    name: str
    description: str
    metric_type: str
    labels: List[str] = None


class PrometheusMetrics:
    """Coletor de métricas Prometheus"""
    
    def __init__(self, registry: Optional[CollectorRegistry] = None):
        self.registry = registry or CollectorRegistry()
        self._metrics = {}
        self._setup_metrics()
    
    def _setup_metrics(self):
        """Configurar métricas básicas"""
        
        # Métricas HTTP/API
        self.http_requests_total = Counter(
            'http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status'],
            registry=self.registry
        )
        
        self.http_request_duration = Histogram(
            'http_request_duration_seconds',
            'HTTP request duration',
            ['method', 'endpoint'],
            registry=self.registry
        )
        
        # Métricas do Bot
        self.bot_trades_total = Counter(
            'bot_trades_total',
            'Total trades executed',
            ['strategy', 'symbol', 'side'],
            registry=self.registry
        )
        
        self.bot_pnl = Gauge(
            'bot_pnl_total',
            'Total P&L',
            ['strategy', 'symbol'],
            registry=self.registry
        )
        
        self.bot_account_balance = Gauge(
            'bot_account_balance',
            'Account balance',
            ['currency'],
            registry=self.registry
        )
        
        self.bot_positions = Gauge(
            'bot_positions_count',
            'Number of open positions',
            ['strategy', 'symbol'],
            registry=self.registry
        )
        
        self.bot_orders_total = Counter(
            'bot_orders_total',
            'Total orders placed',
            ['strategy', 'symbol', 'side', 'status'],
            registry=self.registry
        )
        
        # Métricas de Performance
        self.bot_win_rate = Gauge(
            'bot_win_rate',
            'Win rate percentage',
            ['strategy'],
            registry=self.registry
        )
        
        self.bot_max_drawdown = Gauge(
            'bot_max_drawdown_percent',
            'Maximum drawdown percentage',
            ['strategy'],
            registry=self.registry
        )
        
        self.bot_sharpe_ratio = Gauge(
            'bot_sharpe_ratio',
            'Sharpe ratio',
            ['strategy'],
            registry=self.registry
        )
        
        # Métricas de Sistema
        self.system_cpu_usage = Gauge(
            'system_cpu_usage_percent',
            'CPU usage percentage',
            registry=self.registry
        )
        
        self.system_memory_usage = Gauge(
            'system_memory_usage_bytes',
            'Memory usage in bytes',
            registry=self.registry
        )
        
        self.system_disk_usage = Gauge(
            'system_disk_usage_percent',
            'Disk usage percentage',
            ['mountpoint'],
            registry=self.registry
        )
        
        # Métricas de Conexão
        self.api_connection_errors = Counter(
            'bot_api_connection_errors_total',
            'API connection errors',
            ['exchange', 'error_type'],
            registry=self.registry
        )
        
        self.api_rate_limit_errors = Counter(
            'bot_api_rate_limit_errors_total',
            'API rate limit errors',
            ['exchange'],
            registry=self.registry
        )
        
        # Métricas de Autenticação
        self.auth_attempts = Counter(
            'auth_attempts_total',
            'Authentication attempts',
            ['status'],
            registry=self.registry
        )
        
        self.auth_failed_logins = Counter(
            'auth_failed_logins_total',
            'Failed login attempts',
            ['reason'],
            registry=self.registry
        )
        
        # Métricas de Aplicação
        self.app_info = Info(
            'app_info',
            'Application information',
            registry=self.registry
        )
        
        self.app_uptime = Gauge(
            'app_uptime_seconds',
            'Application uptime in seconds',
            registry=self.registry
        )
        
        # Definir informações da aplicação
        self.app_info.info({
            'version': '1.0.0',
            'name': 'crypto-trading-mvp',
            'environment': 'development'
        })
    
    def record_http_request(self, method: str, endpoint: str, status: int, duration: float):
        """Registrar requisição HTTP"""
        self.http_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status=str(status)
        ).inc()
        
        self.http_request_duration.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
    
    def record_trade(self, strategy: str, symbol: str, side: str, pnl: float):
        """Registrar trade executado"""
        self.bot_trades_total.labels(
            strategy=strategy,
            symbol=symbol,
            side=side
        ).inc()
        
        # Atualizar P&L
        current_pnl = self.bot_pnl.labels(strategy=strategy, symbol=symbol)._value._value
        self.bot_pnl.labels(strategy=strategy, symbol=symbol).set(current_pnl + pnl)
    
    def update_account_balance(self, currency: str, balance: float):
        """Atualizar saldo da conta"""
        self.bot_account_balance.labels(currency=currency).set(balance)
    
    def update_positions_count(self, strategy: str, symbol: str, count: int):
        """Atualizar número de posições abertas"""
        self.bot_positions.labels(strategy=strategy, symbol=symbol).set(count)
    
    def record_order(self, strategy: str, symbol: str, side: str, status: str):
        """Registrar ordem colocada"""
        self.bot_orders_total.labels(
            strategy=strategy,
            symbol=symbol,
            side=side,
            status=status
        ).inc()
    
    def update_performance_metrics(self, strategy: str, win_rate: float, 
                                 max_drawdown: float, sharpe_ratio: float):
        """Atualizar métricas de performance"""
        self.bot_win_rate.labels(strategy=strategy).set(win_rate)
        self.bot_max_drawdown.labels(strategy=strategy).set(max_drawdown)
        self.bot_sharpe_ratio.labels(strategy=strategy).set(sharpe_ratio)
    
    def record_api_error(self, exchange: str, error_type: str):
        """Registrar erro de API"""
        self.api_connection_errors.labels(
            exchange=exchange,
            error_type=error_type
        ).inc()
    
    def record_rate_limit_error(self, exchange: str):
        """Registrar erro de rate limit"""
        self.api_rate_limit_errors.labels(exchange=exchange).inc()
    
    def record_auth_attempt(self, status: str):
        """Registrar tentativa de autenticação"""
        self.auth_attempts.labels(status=status).inc()
    
    def record_failed_login(self, reason: str):
        """Registrar login falhado"""
        self.auth_failed_logins.labels(reason=reason).inc()
    
    def update_system_metrics(self):
        """Atualizar métricas do sistema"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            self.system_cpu_usage.set(cpu_percent)
            
            # Memória
            memory = psutil.virtual_memory()
            self.system_memory_usage.set(memory.used)
            
            # Disco
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    usage_percent = (usage.used / usage.total) * 100
                    self.system_disk_usage.labels(
                        mountpoint=partition.mountpoint
                    ).set(usage_percent)
                except PermissionError:
                    continue
                    
        except Exception as e:
            logger.error(f"Erro ao atualizar métricas do sistema: {e}")
    
    def get_metrics(self) -> str:
        """Obter métricas no formato Prometheus"""
        return generate_latest(self.registry)


class BusinessMetrics:
    """Métricas específicas de negócio"""
    
    def __init__(self, prometheus_metrics: PrometheusMetrics):
        self.prometheus = prometheus_metrics
        self._trading_stats = {}
        self._performance_cache = {}
        self._last_update = {}
    
    def update_trading_stats(self, strategy: str, stats: Dict[str, Any]):
        """Atualizar estatísticas de trading"""
        self._trading_stats[strategy] = stats
        
        # Atualizar métricas Prometheus
        if 'win_rate' in stats:
            self.prometheus.bot_win_rate.labels(strategy=strategy).set(stats['win_rate'])
        
        if 'max_drawdown' in stats:
            self.prometheus.bot_max_drawdown.labels(strategy=strategy).set(stats['max_drawdown'])
        
        if 'sharpe_ratio' in stats:
            self.prometheus.bot_sharpe_ratio.labels(strategy=strategy).set(stats['sharpe_ratio'])
    
    def calculate_daily_metrics(self, strategy: str, trades: List[Dict[str, Any]]):
        """Calcular métricas diárias"""
        today = datetime.now().date()
        daily_trades = [
            trade for trade in trades
            if datetime.fromisoformat(trade['timestamp']).date() == today
        ]
        
        if not daily_trades:
            return
        
        # P&L diário
        daily_pnl = sum(trade.get('pnl', 0) for trade in daily_trades)
        
        # Número de trades
        trade_count = len(daily_trades)
        
        # Win rate diário
        winning_trades = len([t for t in daily_trades if t.get('pnl', 0) > 0])
        daily_win_rate = (winning_trades / trade_count * 100) if trade_count > 0 else 0
        
        # Atualizar cache
        self._performance_cache[strategy] = {
            'daily_pnl': daily_pnl,
            'daily_trades': trade_count,
            'daily_win_rate': daily_win_rate,
            'last_update': datetime.now()
        }
    
    def get_business_summary(self) -> Dict[str, Any]:
        """Obter resumo das métricas de negócio"""
        return {
            'trading_stats': self._trading_stats,
            'performance_cache': self._performance_cache,
            'last_updates': self._last_update
        }


class SystemMetrics:
    """Métricas do sistema"""
    
    def __init__(self, prometheus_metrics: PrometheusMetrics):
        self.prometheus = prometheus_metrics
        self._start_time = time.time()
        self._update_thread = None
        self._running = False
    
    def start_monitoring(self, interval: int = 30):
        """Iniciar monitoramento contínuo"""
        if self._running:
            return
        
        self._running = True
        self._update_thread = threading.Thread(
            target=self._update_loop,
            args=(interval,),
            daemon=True
        )
        self._update_thread.start()
        logger.info("Monitoramento de sistema iniciado")
    
    def stop_monitoring(self):
        """Parar monitoramento"""
        self._running = False
        if self._update_thread:
            self._update_thread.join()
        logger.info("Monitoramento de sistema parado")
    
    def _update_loop(self, interval: int):
        """Loop de atualização das métricas"""
        while self._running:
            try:
                self.update_all_metrics()
                time.sleep(interval)
            except Exception as e:
                logger.error(f"Erro no loop de métricas: {e}")
                time.sleep(interval)
    
    def update_all_metrics(self):
        """Atualizar todas as métricas do sistema"""
        # Uptime
        uptime = time.time() - self._start_time
        self.prometheus.app_uptime.set(uptime)
        
        # Métricas do sistema
        self.prometheus.update_system_metrics()
    
    def get_system_info(self) -> Dict[str, Any]:
        """Obter informações do sistema"""
        return {
            'uptime': time.time() - self._start_time,
            'cpu_count': psutil.cpu_count(),
            'memory_total': psutil.virtual_memory().total,
            'disk_total': sum(
                psutil.disk_usage(p.mountpoint).total 
                for p in psutil.disk_partitions()
            ),
            'python_version': f"{psutil.version_info}",
            'platform': psutil.platform
        }


class TradingMetrics:
    """Métricas específicas de trading"""
    
    def __init__(self, prometheus_metrics: PrometheusMetrics):
        self.prometheus = prometheus_metrics
        self._trade_history = []
        self._position_history = []
        self._order_history = []
    
    def record_trade_execution(self, trade_data: Dict[str, Any]):
        """Registrar execução de trade"""
        self._trade_history.append({
            **trade_data,
            'timestamp': datetime.now().isoformat()
        })
        
        # Atualizar métricas Prometheus
        self.prometheus.record_trade(
            strategy=trade_data.get('strategy', 'unknown'),
            symbol=trade_data.get('symbol', 'unknown'),
            side=trade_data.get('side', 'unknown'),
            pnl=trade_data.get('pnl', 0)
        )
    
    def record_position_update(self, position_data: Dict[str, Any]):
        """Registrar atualização de posição"""
        self._position_history.append({
            **position_data,
            'timestamp': datetime.now().isoformat()
        })
        
        # Contar posições abertas por estratégia/símbolo
        open_positions = {}
        for pos in self._position_history[-100:]:  # Últimas 100 posições
            if pos.get('status') == 'open':
                key = (pos.get('strategy', 'unknown'), pos.get('symbol', 'unknown'))
                open_positions[key] = open_positions.get(key, 0) + 1
        
        # Atualizar métricas
        for (strategy, symbol), count in open_positions.items():
            self.prometheus.update_positions_count(strategy, symbol, count)
    
    def record_order_placement(self, order_data: Dict[str, Any]):
        """Registrar colocação de ordem"""
        self._order_history.append({
            **order_data,
            'timestamp': datetime.now().isoformat()
        })
        
        # Atualizar métricas Prometheus
        self.prometheus.record_order(
            strategy=order_data.get('strategy', 'unknown'),
            symbol=order_data.get('symbol', 'unknown'),
            side=order_data.get('side', 'unknown'),
            status=order_data.get('status', 'unknown')
        )
    
    def get_trading_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Obter resumo de trading das últimas horas"""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        recent_trades = [
            trade for trade in self._trade_history
            if datetime.fromisoformat(trade['timestamp']) > cutoff
        ]
        
        if not recent_trades:
            return {'trades': 0, 'pnl': 0, 'win_rate': 0}
        
        total_pnl = sum(trade.get('pnl', 0) for trade in recent_trades)
        winning_trades = len([t for t in recent_trades if t.get('pnl', 0) > 0])
        win_rate = (winning_trades / len(recent_trades)) * 100
        
        return {
            'trades': len(recent_trades),
            'pnl': total_pnl,
            'win_rate': win_rate,
            'winning_trades': winning_trades,
            'losing_trades': len(recent_trades) - winning_trades
        }


class MetricsCollector:
    """Coletor principal de métricas"""
    
    def __init__(self, port: int = 8080):
        self.port = port
        self.prometheus = PrometheusMetrics()
        self.business = BusinessMetrics(self.prometheus)
        self.system = SystemMetrics(self.prometheus)
        self.trading = TradingMetrics(self.prometheus)
        self._server_started = False
    
    def start(self):
        """Iniciar coletor de métricas"""
        if not self._server_started:
            try:
                start_http_server(self.port, registry=self.prometheus.registry)
                self._server_started = True
                logger.info(f"Servidor de métricas iniciado na porta {self.port}")
            except Exception as e:
                logger.error(f"Erro ao iniciar servidor de métricas: {e}")
        
        # Iniciar monitoramento do sistema
        self.system.start_monitoring()
    
    def stop(self):
        """Parar coletor de métricas"""
        self.system.stop_monitoring()
        logger.info("Coletor de métricas parado")
    
    def get_all_metrics(self) -> str:
        """Obter todas as métricas"""
        return self.prometheus.get_metrics()
    
    def health_check(self) -> Dict[str, Any]:
        """Verificar saúde do sistema de métricas"""
        return {
            'status': 'healthy' if self._server_started else 'unhealthy',
            'port': self.port,
            'uptime': time.time() - self.system._start_time,
            'metrics_count': len(self.prometheus._metrics)
        }


# Instância global (singleton)
_metrics_collector = None

def get_metrics_collector() -> MetricsCollector:
    """Obter instância global do coletor de métricas"""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector


# Decorador para métricas HTTP
def track_http_requests(func):
    """Decorador para rastrear requisições HTTP"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            status = getattr(result, 'status_code', 200)
        except Exception as e:
            status = 500
            raise
        finally:
            duration = time.time() - start_time
            
            # Extrair informações da requisição (se disponível)
            method = getattr(args[0], 'method', 'GET') if args else 'GET'
            endpoint = getattr(args[0], 'path', '/') if args else '/'
            
            # Registrar métrica
            collector = get_metrics_collector()
            collector.prometheus.record_http_request(method, endpoint, status, duration)
        
        return result
    
    return wrapper


# Exportar principais componentes
__all__ = [
    'MetricsCollector',
    'PrometheusMetrics',
    'BusinessMetrics', 
    'SystemMetrics',
    'TradingMetrics',
    'get_metrics_collector',
    'track_http_requests',
]

