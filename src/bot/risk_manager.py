"""
Risk management implementation
"""
import logging
from typing import Dict, List, Any
from datetime import datetime, timedelta

from .interfaces import (
    RiskManager, OrderRequest, Balance, Position,
    OrderSide, PositionSide
)

logger = logging.getLogger(__name__)


class BasicRiskManager(RiskManager):
    """Basic risk management implementation"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize risk manager with configuration"""
        default_config = {
            "max_position_size_usd": 1000.0,      # Maximum position size in USD
            "max_total_exposure_usd": 5000.0,     # Maximum total exposure
            "max_leverage": 3.0,                  # Maximum leverage
            "max_daily_loss_usd": 200.0,          # Maximum daily loss
            "max_drawdown_pct": 0.10,             # Maximum drawdown percentage
            "min_account_balance_usd": 100.0,     # Minimum account balance
            "position_size_pct": 0.02,            # Position size as % of account
            "max_open_positions": 5,              # Maximum number of open positions
            "risk_per_trade_pct": 0.02,           # Risk per trade as % of account
            "stop_loss_pct": 0.03,                # Default stop loss percentage
            "correlation_limit": 0.7,             # Maximum correlation between positions
            "blacklisted_symbols": [],            # Symbols not allowed for trading
            "trading_hours": {                    # Allowed trading hours (UTC)
                "start": 0,
                "end": 24
            }
        }
        
        self.config = default_config
        if config:
            self.config.update(config)
        
        # Track daily statistics
        self.daily_stats = {
            "date": datetime.now().date(),
            "total_pnl": 0.0,
            "trades_count": 0,
            "max_drawdown": 0.0
        }
        
        logger.info("Risk manager initialized with config: %s", self.config)
    
    async def validate_order(self, order_request: OrderRequest, 
                           account_balance: List[Balance], 
                           positions: List[Position]) -> bool:
        """Validate order against risk parameters"""
        try:
            # Check if symbol is blacklisted
            if order_request.symbol in self.config["blacklisted_symbols"]:
                logger.warning(f"Order rejected: {order_request.symbol} is blacklisted")
                return False
            
            # Check trading hours
            if not self._is_trading_hours():
                logger.warning("Order rejected: Outside trading hours")
                return False
            
            # Check minimum account balance
            total_balance = self._get_total_balance_usd(account_balance)
            if total_balance < self.config["min_account_balance_usd"]:
                logger.warning(f"Order rejected: Account balance too low: ${total_balance}")
                return False
            
            # Check maximum number of open positions
            if len(positions) >= self.config["max_open_positions"]:
                # Allow closing orders
                if not order_request.reduce_only:
                    logger.warning(f"Order rejected: Too many open positions: {len(positions)}")
                    return False
            
            # Check position size limits
            if not await self._validate_position_size(order_request, total_balance):
                return False
            
            # Check total exposure
            if not await self._validate_total_exposure(order_request, positions):
                return False
            
            # Check daily loss limits
            if not await self._validate_daily_limits():
                return False
            
            # Check leverage limits
            if not await self._validate_leverage(order_request, account_balance, positions):
                return False
            
            logger.info(f"Order validation passed for {order_request.symbol}")
            return True
            
        except Exception as e:
            logger.error(f"Error validating order: {e}")
            return False
    
    async def check_position_limits(self, positions: List[Position]) -> List[str]:
        """Check if positions exceed limits"""
        warnings = []
        
        try:
            # Check individual position sizes
            for position in positions:
                position_value = position.size * position.mark_price
                if position_value > self.config["max_position_size_usd"]:
                    warnings.append(
                        f"Position {position.symbol} exceeds size limit: "
                        f"${position_value:.2f} > ${self.config['max_position_size_usd']}"
                    )
            
            # Check total exposure
            total_exposure = sum(pos.size * pos.mark_price for pos in positions)
            if total_exposure > self.config["max_total_exposure_usd"]:
                warnings.append(
                    f"Total exposure exceeds limit: "
                    f"${total_exposure:.2f} > ${self.config['max_total_exposure_usd']}"
                )
            
            # Check unrealized PnL
            total_unrealized_pnl = sum(pos.unrealized_pnl for pos in positions)
            if total_unrealized_pnl < -self.config["max_daily_loss_usd"]:
                warnings.append(
                    f"Unrealized loss exceeds daily limit: "
                    f"${total_unrealized_pnl:.2f} < -${self.config['max_daily_loss_usd']}"
                )
            
            return warnings
            
        except Exception as e:
            logger.error(f"Error checking position limits: {e}")
            return [f"Error checking limits: {e}"]
    
    async def calculate_position_size(self, symbol: str, entry_price: float, 
                                    stop_loss: float, risk_amount: float) -> float:
        """Calculate appropriate position size based on risk"""
        try:
            if stop_loss <= 0 or entry_price <= 0:
                return 0.0
            
            # Calculate risk per unit
            risk_per_unit = abs(entry_price - stop_loss)
            
            if risk_per_unit <= 0:
                return 0.0
            
            # Calculate position size based on risk
            position_size_units = risk_amount / risk_per_unit
            position_value = position_size_units * entry_price
            
            # Apply maximum position size limit
            max_position_value = self.config["max_position_size_usd"]
            if position_value > max_position_value:
                position_size_units = max_position_value / entry_price
            
            logger.info(f"Calculated position size for {symbol}: {position_size_units:.6f} units")
            return position_size_units
            
        except Exception as e:
            logger.error(f"Error calculating position size: {e}")
            return 0.0
    
    def get_max_position_size(self, symbol: str) -> float:
        """Get maximum allowed position size for symbol"""
        return self.config["max_position_size_usd"]
    
    def update_daily_stats(self, pnl: float, trade_count: int = 0):
        """Update daily statistics"""
        current_date = datetime.now().date()
        
        # Reset stats if new day
        if self.daily_stats["date"] != current_date:
            self.daily_stats = {
                "date": current_date,
                "total_pnl": 0.0,
                "trades_count": 0,
                "max_drawdown": 0.0
            }
        
        self.daily_stats["total_pnl"] += pnl
        self.daily_stats["trades_count"] += trade_count
        
        # Update max drawdown
        if self.daily_stats["total_pnl"] < self.daily_stats["max_drawdown"]:
            self.daily_stats["max_drawdown"] = self.daily_stats["total_pnl"]
    
    def get_risk_metrics(self) -> Dict[str, Any]:
        """Get current risk metrics"""
        return {
            "config": self.config,
            "daily_stats": self.daily_stats,
            "risk_level": self._calculate_risk_level()
        }
    
    def _get_total_balance_usd(self, balances: List[Balance]) -> float:
        """Calculate total balance in USD"""
        # For simplicity, assume USDT = USD
        total = 0.0
        for balance in balances:
            if balance.asset in ["USDT", "USD", "BUSD"]:
                total += balance.total
        return total
    
    def _is_trading_hours(self) -> bool:
        """Check if current time is within trading hours"""
        current_hour = datetime.utcnow().hour
        start_hour = self.config["trading_hours"]["start"]
        end_hour = self.config["trading_hours"]["end"]
        
        if start_hour <= end_hour:
            return start_hour <= current_hour < end_hour
        else:  # Overnight trading
            return current_hour >= start_hour or current_hour < end_hour
    
    async def _validate_position_size(self, order_request: OrderRequest, 
                                    total_balance: float) -> bool:
        """Validate position size against limits"""
        try:
            # Calculate position value
            if order_request.price:
                position_value = order_request.quantity * order_request.price
            else:
                # For market orders, estimate with current price (would need market data)
                # For now, use a conservative approach
                position_value = order_request.quantity * 50000  # Assume BTC price
            
            # Check against maximum position size
            if position_value > self.config["max_position_size_usd"]:
                logger.warning(f"Position size too large: ${position_value:.2f}")
                return False
            
            # Check against account percentage
            max_position_by_account = total_balance * self.config["position_size_pct"]
            if position_value > max_position_by_account:
                logger.warning(f"Position size exceeds account percentage: "
                             f"${position_value:.2f} > ${max_position_by_account:.2f}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating position size: {e}")
            return False
    
    async def _validate_total_exposure(self, order_request: OrderRequest, 
                                     positions: List[Position]) -> bool:
        """Validate total exposure limits"""
        try:
            # Calculate current total exposure
            current_exposure = sum(pos.size * pos.mark_price for pos in positions)
            
            # Calculate new position exposure
            if order_request.price:
                new_exposure = order_request.quantity * order_request.price
            else:
                new_exposure = order_request.quantity * 50000  # Conservative estimate
            
            # For closing orders, reduce exposure
            if order_request.reduce_only:
                new_exposure = -new_exposure
            
            total_exposure = current_exposure + new_exposure
            
            if total_exposure > self.config["max_total_exposure_usd"]:
                logger.warning(f"Total exposure would exceed limit: "
                             f"${total_exposure:.2f} > ${self.config['max_total_exposure_usd']}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating total exposure: {e}")
            return False
    
    async def _validate_daily_limits(self) -> bool:
        """Validate daily loss limits"""
        if self.daily_stats["total_pnl"] < -self.config["max_daily_loss_usd"]:
            logger.warning(f"Daily loss limit exceeded: ${self.daily_stats['total_pnl']:.2f}")
            return False
        return True
    
    async def _validate_leverage(self, order_request: OrderRequest, 
                               account_balance: List[Balance], 
                               positions: List[Position]) -> bool:
        """Validate leverage limits"""
        try:
            total_balance = self._get_total_balance_usd(account_balance)
            total_exposure = sum(pos.size * pos.mark_price for pos in positions)
            
            # Add new position exposure
            if order_request.price:
                new_exposure = order_request.quantity * order_request.price
            else:
                new_exposure = order_request.quantity * 50000
            
            if not order_request.reduce_only:
                total_exposure += new_exposure
            
            if total_balance > 0:
                leverage = total_exposure / total_balance
                if leverage > self.config["max_leverage"]:
                    logger.warning(f"Leverage too high: {leverage:.2f}x > {self.config['max_leverage']}x")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating leverage: {e}")
            return False
    
    def _calculate_risk_level(self) -> str:
        """Calculate current risk level"""
        # Simple risk level calculation based on daily PnL
        daily_loss_pct = abs(self.daily_stats["total_pnl"]) / self.config["max_daily_loss_usd"]
        
        if daily_loss_pct < 0.3:
            return "LOW"
        elif daily_loss_pct < 0.7:
            return "MEDIUM"
        else:
            return "HIGH"

