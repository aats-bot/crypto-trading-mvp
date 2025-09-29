# 📊 Utilitários de Performance - MVP Bot de Trading
"""
Sistema completo de análise de performance para trading
Localização: /src/utils/performance_utils.py
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
import math


logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Métricas de performance de trading"""
    total_return: float
    annualized_return: float
    volatility: float
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    max_drawdown: float
    max_drawdown_duration: int
    win_rate: float
    profit_factor: float
    avg_win: float
    avg_loss: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    var_95: float
    expected_shortfall: float
    information_ratio: float
    beta: float
    alpha: float


def calculate_returns(prices: List[float]) -> List[float]:
    """
    Calcular retornos percentuais
    
    Args:
        prices: Lista de preços
        
    Returns:
        Lista de retornos percentuais
    """
    if len(prices) < 2:
        return []
    
    returns = []
    for i in range(1, len(prices)):
        if prices[i-1] != 0:
            ret = (prices[i] - prices[i-1]) / prices[i-1]
            returns.append(ret)
        else:
            returns.append(0.0)
    
    return returns


def calculate_sharpe_ratio(returns: List[float], risk_free_rate: float = 0.02) -> float:
    """
    Calcular Sharpe Ratio
    
    Args:
        returns: Lista de retornos
        risk_free_rate: Taxa livre de risco anual
        
    Returns:
        Sharpe ratio
    """
    if not returns or len(returns) < 2:
        return 0.0
    
    returns_array = np.array(returns)
    
    # Converter taxa livre de risco para período dos retornos
    daily_risk_free = risk_free_rate / 252  # Assumindo retornos diários
    
    excess_returns = returns_array - daily_risk_free
    
    if np.std(excess_returns) == 0:
        return 0.0
    
    sharpe = np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)
    return float(sharpe)


def calculate_sortino_ratio(returns: List[float], risk_free_rate: float = 0.02) -> float:
    """
    Calcular Sortino Ratio (considera apenas volatilidade negativa)
    
    Args:
        returns: Lista de retornos
        risk_free_rate: Taxa livre de risco anual
        
    Returns:
        Sortino ratio
    """
    if not returns or len(returns) < 2:
        return 0.0
    
    returns_array = np.array(returns)
    daily_risk_free = risk_free_rate / 252
    
    excess_returns = returns_array - daily_risk_free
    negative_returns = excess_returns[excess_returns < 0]
    
    if len(negative_returns) == 0:
        return float('inf')  # Sem retornos negativos
    
    downside_deviation = np.std(negative_returns)
    
    if downside_deviation == 0:
        return 0.0
    
    sortino = np.mean(excess_returns) / downside_deviation * np.sqrt(252)
    return float(sortino)


def calculate_max_drawdown(equity_curve: List[float]) -> Tuple[float, int]:
    """
    Calcular drawdown máximo e duração
    
    Args:
        equity_curve: Curva de equity
        
    Returns:
        Tuple (max_drawdown_percent, duration_days)
    """
    if not equity_curve or len(equity_curve) < 2:
        return 0.0, 0
    
    equity_array = np.array(equity_curve)
    
    # Calcular running maximum
    running_max = np.maximum.accumulate(equity_array)
    
    # Calcular drawdown
    drawdown = (equity_array - running_max) / running_max
    
    max_drawdown = float(np.min(drawdown))
    
    # Calcular duração do drawdown máximo
    max_dd_idx = np.argmin(drawdown)
    
    # Encontrar início do drawdown
    start_idx = max_dd_idx
    while start_idx > 0 and drawdown[start_idx - 1] < 0:
        start_idx -= 1
    
    # Encontrar fim do drawdown
    end_idx = max_dd_idx
    while end_idx < len(drawdown) - 1 and drawdown[end_idx + 1] < 0:
        end_idx += 1
    
    duration = end_idx - start_idx + 1
    
    return abs(max_drawdown), duration


def calculate_calmar_ratio(returns: List[float], equity_curve: List[float]) -> float:
    """
    Calcular Calmar Ratio (retorno anualizado / max drawdown)
    
    Args:
        returns: Lista de retornos
        equity_curve: Curva de equity
        
    Returns:
        Calmar ratio
    """
    if not returns or not equity_curve:
        return 0.0
    
    annualized_return = calculate_annualized_return(returns)
    max_drawdown, _ = calculate_max_drawdown(equity_curve)
    
    if max_drawdown == 0:
        return float('inf')
    
    return annualized_return / max_drawdown


