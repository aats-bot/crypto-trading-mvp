"""
Trading strategies implementation
"""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from .interfaces import (
    TradingStrategy, MarketData, Position, OrderRequest,
    OrderSide, OrderType, Order
)

logger = logging.getLogger(__name__)


class SimpleMovingAverageStrategy(TradingStrategy):
    """Simple Moving Average crossover strategy"""
    
    def __init__(self, fast_period: int = 10, slow_period: int = 20, 
                 risk_per_trade: float = 0.02, stop_loss_pct: float = 0.02):
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.risk_per_trade = risk_per_trade
        self.stop_loss_pct = stop_loss_pct
        
        # Price history for calculations
        self.price_history = {}
        self.last_signals = {}
        
        # Risk parameters
        self.risk_params = {
            "max_position_size": 1000.0,  # USDT
            "max_daily_loss": 100.0,      # USDT
            "max_open_positions": 3,
            "stop_loss_pct": self.stop_loss_pct,
            "take_profit_pct": 0.04,      # 4% take profit
            "risk_per_trade": self.risk_per_trade
        }
        
        logger.info(f"Initialized SMA strategy: fast={fast_period}, slow={slow_period}")
    
    async def analyze(self, market_data: MarketData, positions: List[Position]) -> List[OrderRequest]:
        """Analyze market data and return trading signals"""
        try:
            symbol = market_data.symbol
            current_price = market_data.price
            
            # Update price history
            if symbol not in self.price_history:
                self.price_history[symbol] = []
            
            self.price_history[symbol].append({
                'timestamp': market_data.timestamp,
                'price': current_price
            })
            
            # Keep only recent data (max 100 points)
            if len(self.price_history[symbol]) > 100:
                self.price_history[symbol] = self.price_history[symbol][-100:]
            
            # Need enough data for calculation
            if len(self.price_history[symbol]) < self.slow_period:
                return []
            
            # Calculate moving averages
            prices = [p['price'] for p in self.price_history[symbol]]
            fast_ma = np.mean(prices[-self.fast_period:])
            slow_ma = np.mean(prices[-self.slow_period:])
            
            # Previous MAs for crossover detection
            if len(prices) >= self.slow_period + 1:
                prev_fast_ma = np.mean(prices[-(self.fast_period + 1):-1])
                prev_slow_ma = np.mean(prices[-(self.slow_period + 1):-1])
            else:
                return []
            
            # Check for existing position
            current_position = None
            for pos in positions:
                if pos.symbol == symbol:
                    current_position = pos
                    break
            
            orders = []
            
            # Bullish crossover (fast MA crosses above slow MA)
            if (fast_ma > slow_ma and prev_fast_ma <= prev_slow_ma and 
                not current_position):
                
                # Calculate position size based on risk
                position_size = self._calculate_position_size(current_price)
                
                if position_size > 0:
                    order = OrderRequest(
                        symbol=symbol,
                        side=OrderSide.BUY,
                        order_type=OrderType.MARKET,
                        quantity=position_size / current_price  # Convert USDT to base asset
                    )
                    orders.append(order)
                    
                    self.last_signals[symbol] = {
                        'type': 'BUY',
                        'timestamp': market_data.timestamp,
                        'price': current_price,
                        'fast_ma': fast_ma,
                        'slow_ma': slow_ma
                    }
                    
                    logger.info(f"BUY signal for {symbol} at {current_price}")
            
            # Bearish crossover (fast MA crosses below slow MA)
            elif (fast_ma < slow_ma and prev_fast_ma >= prev_slow_ma and 
                  current_position and current_position.size > 0):
                
                # Close long position
                order = OrderRequest(
                    symbol=symbol,
                    side=OrderSide.SELL,
                    order_type=OrderType.MARKET,
                    quantity=current_position.size,
                    reduce_only=True
                )
                orders.append(order)
                
                self.last_signals[symbol] = {
                    'type': 'SELL',
                    'timestamp': market_data.timestamp,
                    'price': current_price,
                    'fast_ma': fast_ma,
                    'slow_ma': slow_ma
                }
                
                logger.info(f"SELL signal for {symbol} at {current_price}")
            
            # Check stop loss
            if current_position and current_position.size > 0:
                stop_loss_price = current_position.entry_price * (1 - self.stop_loss_pct)
                if current_price <= stop_loss_price:
                    order = OrderRequest(
                        symbol=symbol,
                        side=OrderSide.SELL,
                        order_type=OrderType.MARKET,
                        quantity=current_position.size,
                        reduce_only=True
                    )
                    orders.append(order)
                    logger.warning(f"Stop loss triggered for {symbol} at {current_price}")
            
            return orders
            
        except Exception as e:
            logger.error(f"Error in strategy analysis: {e}")
            return []
    
    async def on_order_filled(self, order: Order) -> None:
        """Handle order fill events"""
        logger.info(f"Order filled: {order.symbol} {order.side.value} "
                   f"{order.filled_quantity} at {order.avg_price}")
    
    async def on_position_update(self, position: Position) -> None:
        """Handle position update events"""
        logger.info(f"Position update: {position.symbol} {position.side.value} "
                   f"{position.size} at {position.entry_price}, "
                   f"PnL: {position.unrealized_pnl}")
    
    def get_risk_parameters(self) -> Dict[str, Any]:
        """Get current risk parameters"""
        return self.risk_params.copy()
    
    def update_risk_parameters(self, parameters: Dict[str, Any]) -> None:
        """Update risk parameters"""
        self.risk_params.update(parameters)
        logger.info(f"Risk parameters updated: {parameters}")
    
    def _calculate_position_size(self, price: float) -> float:
        """Calculate position size based on risk parameters"""
        max_risk_amount = self.risk_params["max_position_size"] * self.risk_params["risk_per_trade"]
        stop_loss_distance = price * self.risk_params["stop_loss_pct"]
        
        if stop_loss_distance > 0:
            position_size = max_risk_amount / stop_loss_distance * price
            return min(position_size, self.risk_params["max_position_size"])
        
        return 0.0
    
    def get_strategy_info(self) -> Dict[str, Any]:
        """Get strategy information"""
        return {
            "name": "Simple Moving Average",
            "fast_period": self.fast_period,
            "slow_period": self.slow_period,
            "risk_per_trade": self.risk_per_trade,
            "stop_loss_pct": self.stop_loss_pct,
            "last_signals": self.last_signals
        }


