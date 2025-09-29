"""
Client management service
"""
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext
import secrets

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

from src.models.client import Client, ClientSession, ClientConfiguration
from src.security.encryption import encrypt_api_key, decrypt_api_key

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class ClientService:
    """Service for managing clients"""
    
    def __init__(self):
        self.session_duration = timedelta(hours=24)  # 24 hours session
    
    async def create_client(self, session: AsyncSession, 
                          email: str, name: str, password: str,
                          bybit_api_key: str = None, bybit_api_secret: str = None) -> Client:
        """Create a new client"""
        try:
            # Check if email already exists
            existing_client = await self.get_client_by_email(session, email)
            if existing_client:
                raise ValueError("Email already registered")
            
            # Hash password
            password_hash = pwd_context.hash(password)
            
            # Encrypt API keys if provided
            encrypted_api_key = None
            encrypted_api_secret = None
            
            if bybit_api_key and bybit_api_secret:
                encrypted_api_key = encrypt_api_key(bybit_api_key)
                encrypted_api_secret = encrypt_api_key(bybit_api_secret)
            
            # Create client
            client = Client(
                email=email,
                name=name,
                password_hash=password_hash,
                bybit_api_key_encrypted=encrypted_api_key,
                bybit_api_secret_encrypted=encrypted_api_secret,
                trading_config=self._get_default_trading_config(),
                risk_config=self._get_default_risk_config()
            )
            
            session.add(client)
            await session.commit()
            await session.refresh(client)
            
            logger.info(f"Created new client: {email}")
            return client
            
        except IntegrityError:
            await session.rollback()
            raise ValueError("Email already registered")
        except Exception as e:
            await session.rollback()
            logger.error(f"Error creating client: {e}")
            raise
    
    async def authenticate_client(self, session: AsyncSession, 
                                email: str, password: str) -> Optional[Client]:
        """Authenticate client with email and password"""
        try:
            client = await self.get_client_by_email(session, email)
            
            if not client:
                return None
            
            if not client.is_active:
                return None
            
            # Verify password
            if not pwd_context.verify(password, client.password_hash):
                return None
            
            # Update last login
            client.last_login = datetime.utcnow()
            await session.commit()
            
            logger.info(f"Client authenticated: {email}")
            return client
            
        except Exception as e:
            logger.error(f"Error authenticating client: {e}")
            return None
    
    async def create_session(self, session: AsyncSession, client_id: uuid.UUID,
                           ip_address: str = None, user_agent: str = None) -> ClientSession:
        """Create a new client session"""
        try:
            # Generate session token
            session_token = secrets.token_urlsafe(32)
            
            # Create session
            client_session = ClientSession(
                client_id=client_id,
                session_token=session_token,
                ip_address=ip_address,
                user_agent=user_agent,
                expires_at=datetime.utcnow() + self.session_duration
            )
            
            session.add(client_session)
            await session.commit()
            await session.refresh(client_session)
            
            logger.info(f"Created session for client: {client_id}")
            return client_session
            
        except Exception as e:
            await session.rollback()
            logger.error(f"Error creating session: {e}")
            raise
    
    async def get_client_by_session(self, session: AsyncSession, 
                                  session_token: str) -> Optional[Client]:
        """Get client by session token"""
        try:
            # Get session
            stmt = select(ClientSession).where(
                ClientSession.session_token == session_token,
                ClientSession.is_active == True
            )
            result = await session.execute(stmt)
            client_session = result.scalar_one_or_none()
            
            if not client_session or client_session.is_expired():
                return None
            
            # Update last activity
            client_session.last_activity = datetime.utcnow()
            
            # Get client
            client = await self.get_client_by_id(session, client_session.client_id)
            
            await session.commit()
            return client
            
        except Exception as e:
            logger.error(f"Error getting client by session: {e}")
            return None
    
    async def invalidate_session(self, session: AsyncSession, session_token: str) -> bool:
        """Invalidate a client session"""
        try:
            stmt = update(ClientSession).where(
                ClientSession.session_token == session_token
            ).values(is_active=False)
            
            result = await session.execute(stmt)
            await session.commit()
            
            return result.rowcount > 0
            
        except Exception as e:
            logger.error(f"Error invalidating session: {e}")
            return False
    
    async def get_client_by_id(self, session: AsyncSession, client_id: uuid.UUID) -> Optional[Client]:
        """Get client by ID"""
        try:
            stmt = select(Client).where(Client.id == client_id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting client by ID: {e}")
            return None
    
    async def get_client_by_email(self, session: AsyncSession, email: str) -> Optional[Client]:
        """Get client by email"""
        try:
            stmt = select(Client).where(Client.email == email)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting client by email: {e}")
            return None
    
    async def update_client(self, session: AsyncSession, client_id: uuid.UUID, 
                          updates: Dict[str, Any]) -> Optional[Client]:
        """Update client information"""
        try:
            # Get client
            client = await self.get_client_by_id(session, client_id)
            if not client:
                return None
            
            # Update fields
            for field, value in updates.items():
                if hasattr(client, field):
                    if field == "password" and value:
                        # Hash new password
                        client.password_hash = pwd_context.hash(value)
                    elif field == "bybit_api_key" and value:
                        # Encrypt API key
                        client.bybit_api_key_encrypted = encrypt_api_key(value)
                    elif field == "bybit_api_secret" and value:
                        # Encrypt API secret
                        client.bybit_api_secret_encrypted = encrypt_api_key(value)
                    else:
                        setattr(client, field, value)
            
            client.updated_at = datetime.utcnow()
            await session.commit()
            await session.refresh(client)
            
            logger.info(f"Updated client: {client_id}")
            return client
            
        except Exception as e:
            await session.rollback()
            logger.error(f"Error updating client: {e}")
            raise
    
    async def deactivate_client(self, session: AsyncSession, client_id: uuid.UUID) -> bool:
        """Deactivate a client"""
        try:
            stmt = update(Client).where(
                Client.id == client_id
            ).values(is_active=False, updated_at=datetime.utcnow())
            
            result = await session.execute(stmt)
            await session.commit()
            
            if result.rowcount > 0:
                logger.info(f"Deactivated client: {client_id}")
                return True
            
            return False
            
        except Exception as e:
            await session.rollback()
            logger.error(f"Error deactivating client: {e}")
            return False
    
    async def get_client_api_keys(self, session: AsyncSession, client_id: uuid.UUID) -> Optional[Dict[str, str]]:
        """Get decrypted API keys for a client"""
        try:
            client = await self.get_client_by_id(session, client_id)
            if not client:
                return None
            
            if not client.bybit_api_key_encrypted or not client.bybit_api_secret_encrypted:
                return None
            
            # Decrypt API keys
            api_key = decrypt_api_key(client.bybit_api_key_encrypted)
            api_secret = decrypt_api_key(client.bybit_api_secret_encrypted)
            
            return {
                "api_key": api_key,
                "api_secret": api_secret
            }
            
        except Exception as e:
            logger.error(f"Error getting client API keys: {e}")
            return None
    
    async def list_clients(self, session: AsyncSession, 
                         skip: int = 0, limit: int = 100,
                         active_only: bool = True) -> List[Client]:
        """List clients with pagination"""
        try:
            stmt = select(Client)
            
            if active_only:
                stmt = stmt.where(Client.is_active == True)
            
            stmt = stmt.offset(skip).limit(limit).order_by(Client.created_at.desc())
            
            result = await session.execute(stmt)
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"Error listing clients: {e}")
            return []
    
    def _get_default_trading_config(self) -> Dict[str, Any]:
        """Get default trading configuration"""
        return {
            "strategy": "sma",
            "symbols": ["BTCUSDT"],
            "fast_period": 10,
            "slow_period": 20,
            "risk_per_trade": 0.02,
            "update_interval": 30,
            "auto_start": False
        }
    
    def _get_default_risk_config(self) -> Dict[str, Any]:
        """Get default risk configuration"""
        return {
            "max_position_size_usd": 1000.0,
            "max_daily_loss_usd": 100.0,
            "max_open_positions": 3,
            "stop_loss_pct": 0.02,
            "take_profit_pct": 0.04,
            "max_leverage": 3.0
        }

