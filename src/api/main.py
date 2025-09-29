# Métricas Prometheus
try:
    from .metrics import get_prometheus_metrics, metrics_collector, CONTENT_TYPE_LATEST
    METRICS_AVAILABLE = True
except ImportError:
    METRICS_AVAILABLE = False
    print("⚠️ Módulo de métricas não disponível")

# -*- coding: utf-8 -*-
"""
Crypto Trading MVP - API Completa v2.0
FastAPI application with full authentication and trading endpoints
Estrutura: src/ exclusivamente (sem pasta app/)
"""

import os
import sys
import logging
import jwt
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from pathlib import Path

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import uvicorn

# Configure logging
log_dir = "/app/logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler(f'{log_dir}/api.log', mode='a'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Security configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "crypto-trading-mvp-secret-key-2024")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440

# Create FastAPI app
app = FastAPI(
    title="Crypto Trading MVP API",
    description="Complete API for cryptocurrency trading bot - SRC Structure",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Security
security = HTTPBearer()

# Pydantic models
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user_info: Dict[str, str]

class UserInfo(BaseModel):
    username: str
    user_id: str
    tenant_id: str
    role: str

class TradingConfig(BaseModel):
    strategy: str = "PPP_Vishva"
    symbol: str = "BTCUSDT"
    amount: float = 100.0
    risk_level: str = "medium"
    stop_loss: float = 0.02
    take_profit: float = 0.05

class TradingStatus(BaseModel):
    is_active: bool
    strategy: str
    symbol: str
    pnl: float
    trades_count: int
    uptime: str

class TradeHistory(BaseModel):
    id: str
    symbol: str
    side: str
    amount: float
    price: float
    pnl: float
    timestamp: str

class SystemStatus(BaseModel):
    api: str
    database: str
    redis: str
    worker: str
    bybit: str
    uptime: str
    version: str

# Mock database (in production, use real database)
USERS_DB = {
    "admin": {
        "password_hash": hashlib.sha256("admin123".encode()).hexdigest(),
        "user_id": "user_001",
        "tenant_id": "tenant_001",
        "role": "admin"
    },
    "demo": {
        "password_hash": hashlib.sha256("demo123".encode()).hexdigest(),
        "user_id": "user_002", 
        "tenant_id": "tenant_002",
        "role": "user"
    },
    "trader": {
        "password_hash": hashlib.sha256("trader123".encode()).hexdigest(),
        "user_id": "user_003",
        "tenant_id": "tenant_003", 
        "role": "trader"
    }
}

# Utility functions
def create_access_token(data: dict):
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token"""
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def hash_password(password: str) -> str:
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def get_user_info(username: str) -> Dict[str, str]:
    """Get user information"""
    user = USERS_DB.get(username)
    if not user:
        return {}
    return {
        "username": username,
        "user_id": user["user_id"],
        "tenant_id": user["tenant_id"],
        "role": user["role"]
    }

# Health check endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "crypto-trading-api",
        "version": "2.0.0",
        "structure": "src/",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Crypto Trading MVP API v2.0",
        "structure": "src/ (app/ obsoleta)",
        "version": "2.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "auth": "/api/auth/*",
            "trading": "/api/trading/*",
            "user": "/api/user/*",
            "system": "/api/system/*"
        },
        "timestamp": datetime.utcnow().isoformat()
    }

# Authentication endpoints
@app.post("/api/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """User login endpoint with JWT token"""
    logger.info(f"Login attempt for user: {request.username}")
    
    # Validate user
    user = USERS_DB.get(request.username)
    if not user:
        logger.warning(f"Login failed: user not found - {request.username}")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Verify password
    password_hash = hash_password(request.password)
    if password_hash != user["password_hash"]:
        logger.warning(f"Login failed: invalid password - {request.username}")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create token
    access_token = create_access_token(data={"sub": request.username})
    user_info = get_user_info(request.username)
    
    logger.info(f"Login successful for user: {request.username}")
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_info=user_info
    )

@app.post("/api/auth/logout")
async def logout(username: str = Depends(verify_token)):
    """User logout endpoint"""
    logger.info(f"Logout for user: {username}")
    return {
        "message": "Logged out successfully",
        "user": username,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/auth/me", response_model=UserInfo)
async def get_current_user(username: str = Depends(verify_token)):
    """Get current user information"""
    user = USERS_DB.get(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserInfo(
        username=username,
        user_id=user["user_id"],
        tenant_id=user["tenant_id"],
        role=user["role"]
    )

@app.post("/api/auth/refresh")
async def refresh_token(username: str = Depends(verify_token)):
    """Refresh JWT token"""
    access_token = create_access_token(data={"sub": username})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

# Trading endpoints
@app.get("/api/trading/status", response_model=TradingStatus)
async def get_trading_status(username: str = Depends(verify_token)):
    """Get current trading status"""
    logger.info(f"Getting trading status for user: {username}")
    
    # Mock trading status (in production, get from database)
    return TradingStatus(
        is_active=True,
        strategy="PPP_Vishva",
        symbol="BTCUSDT",
        pnl=125.50,
        trades_count=15,
        uptime="2h 30m"
    )

@app.post("/api/trading/start")
async def start_trading(config: TradingConfig, username: str = Depends(verify_token)):
    """Start trading with specified configuration"""
    logger.info(f"Starting trading for user {username} with config: {config.dict()}")
    
    # Mock implementation (in production, start actual trading)
    return {
        "message": "Trading started successfully",
        "config": config.dict(),
        "user": username,
        "timestamp": datetime.utcnow().isoformat(),
        "status": "active"
    }

@app.post("/api/trading/stop")
async def stop_trading(username: str = Depends(verify_token)):
    """Stop current trading"""
    logger.info(f"Stopping trading for user: {username}")
    
    # Mock implementation (in production, stop actual trading)
    return {
        "message": "Trading stopped successfully",
        "user": username,
        "timestamp": datetime.utcnow().isoformat(),
        "status": "stopped"
    }

@app.get("/api/trading/history")
async def get_trading_history(username: str = Depends(verify_token), limit: int = 10):
    """Get trading history"""
    logger.info(f"Getting trading history for user: {username}, limit: {limit}")
    
    # Mock trading history (in production, get from database)
    trades = [
        {
            "id": f"trade_{i:03d}",
            "symbol": "BTCUSDT",
            "side": "buy" if i % 2 == 0 else "sell",
            "amount": 0.001 * (i + 1),
            "price": 65000.0 + (i * 100),
            "pnl": 25.50 * (i + 1),
            "timestamp": (datetime.utcnow() - timedelta(hours=i)).isoformat()
        }
        for i in range(min(limit, 15))
    ]
    
    return {
        "trades": trades,
        "total_pnl": sum(trade["pnl"] for trade in trades),
        "total_trades": len(trades),
        "user": username
    }

@app.get("/api/trading/positions")
async def get_positions(username: str = Depends(verify_token)):
    """Get current trading positions"""
    # Mock positions (in production, get from exchange)
    return {
        "positions": [
            {
                "symbol": "BTCUSDT",
                "side": "long",
                "size": 0.001,
                "entry_price": 65000.0,
                "current_price": 65500.0,
                "pnl": 50.0,
                "percentage": 0.77
            }
        ],
        "total_pnl": 50.0,
        "user": username
    }

# System endpoints
@app.get("/api/system/status", response_model=SystemStatus)
async def get_system_status(username: str = Depends(verify_token)):
    """Get system status"""
    return SystemStatus(
        api="running",
        database="connected",
        redis="connected", 
        worker="active",
        bybit="connected",
        uptime="24h 15m",
        version="2.0.0"
    )

@app.get("/api/system/metrics")
async def get_system_metrics(username: str = Depends(verify_token)):
    """Get system metrics"""
    return {
        "active_users": 3,
        "active_strategies": 5,
        "total_trades_today": 45,
        "system_load": 0.65,
        "memory_usage": 0.45,
        "api_requests_per_minute": 120,
        "structure": "src/",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/system/logs")
async def get_system_logs(username: str = Depends(verify_token), lines: int = 50):
    """Get system logs"""
    # Mock logs (in production, read from actual log files)
    return {
        "logs": [
            f"[{datetime.utcnow().isoformat()}] INFO: System running normally",
            f"[{datetime.utcnow().isoformat()}] INFO: API requests: 120/min",
            f"[{datetime.utcnow().isoformat()}] INFO: Trading active: 3 users"
        ],
        "lines": lines,
        "user": username
    }

# User management endpoints
@app.get("/api/user/profile")
async def get_user_profile(username: str = Depends(verify_token)):
    """Get user profile"""
    user_info = get_user_info(username)
    return {
        "profile": user_info,
        "last_login": datetime.utcnow().isoformat(),
        "total_trades": 15,
        "total_pnl": 125.50
    }

@app.put("/api/user/settings")
async def update_user_settings(settings: Dict[str, Any], username: str = Depends(verify_token)):
    """Update user settings"""
    logger.info(f"Updating settings for user: {username}")
    return {
        "message": "Settings updated successfully",
        "settings": settings,
        "user": username,
        "timestamp": datetime.utcnow().isoformat()
    }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {
        "error": "Endpoint not found",
        "detail": f"The endpoint {request.url.path} was not found",
        "structure": "src/",
        "available_endpoints": ["/health", "/docs", "/api/auth/login"]
    }

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {exc}")
    return {
        "error": "Internal server error",
        "detail": "An unexpected error occurred",
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    logger.info("Starting Crypto Trading MVP API v2.0.0 (SRC Structure)...")
    
    # Get configuration from environment
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))
    
    logger.info(f"API starting on {host}:{port}")
    logger.info("Structure: src/ (pasta app/ obsoleta)")
    logger.info("Available endpoints:")
    logger.info("  - GET  /health")
    logger.info("  - GET  /docs")
    logger.info("  - POST /api/auth/login")
    logger.info("  - POST /api/auth/logout")
    logger.info("  - GET  /api/auth/me")
    logger.info("  - POST /api/auth/refresh")
    logger.info("  - GET  /api/trading/status")
    logger.info("  - POST /api/trading/start")
    logger.info("  - POST /api/trading/stop")
    logger.info("  - GET  /api/trading/history")
    logger.info("  - GET  /api/trading/positions")
    logger.info("  - GET  /api/system/status")
    logger.info("  - GET  /api/system/metrics")
    logger.info("  - GET  /api/system/logs")
    logger.info("  - GET  /api/user/profile")
    logger.info("  - PUT  /api/user/settings")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info",
        access_log=True
    )

# Endpoint de métricas Prometheus
@app.get("/metrics")
async def metrics():
    """Endpoint de métricas Prometheus"""
    try:
        if METRICS_AVAILABLE:
            from fastapi import Response
            return Response(
                content=get_prometheus_metrics(),
                media_type=CONTENT_TYPE_LATEST
            )
        else:
            return {"error": "Metrics not available"}
    except Exception as e:
        print(f"Erro no endpoint de métricas: {e}")
        return {"error": str(e)}

@app.get("/api/system/metrics")
async def system_metrics():
    """Endpoint de métricas do sistema"""
    try:
        if METRICS_AVAILABLE:
            return metrics_collector.get_metrics_summary()
        else:
            return {"error": "Metrics not available"}
    except Exception as e:
        return {"error": str(e)}