class RSIStrategy(TradingStrategy):
    """RSI-based trading strategy"""
    
    def __init__(self, rsi_period: int = 14, oversold: float = 30, 
                 overbought: float = 70, risk_per_trade: float = 0.02):
        self.rsi_period = rsi_period
        self.oversold = oversold
        self.overbought = overbought
        self.risk_per_trade = risk_per_trade
        
        # Price history for RSI calculation
        self.price_history = {}
        self.last_signals = {}
        
        # Risk parameters
        self.risk_params = {
            "max_position_size": 1000.0,
            "max_daily_loss": 100.0,
            "max_open_positions": 3,
            "stop_loss_pct": 0.03,
            "take_profit_pct": 0.06,
            "risk_per_trade": self.risk_per_trade
        }
        
        logger.info(f"Initialized RSI strategy: period={rsi_period}, "
                   f"oversold={oversold}, overbought={overbought}")
    
    async def analyze(self, market_data: MarketData, positions: List[Position]) -> List[OrderRequest]:
        """Analyze market data using RSI"""
        try:
            symbol = market_data.symbol
            current_price = market_data.price
            
            # Update price history
            if symbol not in self.price_history:
                self.price_history[symbol] = []
            
            self.price_history[symbol].append({
                'timestamp': market_data.timestamp,
                'price': current_price
            })
            
            # Keep only recent data
            if len(self.price_history[symbol]) > 100:
                self.price_history[symbol] = self.price_history[symbol][-100:]
            
            # Need enough data for RSI calculation
            if len(self.price_history[symbol]) < self.rsi_period + 1:
                return []
            
            # Calculate RSI
            prices = [p['price'] for p in self.price_history[symbol]]
            rsi = self._calculate_rsi(prices)
            
            if rsi is None:
                return []
            
            # Check for existing position
            current_position = None
            for pos in positions:
                if pos.symbol == symbol:
                    current_position = pos
                    break
            
            orders = []
            
            # RSI oversold - potential buy signal
            if rsi < self.oversold and not current_position:
                position_size = self._calculate_position_size(current_price)
                
                if position_size > 0:
                    order = OrderRequest(
                        symbol=symbol,
                        side=OrderSide.BUY,
                        order_type=OrderType.MARKET,
                        quantity=position_size / current_price
                    )
                    orders.append(order)
                    
                    self.last_signals[symbol] = {
                        'type': 'BUY',
                        'timestamp': market_data.timestamp,
                        'price': current_price,
                        'rsi': rsi
                    }
                    
                    logger.info(f"RSI BUY signal for {symbol} at {current_price}, RSI: {rsi:.2f}")
            
            # RSI overbought - potential sell signal
            elif (rsi > self.overbought and current_position and 
                  current_position.size > 0):
                
                order = OrderRequest(
                    symbol=symbol,
                    side=OrderSide.SELL,
                    order_type=OrderType.MARKET,
                    quantity=current_position.size,
                    reduce_only=True
                )
                orders.append(order)
                
                self.last_signals[symbol] = {
                    'type': 'SELL',
                    'timestamp': market_data.timestamp,
                    'price': current_price,
                    'rsi': rsi
                }
                
                logger.info(f"RSI SELL signal for {symbol} at {current_price}, RSI: {rsi:.2f}")
            
            return orders
            
        except Exception as e:
            logger.error(f"Error in RSI strategy analysis: {e}")
            return []
    
    def _calculate_rsi(self, prices: List[float]) -> Optional[float]:
        """Calculate RSI indicator"""
        try:
            if len(prices) < self.rsi_period + 1:
                return None
            
            # Calculate price changes
            deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
            
            # Separate gains and losses
            gains = [delta if delta > 0 else 0 for delta in deltas]
            losses = [-delta if delta < 0 else 0 for delta in deltas]
            
            # Calculate average gains and losses
            avg_gain = np.mean(gains[-self.rsi_period:])
            avg_loss = np.mean(losses[-self.rsi_period:])
            
            if avg_loss == 0:
                return 100
            
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            
            return rsi
            
        except Exception as e:
            logger.error(f"Error calculating RSI: {e}")
            return None
    
    async def on_order_filled(self, order: Order) -> None:
        """Handle order fill events"""
        logger.info(f"RSI Order filled: {order.symbol} {order.side.value} "
                   f"{order.filled_quantity} at {order.avg_price}")
    
    async def on_position_update(self, position: Position) -> None:
        """Handle position update events"""
        logger.info(f"RSI Position update: {position.symbol} {position.side.value} "
                   f"{position.size} at {position.entry_price}")
    
    def get_risk_parameters(self) -> Dict[str, Any]:
        """Get current risk parameters"""
        return self.risk_params.copy()
    
    def update_risk_parameters(self, parameters: Dict[str, Any]) -> None:
        """Update risk parameters"""
        self.risk_params.update(parameters)
        logger.info(f"RSI Risk parameters updated: {parameters}")
    
    def _calculate_position_size(self, price: float) -> float:
        """Calculate position size based on risk parameters"""
        max_risk_amount = self.risk_params["max_position_size"] * self.risk_params["risk_per_trade"]
        stop_loss_distance = price * self.risk_params["stop_loss_pct"]
        
        if stop_loss_distance > 0:
            position_size = max_risk_amount / stop_loss_distance * price
            return min(position_size, self.risk_params["max_position_size"])
        
        return 0.0
    
    def get_strategy_info(self) -> Dict[str, Any]:
        """Get strategy information"""
        return {
            "name": "RSI Strategy",
            "rsi_period": self.rsi_period,
            "oversold": self.oversold,
            "overbought": self.overbought,
            "risk_per_trade": self.risk_per_trade,
            "last_signals": self.last_signals
        }