def calculate_annualized_return(returns: List[float]) -> float:
    """
    Calcular retorno anualizado
    
    Args:
        returns: Lista de retornos
        
    Returns:
        Retorno anualizado
    """
    if not returns:
        return 0.0
    
    returns_array = np.array(returns)
    total_return = np.prod(1 + returns_array) - 1
    
    # Assumindo retornos diários
    periods_per_year = 252
    num_periods = len(returns)
    
    if num_periods == 0:
        return 0.0
    
    annualized = (1 + total_return) ** (periods_per_year / num_periods) - 1
    return float(annualized)


def calculate_volatility(returns: List[float]) -> float:
    """
    Calcular volatilidade anualizada
    
    Args:
        returns: Lista de retornos
        
    Returns:
        Volatilidade anualizada
    """
    if not returns or len(returns) < 2:
        return 0.0
    
    returns_array = np.array(returns)
    daily_vol = np.std(returns_array)
    annualized_vol = daily_vol * np.sqrt(252)
    
    return float(annualized_vol)


def calculate_var(returns: List[float], confidence_level: float = 0.95) -> float:
    """
    Calcular Value at Risk (VaR)
    
    Args:
        returns: Lista de retornos
        confidence_level: Nível de confiança
        
    Returns:
        VaR no nível de confiança especificado
    """
    if not returns:
        return 0.0
    
    returns_array = np.array(returns)
    var = np.percentile(returns_array, (1 - confidence_level) * 100)
    
    return float(abs(var))


def calculate_expected_shortfall(returns: List[float], confidence_level: float = 0.95) -> float:
    """
    Calcular Expected Shortfall (Conditional VaR)
    
    Args:
        returns: Lista de retornos
        confidence_level: Nível de confiança
        
    Returns:
        Expected Shortfall
    """
    if not returns:
        return 0.0
    
    returns_array = np.array(returns)
    var_threshold = np.percentile(returns_array, (1 - confidence_level) * 100)
    
    # Retornos piores que o VaR
    tail_returns = returns_array[returns_array <= var_threshold]
    
    if len(tail_returns) == 0:
        return 0.0
    
    expected_shortfall = np.mean(tail_returns)
    return float(abs(expected_shortfall))


def calculate_win_rate(trades: List[Dict[str, Any]]) -> float:
    """
    Calcular taxa de acerto
    
    Args:
        trades: Lista de trades com campo 'pnl'
        
    Returns:
        Taxa de acerto (0-1)
    """
    if not trades:
        return 0.0
    
    winning_trades = len([t for t in trades if t.get('pnl', 0) > 0])
    total_trades = len(trades)
    
    return winning_trades / total_trades if total_trades > 0 else 0.0


def calculate_profit_factor(trades: List[Dict[str, Any]]) -> float:
    """
    Calcular fator de lucro (lucro bruto / prejuízo bruto)
    
    Args:
        trades: Lista de trades com campo 'pnl'
        
    Returns:
        Fator de lucro
    """
    if not trades:
        return 0.0
    
    gross_profit = sum(t.get('pnl', 0) for t in trades if t.get('pnl', 0) > 0)
    gross_loss = abs(sum(t.get('pnl', 0) for t in trades if t.get('pnl', 0) < 0))
    
    if gross_loss == 0:
        return float('inf') if gross_profit > 0 else 0.0
    
    return gross_profit / gross_loss


def calculate_average_win_loss(trades: List[Dict[str, Any]]) -> Tuple[float, float]:
    """
    Calcular ganho médio e perda média
    
    Args:
        trades: Lista de trades com campo 'pnl'
        
    Returns:
        Tuple (avg_win, avg_loss)
    """
    if not trades:
        return 0.0, 0.0
    
    winning_trades = [t.get('pnl', 0) for t in trades if t.get('pnl', 0) > 0]
    losing_trades = [t.get('pnl', 0) for t in trades if t.get('pnl', 0) < 0]
    
    avg_win = np.mean(winning_trades) if winning_trades else 0.0
    avg_loss = abs(np.mean(losing_trades)) if losing_trades else 0.0
    
    return float(avg_win), float(avg_loss)


