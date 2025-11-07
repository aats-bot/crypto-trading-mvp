"""
Client model and related database operations
"""
from sqlalchemy import Column, String, Boolean, DateTime, Text, Float, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from datetime import datetime, UTC
import uuid

from .database import Base


class Client(Base):
    """Client model"""
    __tablename__ = "clients"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Basic information
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # API credentials (encrypted)
    bybit_api_key_encrypted = Column(Text, nullable=True)
    bybit_api_secret_encrypted = Column(Text, nullable=True)
    
    # Trading configuration
    trading_config = Column(JSON, nullable=True)
    risk_config = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<Client(id={self.id}, email={self.email}, name={self.name})>"
    
    def to_dict(self, include_sensitive=False):
        """Convert to dictionary"""
        data = {
            "id": str(self.id),
            "email": self.email,
            "name": self.name,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "trading_config": self.trading_config,
            "risk_config": self.risk_config,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None
        }
        
        if include_sensitive:
            data.update({
                "bybit_api_key_encrypted": self.bybit_api_key_encrypted,
                "bybit_api_secret_encrypted": self.bybit_api_secret_encrypted
            })
        
        return data


class ClientSession(Base):
    """Client session model for tracking active sessions"""
    __tablename__ = "client_sessions"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign key to client
    client_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Session data
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    user_agent = Column(Text, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    last_activity = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<ClientSession(id={self.id}, client_id={self.client_id})>"
    
    def is_expired(self):
        """Check if session is expired"""
        return datetime.now(UTC) > self.expires_at
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": str(self.id),
            "client_id": str(self.client_id),
            "session_token": self.session_token,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None,
            "is_expired": self.is_expired()
        }


class ClientConfiguration(Base):
    """Client trading configuration model"""
    __tablename__ = "client_configurations"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign key to client
    client_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Configuration name and type
    config_name = Column(String(100), nullable=False)
    config_type = Column(String(50), nullable=False)  # 'trading', 'risk', 'notification'
    
    # Configuration data
    config_data = Column(JSON, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<ClientConfiguration(id={self.id}, client_id={self.client_id}, name={self.config_name})>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": str(self.id),
            "client_id": str(self.client_id),
            "config_name": self.config_name,
            "config_type": self.config_type,
            "config_data": self.config_data,
            "is_active": self.is_active,
            "is_default": self.is_default,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class TradingPosition(Base):
    """Trading position model"""
    __tablename__ = "trading_positions"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign key to client
    client_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Position data
    symbol = Column(String(20), nullable=False, index=True)
    side = Column(String(10), nullable=False)  # 'Buy', 'Sell'
    size = Column(Float, nullable=False)
    entry_price = Column(Float, nullable=False)
    mark_price = Column(Float, nullable=True)
    
    # PnL data
    unrealized_pnl = Column(Float, default=0.0)
    realized_pnl = Column(Float, default=0.0)
    
    # Status
    is_open = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    opened_at = Column(DateTime(timezone=True), server_default=func.now())
    closed_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<TradingPosition(id={self.id}, client_id={self.client_id}, symbol={self.symbol})>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": str(self.id),
            "client_id": str(self.client_id),
            "symbol": self.symbol,
            "side": self.side,
            "size": self.size,
            "entry_price": self.entry_price,
            "mark_price": self.mark_price,
            "unrealized_pnl": self.unrealized_pnl,
            "realized_pnl": self.realized_pnl,
            "is_open": self.is_open,
            "opened_at": self.opened_at.isoformat() if self.opened_at else None,
            "closed_at": self.closed_at.isoformat() if self.closed_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class TradingOrder(Base):
    """Trading order model"""
    __tablename__ = "trading_orders"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign key to client
    client_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # External order ID from exchange
    exchange_order_id = Column(String(100), nullable=True, index=True)
    
    # Order data
    symbol = Column(String(20), nullable=False, index=True)
    side = Column(String(10), nullable=False)  # 'Buy', 'Sell'
    order_type = Column(String(20), nullable=False)  # 'Market', 'Limit', etc.
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=True)
    filled_quantity = Column(Float, default=0.0)
    avg_price = Column(Float, nullable=True)
    
    # Status
    status = Column(String(20), nullable=False, default='New')  # 'New', 'Filled', 'Cancelled', etc.
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    filled_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<TradingOrder(id={self.id}, client_id={self.client_id}, symbol={self.symbol})>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": str(self.id),
            "client_id": str(self.client_id),
            "exchange_order_id": self.exchange_order_id,
            "symbol": self.symbol,
            "side": self.side,
            "order_type": self.order_type,
            "quantity": self.quantity,
            "price": self.price,
            "filled_quantity": self.filled_quantity,
            "avg_price": self.avg_price,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "filled_at": self.filled_at.isoformat() if self.filled_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