# Import PPP Vishva Strategy
try:
    from .ppp_vishva_strategy import PPPVishvaStrategy
    PPP_VISHVA_AVAILABLE = True
except ImportError as e:
    logger.warning(f"PPP Vishva strategy not available: {e}")
    PPP_VISHVA_AVAILABLE = False


def get_strategy(strategy_name: str, config: Dict[str, Any] = None) -> TradingStrategy:
    """Factory function to create strategy instances"""
    strategies = {
        "sma": SimpleMovingAverageStrategy,
        "rsi": RSIStrategy
    }
    
    # Add PPP Vishva if available
    if PPP_VISHVA_AVAILABLE:
        strategies["ppp_vishva"] = PPPVishvaStrategy
    
    if strategy_name not in strategies:
        available = list(strategies.keys())
        raise ValueError(f"Unknown strategy: {strategy_name}. Available: {available}")
    
    # Handle different initialization patterns
    if strategy_name == "ppp_vishva" and PPP_VISHVA_AVAILABLE:
        return PPPVishvaStrategy(config)
    elif strategy_name == "sma":
        # Extract SMA-specific config
        fast_period = config.get('fast_period', 10) if config else 10
        slow_period = config.get('slow_period', 20) if config else 20
        risk_per_trade = config.get('risk_per_trade', 0.02) if config else 0.02
        stop_loss_pct = config.get('stop_loss_pct', 0.02) if config else 0.02
        return SimpleMovingAverageStrategy(fast_period, slow_period, risk_per_trade, stop_loss_pct)
    elif strategy_name == "rsi":
        # Extract RSI-specific config
        rsi_period = config.get('rsi_period', 14) if config else 14
        oversold = config.get('oversold', 30) if config else 30
        overbought = config.get('overbought', 70) if config else 70
        risk_per_trade = config.get('risk_per_trade', 0.02) if config else 0.02
        return RSIStrategy(rsi_period, oversold, overbought, risk_per_trade)
    
    # Fallback
    return strategies[strategy_name]()


