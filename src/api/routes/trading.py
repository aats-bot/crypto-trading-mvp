"""
Trading routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging
import uuid

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

from src.models.database import get_async_session
from src.models.client import Client
from src.api.routes.auth import get_current_client

logger = logging.getLogger(__name__)

router = APIRouter()


class BotStatusResponse(BaseModel):
    client_id: str
    is_running: bool
    is_paused: bool
    last_update: Optional[str]
    error_count: int
    stats: Dict[str, Any]
    strategy_info: Dict[str, Any]
    risk_metrics: Dict[str, Any]


class BotControlRequest(BaseModel):
    action: str  # 'start', 'stop', 'pause', 'resume'


@router.get("/status", response_model=BotStatusResponse)
async def get_bot_status(
    current_client: Client = Depends(get_current_client)
):
    """Get trading bot status for current client"""
    try:
        # For MVP, return mock status
        # In production, this would query the actual bot worker
        mock_status = {
            "client_id": str(current_client.id),
            "is_running": False,
            "is_paused": False,
            "last_update": None,
            "error_count": 0,
            "stats": {
                "start_time": None,
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "total_pnl": 0.0,
                "max_drawdown": 0.0,
                "last_trade_time": None
            },
            "strategy_info": {
                "name": current_client.trading_config.get("strategy", "sma") if current_client.trading_config else "sma",
                "symbols": current_client.trading_config.get("symbols", ["BTCUSDT"]) if current_client.trading_config else ["BTCUSDT"]
            },
            "risk_metrics": {
                "config": current_client.risk_config or {},
                "risk_level": "LOW"
            }
        }
        
        return BotStatusResponse(**mock_status)
        
    except Exception as e:
        logger.error(f"Error getting bot status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get bot status"
        )


@router.post("/control")
async def control_bot(
    request: BotControlRequest,
    current_client: Client = Depends(get_current_client)
):
    """Control trading bot (start, stop, pause, resume)"""
    try:
        valid_actions = ["start", "stop", "pause", "resume"]
        
        if request.action not in valid_actions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid action. Must be one of: {valid_actions}"
            )
        
        # For MVP, return mock response
        # In production, this would send commands to the bot worker
        logger.info(f"Bot control action '{request.action}' requested for client {current_client.email}")
        
        return {
            "message": f"Bot {request.action} command sent successfully",
            "action": request.action,
            "client_id": str(current_client.id)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error controlling bot: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Bot control failed"
        )


@router.get("/positions")
async def get_positions(
    current_client: Client = Depends(get_current_client)
):
    """Get current trading positions"""
    try:
        # For MVP, return mock positions
        # In production, this would query actual positions from the bot
        mock_positions = []
        
        return {
            "positions": mock_positions,
            "total_positions": len(mock_positions),
            "message": "Positions retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Error getting positions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get positions"
        )


@router.get("/orders")
async def get_orders(
    current_client: Client = Depends(get_current_client),
    limit: int = 50
):
    """Get trading orders history"""
    try:
        # For MVP, return mock orders
        # In production, this would query actual orders from the database
        mock_orders = []
        
        return {
            "orders": mock_orders,
            "total_orders": len(mock_orders),
            "limit": limit,
            "message": "Orders retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Error getting orders: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get orders"
        )


@router.get("/performance")
async def get_performance(
    current_client: Client = Depends(get_current_client)
):
    """Get trading performance metrics"""
    try:
        # For MVP, return mock performance data
        # In production, this would calculate actual performance metrics
        mock_performance = {
            "total_balance": 10000.0,
            "total_unrealized_pnl": 0.0,
            "total_trades": 0,
            "win_rate": 0.0,
            "max_drawdown": 0.0,
            "positions": 0,
            "strategy": current_client.trading_config.get("strategy", "sma") if current_client.trading_config else "sma",
            "risk_level": "LOW",
            "uptime": 0
        }
        
        return {
            "performance": mock_performance,
            "message": "Performance metrics retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Error getting performance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get performance metrics"
        )


@router.get("/balance")
async def get_balance(
    current_client: Client = Depends(get_current_client)
):
    """Get account balance"""
    try:
        # For MVP, return mock balance
        # In production, this would query actual balance from the exchange
        mock_balance = [
            {
                "asset": "USDT",
                "free": 10000.0,
                "locked": 0.0,
                "total": 10000.0
            }
        ]
        
        return {
            "balance": mock_balance,
            "message": "Balance retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Error getting balance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get balance"
        )

