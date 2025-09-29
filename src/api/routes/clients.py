"""
Client management routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
import logging
import uuid

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

from src.models.database import get_async_session
from src.api.services.client_service import ClientService
from src.models.client import Client
from src.api.routes.auth import get_current_client

logger = logging.getLogger(__name__)

router = APIRouter()
client_service = ClientService()


class UpdateClientRequest(BaseModel):
    name: Optional[str] = None
    bybit_api_key: Optional[str] = None
    bybit_api_secret: Optional[str] = None
    trading_config: Optional[Dict[str, Any]] = None
    risk_config: Optional[Dict[str, Any]] = None


class ClientResponse(BaseModel):
    client: dict
    message: str


@router.get("/profile", response_model=ClientResponse)
async def get_profile(
    current_client: Client = Depends(get_current_client)
):
    """Get client profile"""
    return ClientResponse(
        client=current_client.to_dict(),
        message="Profile retrieved successfully"
    )


@router.put("/profile", response_model=ClientResponse)
async def update_profile(
    request: UpdateClientRequest,
    current_client: Client = Depends(get_current_client),
    session: AsyncSession = Depends(get_async_session)
):
    """Update client profile"""
    try:
        # Prepare updates
        updates = {}
        
        if request.name is not None:
            updates["name"] = request.name
        
        if request.bybit_api_key is not None:
            updates["bybit_api_key"] = request.bybit_api_key
        
        if request.bybit_api_secret is not None:
            updates["bybit_api_secret"] = request.bybit_api_secret
        
        if request.trading_config is not None:
            updates["trading_config"] = request.trading_config
        
        if request.risk_config is not None:
            updates["risk_config"] = request.risk_config
        
        # Update client
        updated_client = await client_service.update_client(
            session=session,
            client_id=current_client.id,
            updates=updates
        )
        
        if not updated_client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found"
            )
        
        logger.info(f"Client profile updated: {current_client.email}")
        
        return ClientResponse(
            client=updated_client.to_dict(),
            message="Profile updated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating client profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile update failed"
        )


@router.get("/api-keys")
async def get_api_keys_status(
    current_client: Client = Depends(get_current_client),
    session: AsyncSession = Depends(get_async_session)
):
    """Get API keys status (without revealing actual keys)"""
    try:
        api_keys = await client_service.get_client_api_keys(session, current_client.id)
        
        has_api_keys = api_keys is not None and api_keys.get("api_key") and api_keys.get("api_secret")
        
        return {
            "has_api_keys": has_api_keys,
            "api_key_length": len(api_keys.get("api_key", "")) if has_api_keys else 0,
            "message": "API keys status retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Error getting API keys status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get API keys status"
        )


@router.get("/trading-config")
async def get_trading_config(
    current_client: Client = Depends(get_current_client)
):
    """Get client trading configuration"""
    return {
        "trading_config": current_client.trading_config,
        "risk_config": current_client.risk_config,
        "message": "Trading configuration retrieved successfully"
    }


@router.put("/trading-config")
async def update_trading_config(
    trading_config: Dict[str, Any],
    current_client: Client = Depends(get_current_client),
    session: AsyncSession = Depends(get_async_session)
):
    """Update client trading configuration"""
    try:
        # Validate trading config (basic validation)
        required_fields = ["strategy", "symbols"]
        for field in required_fields:
            if field not in trading_config:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Missing required field: {field}"
                )
        
        # Update client
        updated_client = await client_service.update_client(
            session=session,
            client_id=current_client.id,
            updates={"trading_config": trading_config}
        )
        
        if not updated_client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found"
            )
        
        logger.info(f"Trading config updated for client: {current_client.email}")
        
        return {
            "trading_config": updated_client.trading_config,
            "message": "Trading configuration updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating trading config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Trading configuration update failed"
        )


@router.put("/risk-config")
async def update_risk_config(
    risk_config: Dict[str, Any],
    current_client: Client = Depends(get_current_client),
    session: AsyncSession = Depends(get_async_session)
):
    """Update client risk configuration"""
    try:
        # Validate risk config (basic validation)
        numeric_fields = ["max_position_size_usd", "max_daily_loss_usd", "stop_loss_pct"]
        for field in numeric_fields:
            if field in risk_config:
                try:
                    float(risk_config[field])
                except (ValueError, TypeError):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid numeric value for {field}"
                    )
        
        # Update client
        updated_client = await client_service.update_client(
            session=session,
            client_id=current_client.id,
            updates={"risk_config": risk_config}
        )
        
        if not updated_client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found"
            )
        
        logger.info(f"Risk config updated for client: {current_client.email}")
        
        return {
            "risk_config": updated_client.risk_config,
            "message": "Risk configuration updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating risk config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Risk configuration update failed"
        )


@router.delete("/account")
async def deactivate_account(
    current_client: Client = Depends(get_current_client),
    session: AsyncSession = Depends(get_async_session)
):
    """Deactivate client account"""
    try:
        success = await client_service.deactivate_client(session, current_client.id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found"
            )
        
        logger.info(f"Client account deactivated: {current_client.email}")
        
        return {
            "message": "Account deactivated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deactivating account: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Account deactivation failed"
        )

