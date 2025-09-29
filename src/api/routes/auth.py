"""
Authentication routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr
from typing import Optional
import logging

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

from src.models.database import get_async_session
from src.api.services.client_service import ClientService
from src.models.client import Client

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()
client_service = ClientService()


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    name: str
    password: str
    bybit_api_key: Optional[str] = None
    bybit_api_secret: Optional[str] = None


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    client: dict


class RegisterResponse(BaseModel):
    message: str
    client: dict


async def get_current_client(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_async_session)
) -> Client:
    """Get current authenticated client"""
    try:
        token = credentials.credentials
        client = await client_service.get_client_by_session(session, token)
        
        if not client:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        return client
        
    except Exception as e:
        logger.error(f"Error getting current client: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )


@router.post("/register", response_model=RegisterResponse)
async def register(
    request: RegisterRequest,
    session: AsyncSession = Depends(get_async_session)
):
    """Register a new client"""
    try:
        # Create client
        client = await client_service.create_client(
            session=session,
            email=request.email,
            name=request.name,
            password=request.password,
            bybit_api_key=request.bybit_api_key,
            bybit_api_secret=request.bybit_api_secret
        )
        
        logger.info(f"New client registered: {request.email}")
        
        return RegisterResponse(
            message="Client registered successfully",
            client=client.to_dict()
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error registering client: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    http_request: Request,
    session: AsyncSession = Depends(get_async_session)
):
    """Login client"""
    try:
        # Authenticate client
        client = await client_service.authenticate_client(
            session=session,
            email=request.email,
            password=request.password
        )
        
        if not client:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Create session
        client_session = await client_service.create_session(
            session=session,
            client_id=client.id,
            ip_address=http_request.client.host if http_request.client else None,
            user_agent=http_request.headers.get("user-agent")
        )
        
        logger.info(f"Client logged in: {request.email}")
        
        return LoginResponse(
            access_token=client_session.session_token,
            client=client.to_dict()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error logging in client: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_async_session)
):
    """Logout client"""
    try:
        token = credentials.credentials
        success = await client_service.invalidate_session(session, token)
        
        if success:
            return {"message": "Logged out successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid session"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error logging out client: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )


@router.get("/me")
async def get_current_user_info(
    current_client: Client = Depends(get_current_client)
):
    """Get current client information"""
    return {
        "client": current_client.to_dict(),
        "message": "Client information retrieved successfully"
    }

