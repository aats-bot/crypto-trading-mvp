"""
PPP Vishva Strategy - Windows Compatible Version
Fixed imports for Windows compatibility
"""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import sys
import os

# Add project root to path for Windows compatibility
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import using absolute paths for Windows compatibility
from src.bot.interfaces import (
    TradingStrategy, MarketData, Position, OrderRequest,
    OrderSide, OrderType, Order
)

logger = logging.getLogger(__name__)


class PPPVishvaStrategy(TradingStrategy):
    """
    PPP Vishva Strategy - Windows Compatible
    
    Advanced trading strategy with multiple indicators:
    - UT Bot (ATR-based signals)
    - EMA100 (trend filter)
    - EWO (Elliott Wave Oscillator)
    - Stoch RSI (reversal signals)
    - Heikin Ashi (multi-timeframe analysis)
    """
    
    def __init__(self, 
                 sl_ratio: float = 1.25,
                 pyramid_levels: int = 5,
                 risk_per_trade: float = 0.02):
        """Initialize PPP Vishva strategy"""
        self.sl_ratio = sl_ratio
        self.pyramid_levels = pyramid_levels
        self.risk_per_trade = risk_per_trade
        
        # Strategy parameters
        self.ema_period = 100
        self.atr_period = 14
        self.ut_bot_factor = 3.0
        self.ewo_fast = 5
        self.ewo_slow = 35
        self.stoch_rsi_period = 14
        
        # Data storage
        self.price_history = {}
        self.indicators = {}
        self.last_signals = {}
        
        # Risk parameters
        self.risk_params = {
            "max_position_size": 2000.0,
            "max_daily_loss": 200.0,
            "max_open_positions": self.pyramid_levels,
            "stop_loss_pct": 0.03,
            "take_profit_pct": 0.06,
            "risk_per_trade": self.risk_per_trade,
            "sl_ratio": self.sl_ratio
        }
        
        logger.info(f"Initialized PPP Vishva strategy: SL ratio={sl_ratio}, Pyramid levels={pyramid_levels}")
    
    def calculate_ema(self, prices: List[float], period: int) -> float:
        """Calculate Exponential Moving Average"""
        if len(prices) < period:
            return prices[-1] if prices else 0.0
        
        multiplier = 2 / (period + 1)
        ema = prices[0]
        
        for price in prices[1:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        
        return ema
    
    def calculate_atr(self, highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> float:
        """Calculate Average True Range"""
        if len(closes) < 2:
            return 0.0
        
        true_ranges = []
        for i in range(1, len(closes)):
            high_low = highs[i] - lows[i]
            high_close = abs(highs[i] - closes[i-1])
            low_close = abs(lows[i] - closes[i-1])
            true_range = max(high_low, high_close, low_close)
            true_ranges.append(true_range)
        
        if len(true_ranges) < period:
            return sum(true_ranges) / len(true_ranges) if true_ranges else 0.0
        
        return sum(true_ranges[-period:]) / period
    
    def calculate_ut_bot(self, highs: List[float], lows: List[float], closes: List[float]) -> Dict[str, Any]:
        """Calculate UT Bot signals"""
        if len(closes) < self.atr_period + 1:
            return {"signal": "hold", "level": closes[-1] if closes else 0.0}
        
        atr = self.calculate_atr(highs, lows, closes, self.atr_period)
        current_price = closes[-1]
        
        # Calculate UT Bot levels
        ut_level = atr * self.ut_bot_factor
        
        # Simplified UT Bot logic
        if len(closes) >= 2:
            price_change = current_price - closes[-2]
            if price_change > ut_level:
                return {"signal": "buy", "level": current_price - ut_level}
            elif price_change < -ut_level:
                return {"signal": "sell", "level": current_price + ut_level}
        
        return {"signal": "hold", "level": current_price}
    
    def calculate_ewo(self, closes: List[float]) -> float:
        """Calculate Elliott Wave Oscillator"""
        if len(closes) < self.ewo_slow:
            return 0.0
        
        ema_fast = self.calculate_ema(closes, self.ewo_fast)
        ema_slow = self.calculate_ema(closes, self.ewo_slow)
        
        return ema_fast - ema_slow
    
    def calculate_stoch_rsi(self, closes: List[float]) -> Dict[str, float]:
        """Calculate Stochastic RSI"""
        if len(closes) < self.stoch_rsi_period + 1:
            return {"k": 50.0, "d": 50.0}
        
        # Simplified Stoch RSI calculation
        recent_closes = closes[-self.stoch_rsi_period:]
        min_close = min(recent_closes)
        max_close = max(recent_closes)
        
        if max_close == min_close:
            return {"k": 50.0, "d": 50.0}
        
        k = ((closes[-1] - min_close) / (max_close - min_close)) * 100
        
        # Simple D calculation (3-period SMA of K)
        if len(closes) >= self.stoch_rsi_period + 3:
            k_values = []
            for i in range(3):
                period_closes = closes[-(self.stoch_rsi_period + i + 1):-(i) if i > 0 else None]
                period_min = min(period_closes[-self.stoch_rsi_period:])
                period_max = max(period_closes[-self.stoch_rsi_period:])
                if period_max != period_min:
                    k_val = ((period_closes[-1] - period_min) / (period_max - period_min)) * 100
                    k_values.append(k_val)
            
            d = sum(k_values) / len(k_values) if k_values else k
        else:
            d = k
        
        return {"k": k, "d": d}
    
    async def analyze(self, market_data: MarketData, positions: List[Position]) -> List[OrderRequest]:
        """Analyze market data using PPP Vishva strategy"""
        try:
            symbol = market_data.symbol
            current_price = market_data.price
            
            # Update price history
            if symbol not in self.price_history:
                self.price_history[symbol] = {
                    "closes": [],
                    "highs": [],
                    "lows": [],
                    "timestamps": []
                }
            
            history = self.price_history[symbol]
            history["closes"].append(current_price)
            history["highs"].append(current_price)  # Simplified - using current price
            history["lows"].append(current_price)   # Simplified - using current price
            history["timestamps"].append(datetime.now())
            
            # Keep only last 200 candles
            max_history = 200
            for key in ["closes", "highs", "lows", "timestamps"]:
                if len(history[key]) > max_history:
                    history[key] = history[key][-max_history:]
            
            # Need minimum data for analysis
            if len(history["closes"]) < self.ema_period:
                logger.info(f"Insufficient data for {symbol}: {len(history['closes'])}/{self.ema_period}")
                return []
            
            # Calculate indicators
            ema100 = self.calculate_ema(history["closes"], self.ema_period)
            ut_bot = self.calculate_ut_bot(history["highs"], history["lows"], history["closes"])
            ewo = self.calculate_ewo(history["closes"])
            stoch_rsi = self.calculate_stoch_rsi(history["closes"])
            
            # Store indicators
            self.indicators[symbol] = {
                "ema100": ema100,
                "ut_bot": ut_bot,
                "ewo": ewo,
                "stoch_rsi": stoch_rsi,
                "current_price": current_price
            }
            
            # Trading logic
            orders = []
            
            # Check for existing positions
            existing_positions = [p for p in positions if p.symbol == symbol]
            position_count = len(existing_positions)
            
            # Entry conditions
            if position_count < self.pyramid_levels:
                # Trend filter: price above EMA100 for long
                trend_up = current_price > ema100
                
                # UT Bot signal
                ut_signal = ut_bot["signal"]
                
                # EWO momentum confirmation
                ewo_bullish = ewo > 0
                
                # Stoch RSI oversold for entry
                stoch_oversold = stoch_rsi["k"] < 30 and stoch_rsi["d"] < 30
                
                # Long entry conditions
                if (trend_up and ut_signal == "buy" and ewo_bullish and stoch_oversold):
                    
                    # Calculate position size
                    atr = self.calculate_atr(history["highs"], history["lows"], history["closes"])
                    stop_loss_distance = atr * self.sl_ratio
                    stop_loss_price = current_price - stop_loss_distance
                    
                    # Risk-based position sizing
                    risk_amount = 1000 * self.risk_per_trade  # Assuming $1000 account
                    position_size = risk_amount / stop_loss_distance if stop_loss_distance > 0 else 0.01
                    
                    # Limit position size
                    max_size = self.risk_params["max_position_size"] / current_price
                    position_size = min(position_size, max_size)
                    
                    if position_size > 0.001:  # Minimum position size
                        order = OrderRequest(
                            symbol=symbol,
                            side=OrderSide.BUY,
                            order_type=OrderType.MARKET,
                            quantity=position_size,
                            price=current_price,
                            stop_loss=stop_loss_price,
                            take_profit=current_price + (stop_loss_distance * 2),  # 1:2 RR
                            metadata={
                                "strategy": "ppp_vishva",
                                "entry_reason": "ut_bot_buy_ema_trend_ewo_momentum_stoch_oversold",
                                "pyramid_level": position_count + 1,
                                "indicators": self.indicators[symbol]
                            }
                        )
                        orders.append(order)
                        
                        logger.info(f"PPP Vishva BUY signal for {symbol} at {current_price:.4f}")
            
            # Exit conditions for existing positions
            for position in existing_positions:
                if position.side == "long":
                    # Exit on UT Bot sell signal or trend reversal
                    if ut_bot["signal"] == "sell" or current_price < ema100 * 0.98:
                        order = OrderRequest(
                            symbol=symbol,
                            side=OrderSide.SELL,
                            order_type=OrderType.MARKET,
                            quantity=position.quantity,
                            price=current_price,
                            metadata={
                                "strategy": "ppp_vishva",
                                "exit_reason": "ut_bot_sell_or_trend_reversal",
                                "position_id": position.id if hasattr(position, 'id') else None
                            }
                        )
                        orders.append(order)
                        
                        logger.info(f"PPP Vishva SELL signal for {symbol} at {current_price:.4f}")
            
            return orders
            
        except Exception as e:
            logger.error(f"Error in PPP Vishva analysis for {market_data.symbol}: {e}")
            return []
    
    async def on_order_filled(self, order: Order, position: Position) -> None:
        """Handle order filled event"""
        logger.info(f"PPP Vishva order filled: {order.symbol} {order.side} {order.quantity} at {order.price}")
    
    async def on_position_update(self, position: Position) -> None:
        """Handle position update event"""
        logger.info(f"PPP Vishva position updated: {position.symbol} {position.side} {position.quantity}")
    
    def get_risk_parameters(self) -> Dict[str, Any]:
        """Get risk management parameters"""
        return self.risk_params.copy()
    
    def update_risk_parameters(self, params: Dict[str, Any]) -> None:
        """Update risk management parameters"""
        self.risk_params.update(params)
        logger.info(f"PPP Vishva risk parameters updated: {params}")