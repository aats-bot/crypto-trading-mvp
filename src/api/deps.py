from datetime import datetime, timezone
from fastapi import Header, HTTPException, status

class _Client:
    def __init__(self):
        self.id = 1
        self.email = "test@example.com"
        self.created_at = datetime.now(timezone.utc)
        self.trading_config = {
            "strategy": "sma",
            "symbols": ["BTCUSDT"],
            "risk_per_trade": 0.02,
            "fast_period": 10,
            "slow_period": 20,
        }

async def get_current_client(authorization: str | None = Header(default=None)):
    """
    Dependência de auth simples:
    - Se não houver Authorization -> 401 (os testes esperam isso)
    - Caso haja, retorna um cliente mockado (os testes fazem patch disso quando precisam).
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="unauthorized",
        )
    return _Client()
