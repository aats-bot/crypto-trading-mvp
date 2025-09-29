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