def calculate_information_ratio(returns: List[float], benchmark_returns: List[float]) -> float:
    """
    Calcular Information Ratio vs benchmark
    
    Args:
        returns: Retornos da estratégia
        benchmark_returns: Retornos do benchmark
        
    Returns:
        Information ratio
    """
    if not returns or not benchmark_returns or len(returns) != len(benchmark_returns):
        return 0.0
    
    returns_array = np.array(returns)
    benchmark_array = np.array(benchmark_returns)
    
    excess_returns = returns_array - benchmark_array
    tracking_error = np.std(excess_returns)
    
    if tracking_error == 0:
        return 0.0
    
    information_ratio = np.mean(excess_returns) / tracking_error * np.sqrt(252)
    return float(information_ratio)


def calculate_beta_alpha(returns: List[float], benchmark_returns: List[float], 
                        risk_free_rate: float = 0.02) -> Tuple[float, float]:
    """
    Calcular Beta e Alpha vs benchmark
    
    Args:
        returns: Retornos da estratégia
        benchmark_returns: Retornos do benchmark
        risk_free_rate: Taxa livre de risco
        
    Returns:
        Tuple (beta, alpha)
    """
    if not returns or not benchmark_returns or len(returns) != len(benchmark_returns):
        return 0.0, 0.0
    
    returns_array = np.array(returns)
    benchmark_array = np.array(benchmark_returns)
    
    daily_risk_free = risk_free_rate / 252
    
    excess_returns = returns_array - daily_risk_free
    excess_benchmark = benchmark_array - daily_risk_free
    
    # Calcular beta
    covariance = np.cov(excess_returns, excess_benchmark)[0, 1]
    benchmark_variance = np.var(excess_benchmark)
    
    if benchmark_variance == 0:
        beta = 0.0
    else:
        beta = covariance / benchmark_variance
    
    # Calcular alpha
    alpha = np.mean(excess_returns) - beta * np.mean(excess_benchmark)
    alpha_annualized = alpha * 252  # Anualizar
    
    return float(beta), float(alpha_annualized)


def generate_performance_report(trades: List[Dict[str, Any]], 
                              equity_curve: List[float],
                              benchmark_returns: Optional[List[float]] = None,
                              risk_free_rate: float = 0.02) -> PerformanceMetrics:
    """
    Gerar relatório completo de performance
    
    Args:
        trades: Lista de trades
        equity_curve: Curva de equity
        benchmark_returns: Retornos do benchmark (opcional)
        risk_free_rate: Taxa livre de risco
        
    Returns:
        Objeto PerformanceMetrics com todas as métricas
    """
    try:
        # Calcular retornos da equity curve
        returns = calculate_returns(equity_curve)
        
        # Métricas básicas
        total_return = (equity_curve[-1] / equity_curve[0] - 1) if len(equity_curve) >= 2 else 0.0
        annualized_return = calculate_annualized_return(returns)
        volatility = calculate_volatility(returns)
        
        # Ratios de risco-retorno
        sharpe_ratio = calculate_sharpe_ratio(returns, risk_free_rate)
        sortino_ratio = calculate_sortino_ratio(returns, risk_free_rate)
        calmar_ratio = calculate_calmar_ratio(returns, equity_curve)
        
        # Drawdown
        max_drawdown, max_drawdown_duration = calculate_max_drawdown(equity_curve)
        
        # Métricas de trading
        win_rate = calculate_win_rate(trades)
        profit_factor = calculate_profit_factor(trades)
        avg_win, avg_loss = calculate_average_win_loss(trades)
        
        # Contadores
        total_trades = len(trades)
        winning_trades = len([t for t in trades if t.get('pnl', 0) > 0])
        losing_trades = total_trades - winning_trades
        
        # Métricas de risco
        var_95 = calculate_var(returns, 0.95)
        expected_shortfall = calculate_expected_shortfall(returns, 0.95)
        
        # Métricas vs benchmark
        information_ratio = 0.0
        beta = 0.0
        alpha = 0.0
        
        if benchmark_returns and len(benchmark_returns) == len(returns):
            information_ratio = calculate_information_ratio(returns, benchmark_returns)
            beta, alpha = calculate_beta_alpha(returns, benchmark_returns, risk_free_rate)
        
        return PerformanceMetrics(
            total_return=total_return,
            annualized_return=annualized_return,
            volatility=volatility,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            calmar_ratio=calmar_ratio,
            max_drawdown=max_drawdown,
            max_drawdown_duration=max_drawdown_duration,
            win_rate=win_rate,
            profit_factor=profit_factor,
            avg_win=avg_win,
            avg_loss=avg_loss,
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            var_95=var_95,
            expected_shortfall=expected_shortfall,
            information_ratio=information_ratio,
            beta=beta,
            alpha=alpha
        )
        
    except Exception as e:
        logger.error(f"Erro ao gerar relatório de performance: {e}")
        
        # Retornar métricas zeradas em caso de erro
        return PerformanceMetrics(
            total_return=0.0, annualized_return=0.0, volatility=0.0,
            sharpe_ratio=0.0, sortino_ratio=0.0, calmar_ratio=0.0,
            max_drawdown=0.0, max_drawdown_duration=0,
            win_rate=0.0, profit_factor=0.0, avg_win=0.0, avg_loss=0.0,
            total_trades=0, winning_trades=0, losing_trades=0,
            var_95=0.0, expected_shortfall=0.0, information_ratio=0.0,
            beta=0.0, alpha=0.0
        )


