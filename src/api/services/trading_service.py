# 📈 Serviço de Trading - API
"""
Serviço principal para operações de trading
Localização: /src/api/services/trading_service.py
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
import json

from src.models.client import Client, ClientConfiguration, TradingPosition, TradingOrder
from src.models.database import get_db_session
from src.bot.trading_bot import TradingBot
from src.bot.strategies import get_strategy
from src.bot.bybit_provider import BybitMarketDataProvider, BybitOrderExecutor, BybitAccountManager
from src.security.encryption import decrypt_api_credentials
from config.environments import current_config


logger = logging.getLogger(__name__)


class TradingService:
    """Serviço principal para operações de trading"""
    
    def __init__(self):
        self.active_bots = {}  # client_id -> TradingBot instance
        self.bot_status = {}   # client_id -> status info
        self.performance_cache = {}  # client_id -> performance data
        
    async def get_bot_status(self, client_id: int) -> Dict[str, Any]:
        """
        Obtém status atual do bot de trading
        
        Args:
            client_id: ID do cliente
            
        Returns:
            Dict com informações de status
        """
        try:
            bot = self.active_bots.get(client_id)
            
            if not bot:
                return {
                    "bot_status": "stopped",
                    "uptime": 0,
                    "daily_pnl": 0.0,
                    "positions_count": 0,
                    "strategy": None,
                    "symbols": [],
                    "total_trades_today": 0,
                    "account_balance": {},
                    "last_update": datetime.utcnow().isoformat()
                }
            
            # Obter informações do bot
            status_info = {
                "bot_status": bot.status,
                "uptime": bot.get_uptime(),
                "strategy": bot.strategy.__class__.__name__ if bot.strategy else None,
                "symbols": bot.symbols,
                "last_update": datetime.utcnow().isoformat()
            }
            
            # Obter posições abertas
            positions = await self._get_client_positions(client_id)
            status_info["positions_count"] = len(positions)
            
            # Calcular P&L diário
            daily_pnl = await self._calculate_daily_pnl(client_id)
            status_info["daily_pnl"] = daily_pnl
            
            # Contar trades de hoje
            trades_today = await self._count_trades_today(client_id)
            status_info["total_trades_today"] = trades_today
            
            # Obter saldo da conta
            account_balance = await self._get_account_balance(client_id)
            status_info["account_balance"] = account_balance
            
            return status_info
            
        except Exception as e:
            logger.error(f"Erro ao obter status do bot para cliente {client_id}: {str(e)}")
            raise
    
    async def start_bot(self, client_id: int) -> Dict[str, Any]:
        """
        Inicia bot de trading para cliente
        
        Args:
            client_id: ID do cliente
            
        Returns:
            Dict com resultado da operação
        """
        try:
            # Verificar se bot já está ativo
            if client_id in self.active_bots:
                current_status = self.active_bots[client_id].status
                if current_status == "running":
                    return {
                        "success": False,
                        "message": "Bot já está em execução",
                        "status": current_status
                    }
            
            # Obter configuração do cliente
            async with get_db_session() as session:
                client = await session.get(Client, client_id)
                if not client:
                    return {
                        "success": False,
                        "message": "Cliente não encontrado"
                    }
                
                config = await session.get(ClientConfiguration, client_id)
                if not config:
                    return {
                        "success": False,
                        "message": "Configuração de trading não encontrada"
                    }
            
            # Descriptografar credenciais da API
            api_key, api_secret = decrypt_api_credentials(
                client.bybit_api_key_encrypted,
                client.bybit_api_secret_encrypted
            )
            
            # Criar providers
            market_provider = BybitMarketDataProvider(api_key, api_secret)
            order_executor = BybitOrderExecutor(api_key, api_secret)
            account_manager = BybitAccountManager(api_key, api_secret)
            
            # Obter estratégia
            strategy = get_strategy(
                config.strategy,
                config.strategy_parameters or {}
            )
            
            # Criar e configurar bot
            bot = TradingBot(
                client_id=client_id,
                market_data_provider=market_provider,
                order_executor=order_executor,
                account_manager=account_manager,
                strategy=strategy
            )
            
            # Configurar símbolos e parâmetros
            bot.symbols = config.symbols or ["BTCUSDT"]
            bot.risk_per_trade = config.risk_per_trade or 0.01
            
            # Iniciar bot
            await bot.start()
            
            # Armazenar bot ativo
            self.active_bots[client_id] = bot
            self.bot_status[client_id] = {
                "status": "running",
                "started_at": datetime.utcnow(),
                "strategy": config.strategy,
                "symbols": bot.symbols
            }
            
            logger.info(f"Bot iniciado para cliente {client_id}")
            
            return {
                "success": True,
                "message": "Bot iniciado com sucesso",
                "status": "running",
                "strategy": config.strategy,
                "symbols": bot.symbols
            }
            
        except Exception as e:
            logger.error(f"Erro ao iniciar bot para cliente {client_id}: {str(e)}")
            return {
                "success": False,
                "message": f"Erro ao iniciar bot: {str(e)}"
            }
    
    async def stop_bot(self, client_id: int) -> Dict[str, Any]:
        """
        Para bot de trading para cliente
        
        Args:
            client_id: ID do cliente
            
        Returns:
            Dict com resultado da operação
        """
        try:
            bot = self.active_bots.get(client_id)
            
            if not bot:
                return {
                    "success": False,
                    "message": "Bot não está em execução"
                }
            
            # Parar bot
            await bot.stop()
            
            # Remover bot dos ativos
            del self.active_bots[client_id]
            
            # Atualizar status
            if client_id in self.bot_status:
                self.bot_status[client_id]["status"] = "stopped"
                self.bot_status[client_id]["stopped_at"] = datetime.utcnow()
            
            logger.info(f"Bot parado para cliente {client_id}")
            
            return {
                "success": True,
                "message": "Bot parado com sucesso",
                "status": "stopped"
            }
            
        except Exception as e:
            logger.error(f"Erro ao parar bot para cliente {client_id}: {str(e)}")
            return {
                "success": False,
                "message": f"Erro ao parar bot: {str(e)}"
            }
    
    async def pause_bot(self, client_id: int) -> Dict[str, Any]:
        """
        Pausa bot de trading para cliente
        
        Args:
            client_id: ID do cliente
            
        Returns:
            Dict com resultado da operação
        """
        try:
            bot = self.active_bots.get(client_id)
            
            if not bot:
                return {
                    "success": False,
                    "message": "Bot não está em execução"
                }
            
            # Pausar bot
            await bot.pause()
            
            # Atualizar status
            if client_id in self.bot_status:
                self.bot_status[client_id]["status"] = "paused"
                self.bot_status[client_id]["paused_at"] = datetime.utcnow()
            
            logger.info(f"Bot pausado para cliente {client_id}")
            
            return {
                "success": True,
                "message": "Bot pausado com sucesso",
                "status": "paused"
            }
            
        except Exception as e:
            logger.error(f"Erro ao pausar bot para cliente {client_id}: {str(e)}")
            return {
                "success": False,
                "message": f"Erro ao pausar bot: {str(e)}"
            }
    
    async def resume_bot(self, client_id: int) -> Dict[str, Any]:
        """
        Retoma bot de trading pausado
        
        Args:
            client_id: ID do cliente
            
        Returns:
            Dict com resultado da operação
        """
        try:
            bot = self.active_bots.get(client_id)
            
            if not bot:
                return {
                    "success": False,
                    "message": "Bot não está em execução"
                }
            
            if bot.status != "paused":
                return {
                    "success": False,
                    "message": f"Bot não está pausado (status atual: {bot.status})"
                }
            
            # Retomar bot
            await bot.resume()
            
            # Atualizar status
            if client_id in self.bot_status:
                self.bot_status[client_id]["status"] = "running"
                self.bot_status[client_id]["resumed_at"] = datetime.utcnow()
            
            logger.info(f"Bot retomado para cliente {client_id}")
            
            return {
                "success": True,
                "message": "Bot retomado com sucesso",
                "status": "running"
            }
            
        except Exception as e:
            logger.error(f"Erro ao retomar bot para cliente {client_id}: {str(e)}")
            return {
                "success": False,
                "message": f"Erro ao retomar bot: {str(e)}"
            }
    
    async def get_positions(self, client_id: int) -> List[Dict[str, Any]]:
        """
        Obtém posições abertas do cliente
        
        Args:
            client_id: ID do cliente
            
        Returns:
            Lista de posições
        """
        try:
            return await self._get_client_positions(client_id)
            
        except Exception as e:
            logger.error(f"Erro ao obter posições para cliente {client_id}: {str(e)}")
            raise
    
    async def get_orders(
        self,
        client_id: int,
        symbol: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        Obtém histórico de ordens do cliente
        
        Args:
            client_id: ID do cliente
            symbol: Filtrar por símbolo (opcional)
            status: Filtrar por status (opcional)
            limit: Limite de ordens
            
        Returns:
            Dict com ordens e metadados
        """
        try:
            async with get_db_session() as session:
                query = session.query(TradingOrder).filter(
                    TradingOrder.client_id == client_id
                )
                
                if symbol:
                    query = query.filter(TradingOrder.symbol == symbol)
                
                if status:
                    query = query.filter(TradingOrder.status == status)
                
                orders = query.order_by(
                    TradingOrder.created_at.desc()
                ).limit(limit).all()
                
                # Converter para dict
                orders_data = []
                for order in orders:
                    orders_data.append({
                        "id": order.id,
                        "symbol": order.symbol,
                        "side": order.side,
                        "type": order.type,
                        "quantity": float(order.quantity),
                        "filled_price": float(order.filled_price) if order.filled_price else None,
                        "status": order.status,
                        "created_at": order.created_at.isoformat(),
                        "filled_at": order.filled_at.isoformat() if order.filled_at else None,
                        "commission": float(order.commission) if order.commission else 0.0,
                    })
                
                # Contar total de ordens
                total_count = session.query(TradingOrder).filter(
                    TradingOrder.client_id == client_id
                ).count()
                
                return {
                    "orders": orders_data,
                    "total": total_count,
                    "limit": limit,
                    "has_more": len(orders_data) == limit
                }
                
        except Exception as e:
            logger.error(f"Erro ao obter ordens para cliente {client_id}: {str(e)}")
            raise
    
    async def get_performance(
        self,
        client_id: int,
        period: str = "30d"
    ) -> Dict[str, Any]:
        """
        Obtém métricas de performance do cliente
        
        Args:
            client_id: ID do cliente
            period: Período de análise (1d, 7d, 30d, all)
            
        Returns:
            Dict com métricas de performance
        """
        try:
            # Verificar cache
            cache_key = f"{client_id}_{period}"
            if cache_key in self.performance_cache:
                cached_data = self.performance_cache[cache_key]
                if (datetime.utcnow() - cached_data["timestamp"]).seconds < 300:  # 5 min cache
                    return cached_data["data"]
            
            # Calcular período de análise
            end_date = datetime.utcnow()
            if period == "1d":
                start_date = end_date - timedelta(days=1)
            elif period == "7d":
                start_date = end_date - timedelta(days=7)
            elif period == "30d":
                start_date = end_date - timedelta(days=30)
            else:  # all
                start_date = datetime(2020, 1, 1)  # Data muito antiga
            
            # Obter ordens do período
            async with get_db_session() as session:
                orders = session.query(TradingOrder).filter(
                    TradingOrder.client_id == client_id,
                    TradingOrder.status == "filled",
                    TradingOrder.filled_at >= start_date,
                    TradingOrder.filled_at <= end_date
                ).all()
                
                # Calcular métricas
                performance = await self._calculate_performance_metrics(orders)
                
                # Cache resultado
                self.performance_cache[cache_key] = {
                    "data": performance,
                    "timestamp": datetime.utcnow()
                }
                
                return performance
                
        except Exception as e:
            logger.error(f"Erro ao obter performance para cliente {client_id}: {str(e)}")
            raise
    
    async def update_trading_config(
        self,
        client_id: int,
        config_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Atualiza configuração de trading do cliente
        
        Args:
            client_id: ID do cliente
            config_data: Novos dados de configuração
            
        Returns:
            Dict com resultado da operação
        """
        try:
            async with get_db_session() as session:
                config = await session.get(ClientConfiguration, client_id)
                
                if not config:
                    # Criar nova configuração
                    config = ClientConfiguration(client_id=client_id)
                    session.add(config)
                
                # Atualizar campos
                if "strategy" in config_data:
                    config.strategy = config_data["strategy"]
                
                if "symbols" in config_data:
                    config.symbols = config_data["symbols"]
                
                if "risk_per_trade" in config_data:
                    config.risk_per_trade = config_data["risk_per_trade"]
                
                if "strategy_parameters" in config_data:
                    config.strategy_parameters = config_data["strategy_parameters"]
                
                config.updated_at = datetime.utcnow()
                
                await session.commit()
                
                # Se bot está ativo, reiniciar com nova configuração
                if client_id in self.active_bots:
                    await self.stop_bot(client_id)
                    await asyncio.sleep(1)  # Aguardar parada completa
                    await self.start_bot(client_id)
                
                return {
                    "success": True,
                    "message": "Configuração atualizada com sucesso"
                }
                
        except Exception as e:
            logger.error(f"Erro ao atualizar configuração para cliente {client_id}: {str(e)}")
            return {
                "success": False,
                "message": f"Erro ao atualizar configuração: {str(e)}"
            }
    
    # Métodos auxiliares privados
    async def _get_client_positions(self, client_id: int) -> List[Dict[str, Any]]:
        """Obtém posições abertas do cliente"""
        async with get_db_session() as session:
            positions = session.query(TradingPosition).filter(
                TradingPosition.client_id == client_id,
                TradingPosition.status == "open"
            ).all()
            
            positions_data = []
            for position in positions:
                # Calcular P&L não realizado (simulado)
                current_price = await self._get_current_price(position.symbol)
                unrealized_pnl = self._calculate_unrealized_pnl(
                    position, current_price
                )
                
                positions_data.append({
                    "id": position.id,
                    "symbol": position.symbol,
                    "side": position.side,
                    "size": float(position.size),
                    "entry_price": float(position.entry_price),
                    "current_price": current_price,
                    "unrealized_pnl": unrealized_pnl,
                    "unrealized_pnl_pct": (unrealized_pnl / float(position.size * position.entry_price)) * 100,
                    "opened_at": position.opened_at.isoformat()
                })
            
            return positions_data
    
    async def _calculate_daily_pnl(self, client_id: int) -> float:
        """Calcula P&L diário do cliente"""
        today = datetime.utcnow().date()
        
        async with get_db_session() as session:
            orders = session.query(TradingOrder).filter(
                TradingOrder.client_id == client_id,
                TradingOrder.status == "filled",
                TradingOrder.filled_at >= today
            ).all()
            
            total_pnl = 0.0
            for order in orders:
                if order.realized_pnl:
                    total_pnl += float(order.realized_pnl)
            
            return total_pnl
    
    async def _count_trades_today(self, client_id: int) -> int:
        """Conta trades executados hoje"""
        today = datetime.utcnow().date()
        
        async with get_db_session() as session:
            count = session.query(TradingOrder).filter(
                TradingOrder.client_id == client_id,
                TradingOrder.status == "filled",
                TradingOrder.filled_at >= today
            ).count()
            
            return count
    
    async def _get_account_balance(self, client_id: int) -> Dict[str, float]:
        """Obtém saldo da conta do cliente"""
        # Implementação simulada - em produção viria da API da Bybit
        return {
            "USDT": 10000.0,
            "BTC": 0.0,
            "ETH": 0.0
        }
    
    async def _get_current_price(self, symbol: str) -> float:
        """Obtém preço atual do símbolo"""
        # Implementação simulada - em produção viria da API da Bybit
        prices = {
            "BTCUSDT": 50000.0,
            "ETHUSDT": 3000.0,
            "ADAUSDT": 0.5
        }
        return prices.get(symbol, 1.0)
    
    def _calculate_unrealized_pnl(self, position: TradingPosition, current_price: float) -> float:
        """Calcula P&L não realizado de uma posição"""
        entry_price = float(position.entry_price)
        size = float(position.size)
        
        if position.side == "BUY":
            return (current_price - entry_price) * size
        else:  # SELL
            return (entry_price - current_price) * size
    
    async def _calculate_performance_metrics(self, orders: List[TradingOrder]) -> Dict[str, Any]:
        """Calcula métricas de performance baseadas nas ordens"""
        if not orders:
            return {
                "total_pnl": 0.0,
                "total_pnl_pct": 0.0,
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "win_rate": 0.0,
                "best_trade": 0.0,
                "worst_trade": 0.0,
                "average_trade": 0.0,
                "profit_factor": 0.0,
                "max_drawdown": 0.0,
                "max_drawdown_pct": 0.0,
                "sharpe_ratio": 0.0,
                "daily_pnl": []
            }
        
        # Calcular métricas básicas
        total_pnl = sum(float(order.realized_pnl or 0) for order in orders)
        total_trades = len(orders)
        
        pnl_values = [float(order.realized_pnl or 0) for order in orders]
        winning_trades = len([pnl for pnl in pnl_values if pnl > 0])
        losing_trades = len([pnl for pnl in pnl_values if pnl < 0])
        
        win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
        
        best_trade = max(pnl_values) if pnl_values else 0
        worst_trade = min(pnl_values) if pnl_values else 0
        average_trade = total_pnl / total_trades if total_trades > 0 else 0
        
        # Profit factor
        gross_profit = sum(pnl for pnl in pnl_values if pnl > 0)
        gross_loss = abs(sum(pnl for pnl in pnl_values if pnl < 0))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
        
        # P&L diário
        daily_pnl = self._calculate_daily_pnl_series(orders)
        
        # Drawdown e Sharpe ratio (simulados)
        max_drawdown = min(daily_pnl) if daily_pnl else 0
        max_drawdown_pct = (max_drawdown / 10000) * 100 if daily_pnl else 0  # Assumindo capital inicial de $10k
        
        # Sharpe ratio simplificado
        if len(daily_pnl) > 1:
            import numpy as np
            returns = np.diff(daily_pnl)
            sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(252) if np.std(returns) > 0 else 0
        else:
            sharpe_ratio = 0
        
        return {
            "total_pnl": total_pnl,
            "total_pnl_pct": (total_pnl / 10000) * 100,  # Assumindo capital inicial
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "losing_trades": losing_trades,
            "win_rate": win_rate,
            "best_trade": best_trade,
            "worst_trade": worst_trade,
            "average_trade": average_trade,
            "profit_factor": profit_factor,
            "max_drawdown": max_drawdown,
            "max_drawdown_pct": max_drawdown_pct,
            "sharpe_ratio": sharpe_ratio,
            "daily_pnl": [{"date": date, "pnl": pnl} for date, pnl in daily_pnl]
        }
    
    def _calculate_daily_pnl_series(self, orders: List[TradingOrder]) -> List[Tuple[str, float]]:
        """Calcula série temporal de P&L diário"""
        daily_pnl = {}
        
        for order in orders:
            if order.filled_at and order.realized_pnl:
                date_key = order.filled_at.date().isoformat()
                if date_key not in daily_pnl:
                    daily_pnl[date_key] = 0.0
                daily_pnl[date_key] += float(order.realized_pnl)
        
        # Ordenar por data
        sorted_dates = sorted(daily_pnl.keys())
        return [(date, daily_pnl[date]) for date in sorted_dates]


# Instância global do serviço
trading_service = TradingService()


# Exportar serviço principal
__all__ = [
    "TradingService",
    "trading_service",
]

