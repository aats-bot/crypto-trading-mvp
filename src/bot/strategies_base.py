# 📊 Estratégias Base de Trading - MVP Bot
"""
Estratégias básicas de trading (SMA e RSI)
Localização: /src/bot/strategies_base.py
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
                'price': current_price,
                'timestamp': market_data.timestamp
            })
            
            # Keep only necessary history
            max_history = max(self.slow_period, self.fast_period) + 10
            if len(self.price_history[symbol]) > max_history:
                self.price_history[symbol] = self.price_history[symbol][-max_history:]
            
            # Need enough data for calculation
            if len(self.price_history[symbol]) < self.slow_period:
                logger.debug(f"Not enough data for {symbol}: {len(self.price_history[symbol])}")
                return []
            
            # Calculate moving averages
            prices = [p['price'] for p in self.price_history[symbol]]
            fast_ma = sum(prices[-self.fast_period:]) / self.fast_period
            slow_ma = sum(prices[-self.slow_period:]) / self.slow_period
            
            # Previous MAs for crossover detection
            if len(prices) >= self.slow_period + 1:
                prev_fast_ma = sum(prices[-self.fast_period-1:-1]) / self.fast_period
                prev_slow_ma = sum(prices[-self.slow_period-1:-1]) / self.slow_period
            else:
                prev_fast_ma = fast_ma
                prev_slow_ma = slow_ma
            
            # Detect crossovers
            current_signal = "buy" if fast_ma > slow_ma else "sell"
            prev_signal = "buy" if prev_fast_ma > prev_slow_ma else "sell"
            
            # Check for signal change (crossover)
            if current_signal != prev_signal:
                last_signal = self.last_signals.get(symbol)
                
                # Avoid duplicate signals
                if last_signal != current_signal:
                    self.last_signals[symbol] = current_signal
                    
                    # Check existing positions
                    existing_position = None
                    for pos in positions:
                        if pos.symbol == symbol:
                            existing_position = pos
                            break
                    
                    orders = []
                    
                    if current_signal == "buy" and (not existing_position or existing_position.side == "short"):
                        # Close short position if exists
                        if existing_position and existing_position.side == "short":
                            close_order = OrderRequest(
                                symbol=symbol,
                                side=OrderSide.BUY,
                                order_type=OrderType.MARKET,
                                quantity=abs(existing_position.quantity),
                                price=current_price
                            )
                            orders.append(close_order)
                        
                        # Open long position
                        quantity = self._calculate_position_size(current_price, "buy")
                        if quantity > 0:
                            buy_order = OrderRequest(
                                symbol=symbol,
                                side=OrderSide.BUY,
                                order_type=OrderType.MARKET,
                                quantity=quantity,
                                price=current_price,
                                stop_loss=current_price * (1 - self.stop_loss_pct),
                                take_profit=current_price * (1 + self.risk_params["take_profit_pct"])
                            )
                            orders.append(buy_order)
                    
                    elif current_signal == "sell" and (not existing_position or existing_position.side == "long"):
                        # Close long position if exists
                        if existing_position and existing_position.side == "long":
                            close_order = OrderRequest(
                                symbol=symbol,
                                side=OrderSide.SELL,
                                order_type=OrderType.MARKET,
                                quantity=existing_position.quantity,
                                price=current_price
                            )
                            orders.append(close_order)
                        
                        # Open short position
                        quantity = self._calculate_position_size(current_price, "sell")
                        if quantity > 0:
                            sell_order = OrderRequest(
                                symbol=symbol,
                                side=OrderSide.SELL,
                                order_type=OrderType.MARKET,
                                quantity=quantity,
                                price=current_price,
                                stop_loss=current_price * (1 + self.stop_loss_pct),
                                take_profit=current_price * (1 - self.risk_params["take_profit_pct"])
                            )
                            orders.append(sell_order)
                    
                    if orders:
                        logger.info(f"SMA crossover signal for {symbol}: {current_signal} "
                                  f"(fast_ma={fast_ma:.2f}, slow_ma={slow_ma:.2f})")
                    
                    return orders
            
            return []
            
        except Exception as e:
            logger.error(f"Error in SMA analysis for {market_data.symbol}: {e}")
            return []
    
    def _calculate_position_size(self, price: float, side: str) -> float:
        """Calculate position size based on risk management"""
        try:
            # Simple position sizing based on risk per trade
            risk_amount = self.risk_params["max_position_size"] * self.risk_per_trade
            stop_distance = price * self.stop_loss_pct
            
            if stop_distance > 0:
                quantity = risk_amount / stop_distance
                # Limit to max position size
                max_quantity = self.risk_params["max_position_size"] / price
                return min(quantity, max_quantity)
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Error calculating position size: {e}")
            return 0.0
    
    async def on_order_filled(self, order: Order) -> None:
        """Handle order fill events"""
        logger.info(f"SMA Strategy - Order filled: {order.symbol} {order.side} {order.quantity} @ {order.price}")
    
    async def on_position_update(self, position: Position) -> None:
        """Handle position update events"""
        logger.info(f"SMA Strategy - Position updated: {position.symbol} {position.side} {position.quantity}")
    
    def get_risk_parameters(self) -> Dict[str, Any]:
        """Get current risk parameters"""
        return self.risk_params.copy()
    
    def update_risk_parameters(self, parameters: Dict[str, Any]) -> None:
        """Update risk parameters"""
        for key, value in parameters.items():
            if key in self.risk_params:
                self.risk_params[key] = value
                logger.info(f"SMA Strategy - Updated {key} to {value}")


class RSIStrategy(TradingStrategy):
    """RSI-based trading strategy"""
    
    def __init__(self, period: int = 14, oversold: float = 30, overbought: float = 70,
                 risk_per_trade: float = 0.02, stop_loss_pct: float = 0.02):
        self.period = period
        self.oversold = oversold
        self.overbought = overbought
        self.risk_per_trade = risk_per_trade
        self.stop_loss_pct = stop_loss_pct
        
        # Permite ambos os nomes: rsi_period OU period
        self.period = rsi_period or period
        self.overbought = overbought
        self.oversold = oversold
        # ... resto da inicialização
        
        # Price history for RSI calculation
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
        
        logger.info(f"Initialized RSI strategy: period={period}, oversold={oversold}, overbought={overbought}")
    
    async def analyze(self, market_data: MarketData, positions: List[Position]) -> List[OrderRequest]:
        """Analyze market data using RSI"""
        try:
            symbol = market_data.symbol
            current_price = market_data.price
            
            # Update price history
            if symbol not in self.price_history:
                self.price_history[symbol] = []
            
            self.price_history[symbol].append({
                'price': current_price,
                'timestamp': market_data.timestamp
            })
            
            # Keep only necessary history
            max_history = self.period + 20
            if len(self.price_history[symbol]) > max_history:
                self.price_history[symbol] = self.price_history[symbol][-max_history:]
            
            # Need enough data for RSI calculation
            if len(self.price_history[symbol]) < self.period + 1:
                logger.debug(f"Not enough data for RSI {symbol}: {len(self.price_history[symbol])}")
                return []
            
            # Calculate RSI
            rsi = self._calculate_rsi(symbol)
            if rsi is None:
                return []
            
            # Generate signals based on RSI levels
            signal = None
            if rsi < self.oversold:
                signal = "buy"
            elif rsi > self.overbought:
                signal = "sell"
            
            if signal:
                last_signal = self.last_signals.get(symbol)
                
                # Avoid duplicate signals
                if last_signal != signal:
                    self.last_signals[symbol] = signal
                    
                    # Check existing positions
                    existing_position = None
                    for pos in positions:
                        if pos.symbol == symbol:
                            existing_position = pos
                            break
                    
                    orders = []
                    
                    if signal == "buy" and (not existing_position or existing_position.side == "short"):
                        # Close short position if exists
                        if existing_position and existing_position.side == "short":
                            close_order = OrderRequest(
                                symbol=symbol,
                                side=OrderSide.BUY,
                                order_type=OrderType.MARKET,
                                quantity=abs(existing_position.quantity),
                                price=current_price
                            )
                            orders.append(close_order)
                        
                        # Open long position
                        quantity = self._calculate_position_size(current_price, "buy")
                        if quantity > 0:
                            buy_order = OrderRequest(
                                symbol=symbol,
                                side=OrderSide.BUY,
                                order_type=OrderType.MARKET,
                                quantity=quantity,
                                price=current_price,
                                stop_loss=current_price * (1 - self.stop_loss_pct),
                                take_profit=current_price * (1 + self.risk_params["take_profit_pct"])
                            )
                            orders.append(buy_order)
                    
                    elif signal == "sell" and (not existing_position or existing_position.side == "long"):
                        # Close long position if exists
                        if existing_position and existing_position.side == "long":
                            close_order = OrderRequest(
                                symbol=symbol,
                                side=OrderSide.SELL,
                                order_type=OrderType.MARKET,
                                quantity=existing_position.quantity,
                                price=current_price
                            )
                            orders.append(close_order)
                        
                        # Open short position
                        quantity = self._calculate_position_size(current_price, "sell")
                        if quantity > 0:
                            sell_order = OrderRequest(
                                symbol=symbol,
                                side=OrderSide.SELL,
                                order_type=OrderType.MARKET,
                                quantity=quantity,
                                price=current_price,
                                stop_loss=current_price * (1 + self.stop_loss_pct),
                                take_profit=current_price * (1 - self.risk_params["take_profit_pct"])
                            )
                            orders.append(sell_order)
                    
                    if orders:
                        logger.info(f"RSI signal for {symbol}: {signal} (RSI={rsi:.2f})")
                    
                    return orders
            
            return []
            
        except Exception as e:
            logger.error(f"Error in RSI analysis for {market_data.symbol}: {e}")
            return []
    
    def _calculate_rsi(self, symbol: str) -> Optional[float]:
        """Calculate RSI for the given symbol"""
        try:
            prices = [p['price'] for p in self.price_history[symbol]]
            
            if len(prices) < self.period + 1:
                return None
            
            # Calculate price changes
            deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
            
            # Separate gains and losses
            gains = [max(delta, 0) for delta in deltas]
            losses = [abs(min(delta, 0)) for delta in deltas]
            
            # Calculate average gains and losses
            avg_gain = sum(gains[-self.period:]) / self.period
            avg_loss = sum(losses[-self.period:]) / self.period
            
            if avg_loss == 0:
                return 100.0
            
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            
            return rsi
            
        except Exception as e:
            logger.error(f"Error calculating RSI: {e}")
            return None
    
    def _calculate_position_size(self, price: float, side: str) -> float:
        """Calculate position size based on risk management"""
        try:
            # Simple position sizing based on risk per trade
            risk_amount = self.risk_params["max_position_size"] * self.risk_per_trade
            stop_distance = price * self.stop_loss_pct
            
            if stop_distance > 0:
                quantity = risk_amount / stop_distance
                # Limit to max position size
                max_quantity = self.risk_params["max_position_size"] / price
                return min(quantity, max_quantity)
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Error calculating position size: {e}")
            return 0.0
    
    async def on_order_filled(self, order: Order) -> None:
        """Handle order fill events"""
        logger.info(f"RSI Strategy - Order filled: {order.symbol} {order.side} {order.quantity} @ {order.price}")
    
    async def on_position_update(self, position: Position) -> None:
        """Handle position update events"""
        logger.info(f"RSI Strategy - Position updated: {position.symbol} {position.side} {position.quantity}")
    
    def get_risk_parameters(self) -> Dict[str, Any]:
        """Get current risk parameters"""
        return self.risk_params.copy()
    
    def update_risk_parameters(self, parameters: Dict[str, Any]) -> None:
        """Update risk parameters"""
        for key, value in parameters.items():
            if key in self.risk_params:
                self.risk_params[key] = value
                logger.info(f"RSI Strategy - Updated {key} to {value}")


def get_strategy(strategy_name: str, **kwargs) -> TradingStrategy:
    """Factory function to create strategy instances"""
    strategies = {
        "sma": SimpleMovingAverageStrategy,
        "rsi": RSIStrategy,
    }
    
    # Importar PPP Vishva se disponível
    try:
        from .strategies.ppp_vishva_strategy import PPPVishvaStrategy
        strategies["ppp_vishva"] = PPPVishvaStrategy
    except ImportError:
        logger.warning("PPP Vishva strategy not available")
    
    strategy_class = strategies.get(strategy_name.lower())
    if not strategy_class:
        raise ValueError(f"Unknown strategy: {strategy_name}")
    
    return strategy_class(**kwargs)


# Exportar estratégias
__all__ = [
    'SimpleMovingAverageStrategy',
    'RSIStrategy',
    'get_strategy'
]