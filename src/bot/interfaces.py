"""
Abstract interfaces for trading bot components
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class OrderSide(Enum):
    """Order side enumeration"""
    BUY = "Buy"
    SELL = "Sell"


class OrderType(Enum):
    """Order type enumeration"""
    MARKET = "Market"
    LIMIT = "Limit"
    STOP = "Stop"
    STOP_LIMIT = "StopLimit"


class PositionSide(Enum):
    """Position side enumeration"""
    LONG = "Buy"
    SHORT = "Sell"
    NONE = "None"


@dataclass
class MarketData:
    """Market data structure"""
    symbol: str
    timestamp: datetime
    price: float
    volume: float
    bid: Optional[float] = None
    ask: Optional[float] = None
    high_24h: Optional[float] = None
    low_24h: Optional[float] = None
    change_24h: Optional[float] = None


@dataclass
class OrderRequest:
    """Order request structure"""
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: float
    price: Optional[float] = None
    stop_price: Optional[float] = None
    time_in_force: str = "GTC"
    reduce_only: bool = False


@dataclass
class Order:
    """Order structure"""
    order_id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: float
    price: Optional[float]
    filled_quantity: float
    status: str
    timestamp: datetime
    avg_price: Optional[float] = None


@dataclass
class Position:
    """Position structure"""
    symbol: str
    side: PositionSide
    size: float
    entry_price: float
    mark_price: float
    unrealized_pnl: float
    realized_pnl: float
    timestamp: datetime


@dataclass
class Balance:
    """Balance structure"""
    asset: str
    free: float
    locked: float
    total: float


class MarketDataProvider(ABC):
    """Abstract market data provider interface"""
    
    @abstractmethod
    async def get_ticker(self, symbol: str) -> MarketData:
        """Get current ticker data for a symbol"""
        pass
    
    @abstractmethod
    async def get_orderbook(self, symbol: str, limit: int = 20) -> Dict[str, Any]:
        """Get orderbook data for a symbol"""
        pass
    
    @abstractmethod
    async def get_klines(self, symbol: str, interval: str, limit: int = 100) -> List[Dict]:
        """Get kline/candlestick data"""
        pass
    
    @abstractmethod
    async def subscribe_ticker(self, symbol: str, callback) -> None:
        """Subscribe to real-time ticker updates"""
        pass
    
    @abstractmethod
    async def subscribe_orderbook(self, symbol: str, callback) -> None:
        """Subscribe to real-time orderbook updates"""
        pass


class OrderExecutor(ABC):
    """Abstract order executor interface"""
    
    @abstractmethod
    async def place_order(self, order_request: OrderRequest) -> Order:
        """Place a new order"""
        pass
    
    @abstractmethod
    async def cancel_order(self, symbol: str, order_id: str) -> bool:
        """Cancel an existing order"""
        pass
    
    @abstractmethod
    async def get_order(self, symbol: str, order_id: str) -> Optional[Order]:
        """Get order details"""
        pass
    
    @abstractmethod
    async def get_open_orders(self, symbol: Optional[str] = None) -> List[Order]:
        """Get all open orders"""
        pass
    
    @abstractmethod
    async def get_order_history(self, symbol: Optional[str] = None, limit: int = 100) -> List[Order]:
        """Get order history"""
        pass


class AccountManager(ABC):
    """Abstract account manager interface"""
    
    @abstractmethod
    async def get_balance(self) -> List[Balance]:
        """Get account balance"""
        pass
    
    @abstractmethod
    async def get_positions(self, symbol: Optional[str] = None) -> List[Position]:
        """Get current positions"""
        pass
    
    @abstractmethod
    async def get_position(self, symbol: str) -> Optional[Position]:
        """Get position for specific symbol"""
        pass
    
    @abstractmethod
    async def close_position(self, symbol: str, quantity: Optional[float] = None) -> Order:
        """Close position (market order)"""
        pass


class TradingStrategy(ABC):
    """Abstract trading strategy interface"""
    
    @abstractmethod
    async def analyze(self, market_data: MarketData, positions: List[Position]) -> List[OrderRequest]:
        """Analyze market data and return trading signals"""
        pass
    
    @abstractmethod
    async def on_order_filled(self, order: Order) -> None:
        """Handle order fill events"""
        pass
    
    @abstractmethod
    async def on_position_update(self, position: Position) -> None:
        """Handle position update events"""
        pass
    
    @abstractmethod
    def get_risk_parameters(self) -> Dict[str, Any]:
        """Get current risk parameters"""
        pass
    
    @abstractmethod
    def update_risk_parameters(self, parameters: Dict[str, Any]) -> None:
        """Update risk parameters"""
        pass


class RiskManager(ABC):
    """Abstract risk manager interface"""
    
    @abstractmethod
    async def validate_order(self, order_request: OrderRequest, account_balance: List[Balance], 
                           positions: List[Position]) -> bool:
        """Validate order against risk parameters"""
        pass
    
    @abstractmethod
    async def check_position_limits(self, positions: List[Position]) -> List[str]:
        """Check if positions exceed limits"""
        pass
    
    @abstractmethod
    async def calculate_position_size(self, symbol: str, entry_price: float, 
                                    stop_loss: float, risk_amount: float) -> float:
        """Calculate appropriate position size based on risk"""
        pass
    
    @abstractmethod
    def get_max_position_size(self, symbol: str) -> float:
        """Get maximum allowed position size for symbol"""
        pass

