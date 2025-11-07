from fastapi import FastAPI
from datetime import datetime, timezone

from src.api.routes.auth import router as auth_router
from src.api.routes.clients import router as clients_router
from src.api.routes.trading import router as trading_router

app = FastAPI(title="Crypto Trading API")

# Routers
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(clients_router, prefix="/api/clients", tags=["clients"])
app.include_router(trading_router, prefix="/api/trading", tags=["trading"])
app.include_router(trading_router, prefix="/trading", tags=["trading-compat"])

@app.get("/")
def root():
    return {
        "message": "Crypto Trading API",
        "status": "ok",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