def get_available_strategies() -> List[str]:
    """Get list of available strategy names"""
    strategies = ["sma", "rsi"]
    if PPP_VISHVA_AVAILABLE:
        strategies.append("ppp_vishva")
    return strategies


def get_strategy_info(strategy_name: str) -> Dict[str, Any]:
    """Get information about a specific strategy"""
    info = {
        "sma": {
            "name": "Simple Moving Average",
            "description": "Crossover strategy using fast and slow moving averages",
            "parameters": ["fast_period", "slow_period", "risk_per_trade", "stop_loss_pct"]
        },
        "rsi": {
            "name": "RSI Mean Reversion",
            "description": "Mean reversion strategy using RSI overbought/oversold levels",
            "parameters": ["rsi_period", "oversold", "overbought", "risk_per_trade"]
        }
    }
    
    if PPP_VISHVA_AVAILABLE:
        info["ppp_vishva"] = {
            "name": "PPP Vishva Algorithm",
            "description": "Advanced multi-indicator strategy with trend filter, momentum confirmation, and multi-timeframe validation",
            "parameters": ["sl_ratio", "max_pyramid_levels", "risk_per_trade"],
            "indicators": ["EMA100", "UT Bot", "EWO", "Stoch RSI", "Heikin Ashi", "ATR"]
        }
    
    return info.get(strategy_name, {})

