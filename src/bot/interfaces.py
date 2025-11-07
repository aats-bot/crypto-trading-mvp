from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List


# =========================
# Enums
# =========================
class OrderSide(str, Enum):
    BUY = "Buy"
    SELL = "Sell"


class OrderType(str, Enum):
    MARKET = "Market"
    LIMIT = "Limit"


class PositionSide(str, Enum):
    LONG = "LONG"
    SHORT = "SHORT"


class OrderStatus(str, Enum):
    NEW = "NEW"
    FILLED = "FILLED"
    CANCELED = "CANCELED"


# =========================
# Modelos / DTOs
# =========================
@dataclass
class MarketData:
    symbol: str
    price: float
    timestamp: datetime
    volume: float
    bid: Optional[float] = None
    ask: Optional[float] = None
    high_24h: Optional[float] = None
    low_24h: Optional[float] = None
    change_24h: Optional[float] = None


@dataclass
class OrderRequest:
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
    id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: float
    price: Optional[float] = None
    status: OrderStatus = OrderStatus.NEW
    created_at: datetime = field(default_factory=lambda: datetime.now())


@dataclass
class Position:
    symbol: str
    side: PositionSide
    size: float
    entry_price: float
    # Campos que geravam erro nos testes quando obrigatórios:
    mark_price: Optional[float] = None
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0
    timestamp: datetime = field(default_factory=lambda: datetime.now())


@dataclass
class Balance:
    asset: str
    free: float
    locked: float = 0.0


@dataclass
class AccountInfo:
    balances: List[Balance]


# =========================
# “Interfaces” (contratos mínimos)
# =========================
class MarketDataProvider:
    async def get_market_data(self, symbol: str) -> MarketData:  # pragma: no cover
        raise NotImplementedError


class OrderExecutor:
    async def place_order(self, req: OrderRequest) -> Order:  # pragma: no cover
        raise NotImplementedError


class AccountManager:
    async def get_account_info(self) -> AccountInfo:  # pragma: no cover
        raise NotImplementedError


__all__ = [
    "OrderSide",
    "OrderType",
    "PositionSide",
    "OrderStatus",
    "MarketData",
    "OrderRequest",
    "Order",
    "Position",
    "Balance",
    "AccountInfo",
    "MarketDataProvider",
    "OrderExecutor",
    "AccountManager",
]
