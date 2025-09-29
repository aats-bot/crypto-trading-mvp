"""
Main trading bot implementation
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json

from .interfaces import (
    MarketDataProvider, OrderExecutor, AccountManager,
    TradingStrategy, RiskManager, MarketData, Position, Order
)
from .bybit_provider import BybitMarketDataProvider, BybitOrderExecutor, BybitAccountManager
from .strategies_base import SimpleMovingAverageStrategy, RSIStrategy
from .risk_manager import BasicRiskManager

logger = logging.getLogger(__name__)


class TradingBot:
    """Main trading bot class"""
    
    def __init__(self, client_id: str, config: Dict[str, Any]):
        """Initialize trading bot for a specific client"""
        self.client_id = client_id
        self.config = config
        self.is_running = False
        self.is_paused = False
        
        # Initialize components
        self._init_components()
        
        # Bot state
        self.last_update = None
        self.error_count = 0
        self.max_errors = 10
        
        # Performance tracking
        self.stats = {
            "start_time": None,
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "total_pnl": 0.0,
            "max_drawdown": 0.0,
            "last_trade_time": None
        }
        
        logger.info(f"Trading bot initialized for client {client_id}")
    
    def _init_components(self):
        """Initialize bot components"""
        try:
            # Extract configuration
            api_key = self.config.get("api_key")
            api_secret = self.config.get("api_secret")
            testnet = self.config.get("testnet", True)
            strategy_type = self.config.get("strategy", "sma")
            
            if not api_key or not api_secret:
                raise ValueError("API key and secret are required")
            
            # Initialize providers
            self.market_data = BybitMarketDataProvider(api_key, api_secret, testnet)
            self.order_executor = BybitOrderExecutor(api_key, api_secret, testnet)
            self.account_manager = BybitAccountManager(api_key, api_secret, testnet)
            
            # Initialize strategy
            if strategy_type == "sma":
                self.strategy = SimpleMovingAverageStrategy(
                    fast_period=self.config.get("fast_period", 10),
                    slow_period=self.config.get("slow_period", 20),
                    risk_per_trade=self.config.get("risk_per_trade", 0.02)
                )
            elif strategy_type == "rsi":
                self.strategy = RSIStrategy(
                    rsi_period=self.config.get("rsi_period", 14),
                    oversold=self.config.get("oversold", 30),
                    overbought=self.config.get("overbought", 70),
                    risk_per_trade=self.config.get("risk_per_trade", 0.02)
                )
            else:
                raise ValueError(f"Unknown strategy type: {strategy_type}")
            
            # Initialize risk manager
            risk_config = self.config.get("risk_management", {})
            self.risk_manager = BasicRiskManager(risk_config)
            
            # Trading symbols
            self.symbols = self.config.get("symbols", ["BTCUSDT"])
            
            logger.info(f"Components initialized for client {self.client_id}")
            
        except Exception as e:
            logger.error(f"Error initializing components: {e}")
            raise
    
    async def start(self):
        """Start the trading bot"""
        if self.is_running:
            logger.warning(f"Bot {self.client_id} is already running")
            return
        
        try:
            self.is_running = True
            self.is_paused = False
            self.stats["start_time"] = datetime.now()
            self.error_count = 0
            
            logger.info(f"Starting trading bot for client {self.client_id}")
            
            # Start main trading loop
            await self._trading_loop()
            
        except Exception as e:
            logger.error(f"Error starting bot {self.client_id}: {e}")
            self.is_running = False
            raise
    
    async def stop(self):
        """Stop the trading bot"""
        logger.info(f"Stopping trading bot for client {self.client_id}")
        self.is_running = False
        self.is_paused = False
    
    async def pause(self):
        """Pause the trading bot"""
        logger.info(f"Pausing trading bot for client {self.client_id}")
        self.is_paused = True
    
    async def resume(self):
        """Resume the trading bot"""
        logger.info(f"Resuming trading bot for client {self.client_id}")
        self.is_paused = False
    
    async def _trading_loop(self):
        """Main trading loop"""
        while self.is_running:
            try:
                if self.is_paused:
                    await asyncio.sleep(5)
                    continue
                
                # Update market data and analyze
                await self._update_and_analyze()
                
                # Check positions and risk
                await self._check_positions_and_risk()
                
                # Update statistics
                await self._update_statistics()
                
                self.last_update = datetime.now()
                self.error_count = 0  # Reset error count on successful iteration
                
                # Wait before next iteration
                await asyncio.sleep(self.config.get("update_interval", 30))
                
            except Exception as e:
                self.error_count += 1
                logger.error(f"Error in trading loop for {self.client_id}: {e}")
                
                if self.error_count >= self.max_errors:
                    logger.critical(f"Too many errors for {self.client_id}, stopping bot")
                    self.is_running = False
                    break
                
                # Wait before retrying
                await asyncio.sleep(10)
    
    async def _update_and_analyze(self):
        """Update market data and run strategy analysis"""
        try:
            for symbol in self.symbols:
                # Get current market data
                market_data = await self.market_data.get_ticker(symbol)
                
                # Get current positions
                positions = await self.account_manager.get_positions(symbol)
                
                # Run strategy analysis
                signals = await self.strategy.analyze(market_data, positions)
                
                # Process signals
                for signal in signals:
                    await self._process_signal(signal)
                    
        except Exception as e:
            logger.error(f"Error updating and analyzing for {self.client_id}: {e}")
            raise
    
    async def _process_signal(self, order_request):
        """Process trading signal"""
        try:
            # Get account balance and positions for risk validation
            balance = await self.account_manager.get_balance()
            positions = await self.account_manager.get_positions()
            
            # Validate order with risk manager
            is_valid = await self.risk_manager.validate_order(
                order_request, balance, positions
            )
            
            if not is_valid:
                logger.warning(f"Order rejected by risk manager: {order_request.symbol}")
                return
            
            # Execute order
            order = await self.order_executor.place_order(order_request)
            
            if order:
                logger.info(f"Order placed for {self.client_id}: "
                           f"{order.symbol} {order.side.value} {order.quantity}")
                
                # Notify strategy about order
                await self.strategy.on_order_filled(order)
                
                # Update statistics
                self.stats["total_trades"] += 1
                self.stats["last_trade_time"] = datetime.now()
                
        except Exception as e:
            logger.error(f"Error processing signal for {self.client_id}: {e}")
    
    async def _check_positions_and_risk(self):
        """Check positions and risk limits"""
        try:
            # Get current positions
            positions = await self.account_manager.get_positions()
            
            # Check position limits
            warnings = await self.risk_manager.check_position_limits(positions)
            
            if warnings:
                for warning in warnings:
                    logger.warning(f"Risk warning for {self.client_id}: {warning}")
            
            # Update strategy with position updates
            for position in positions:
                await self.strategy.on_position_update(position)
                
        except Exception as e:
            logger.error(f"Error checking positions for {self.client_id}: {e}")
    
    async def _update_statistics(self):
        """Update bot statistics"""
        try:
            # Get current positions for PnL calculation
            positions = await self.account_manager.get_positions()
            
            # Calculate total unrealized PnL
            total_unrealized_pnl = sum(pos.unrealized_pnl for pos in positions)
            
            # Update max drawdown
            if total_unrealized_pnl < self.stats["max_drawdown"]:
                self.stats["max_drawdown"] = total_unrealized_pnl
            
            # Update risk manager daily stats
            self.risk_manager.update_daily_stats(total_unrealized_pnl)
            
        except Exception as e:
            logger.error(f"Error updating statistics for {self.client_id}: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get bot status"""
        return {
            "client_id": self.client_id,
            "is_running": self.is_running,
            "is_paused": self.is_paused,
            "last_update": self.last_update.isoformat() if self.last_update else None,
            "error_count": self.error_count,
            "stats": self.stats.copy(),
            "strategy_info": self.strategy.get_strategy_info() if hasattr(self.strategy, 'get_strategy_info') else {},
            "risk_metrics": self.risk_manager.get_risk_metrics()
        }
    
    def update_config(self, new_config: Dict[str, Any]):
        """Update bot configuration"""
        try:
            # Update strategy parameters if provided
            if "strategy_params" in new_config:
                self.strategy.update_risk_parameters(new_config["strategy_params"])
            
            # Update risk management parameters
            if "risk_management" in new_config:
                self.risk_manager.config.update(new_config["risk_management"])
            
            # Update other config
            self.config.update(new_config)
            
            logger.info(f"Configuration updated for client {self.client_id}")
            
        except Exception as e:
            logger.error(f"Error updating config for {self.client_id}: {e}")
            raise
    
    async def get_performance_report(self) -> Dict[str, Any]:
        """Generate performance report"""
        try:
            # Get current positions and balance
            positions = await self.account_manager.get_positions()
            balance = await self.account_manager.get_balance()
            
            # Calculate metrics
            total_balance = sum(b.total for b in balance if b.asset in ["USDT", "USD"])
            total_unrealized_pnl = sum(pos.unrealized_pnl for pos in positions)
            
            win_rate = 0
            if self.stats["total_trades"] > 0:
                win_rate = self.stats["winning_trades"] / self.stats["total_trades"] * 100
            
            return {
                "client_id": self.client_id,
                "total_balance": total_balance,
                "total_unrealized_pnl": total_unrealized_pnl,
                "total_trades": self.stats["total_trades"],
                "win_rate": win_rate,
                "max_drawdown": self.stats["max_drawdown"],
                "positions": len(positions),
                "strategy": self.strategy.get_strategy_info() if hasattr(self.strategy, 'get_strategy_info') else {},
                "risk_level": self.risk_manager.get_risk_metrics()["risk_level"],
                "uptime": (datetime.now() - self.stats["start_time"]).total_seconds() if self.stats["start_time"] else 0
            }
            
        except Exception as e:
            logger.error(f"Error generating performance report for {self.client_id}: {e}")
            return {"error": str(e)}