def format_performance_summary(metrics: PerformanceMetrics) -> Dict[str, str]:
    """
    Formatar resumo de performance para exibição
    
    Args:
        metrics: Objeto PerformanceMetrics
        
    Returns:
        Dict com métricas formatadas
    """
    return {
        'Total Return': f"{metrics.total_return:.2%}",
        'Annualized Return': f"{metrics.annualized_return:.2%}",
        'Volatility': f"{metrics.volatility:.2%}",
        'Sharpe Ratio': f"{metrics.sharpe_ratio:.2f}",
        'Sortino Ratio': f"{metrics.sortino_ratio:.2f}",
        'Calmar Ratio': f"{metrics.calmar_ratio:.2f}",
        'Max Drawdown': f"{metrics.max_drawdown:.2%}",
        'Max DD Duration': f"{metrics.max_drawdown_duration} days",
        'Win Rate': f"{metrics.win_rate:.2%}",
        'Profit Factor': f"{metrics.profit_factor:.2f}",
        'Avg Win': f"${metrics.avg_win:.2f}",
        'Avg Loss': f"${metrics.avg_loss:.2f}",
        'Total Trades': f"{metrics.total_trades}",
        'Winning Trades': f"{metrics.winning_trades}",
        'Losing Trades': f"{metrics.losing_trades}",
        'VaR (95%)': f"{metrics.var_95:.2%}",
        'Expected Shortfall': f"{metrics.expected_shortfall:.2%}",
        'Information Ratio': f"{metrics.information_ratio:.2f}",
        'Beta': f"{metrics.beta:.2f}",
        'Alpha': f"{metrics.alpha:.2%}"
    }


def calculate_rolling_metrics(equity_curve: List[float], window: int = 30) -> Dict[str, List[float]]:
    """
    Calcular métricas móveis
    
    Args:
        equity_curve: Curva de equity
        window: Janela para cálculo móvel
        
    Returns:
        Dict com métricas móveis
    """
    if len(equity_curve) < window:
        return {}
    
    rolling_returns = []
    rolling_volatility = []
    rolling_sharpe = []
    rolling_drawdown = []
    
    for i in range(window, len(equity_curve)):
        window_data = equity_curve[i-window:i]
        window_returns = calculate_returns(window_data)
        
        # Retorno da janela
        window_return = (window_data[-1] / window_data[0] - 1) if len(window_data) >= 2 else 0.0
        rolling_returns.append(window_return)
        
        # Volatilidade da janela
        window_vol = calculate_volatility(window_returns)
        rolling_volatility.append(window_vol)
        
        # Sharpe da janela
        window_sharpe = calculate_sharpe_ratio(window_returns)
        rolling_sharpe.append(window_sharpe)
        
        # Drawdown atual
        window_dd, _ = calculate_max_drawdown(window_data)
        rolling_drawdown.append(window_dd)
    
    return {
        'rolling_returns': rolling_returns,
        'rolling_volatility': rolling_volatility,
        'rolling_sharpe': rolling_sharpe,
        'rolling_drawdown': rolling_drawdown
    }


# Exportar funções principais
__all__ = [
    'PerformanceMetrics',
    'calculate_returns',
    'calculate_sharpe_ratio',
    'calculate_sortino_ratio',
    'calculate_max_drawdown',
    'calculate_calmar_ratio',
    'calculate_annualized_return',
    'calculate_volatility',
    'calculate_var',
    'calculate_expected_shortfall',
    'calculate_win_rate',
    'calculate_profit_factor',
    'calculate_average_win_loss',
    'calculate_information_ratio',
    'calculate_beta_alpha',
    'generate_performance_report',
    'format_performance_summary',
    'calculate_rolling_metrics',
]

