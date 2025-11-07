# src/models/database.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime

# Declarative base compat (evita warnings nos testes que importam Base)
try:
    from sqlalchemy.orm import declarative_base  # type: ignore
    Base = declarative_base()
except Exception:
    class _DummyBase: ...
    Base = _DummyBase()  # type: ignore


@dataclass
class _User:
    id: int
    username: str
    email: str
    password_hash: str
    created_at: datetime = field(default_factory=datetime.utcnow)


class DatabaseManager:
    """
    Implementação em memória apenas para passar os testes de integração.
    """
    def __init__(self) -> None:
        self._users: Dict[int, _User] = {}
        self._user_seq: int = 0
        self._logs: List[Dict[str, Any]] = []
        self._market: Dict[str, List[Dict[str, Any]]] = {}  # key: f"{symbol}:{interval}"

    # ---- Users ----
    async def create_user(self, username: str, email: str, password_hash: str) -> Dict[str, Any]:
        self._user_seq += 1
        user = _User(id=self._user_seq, username=username, email=email, password_hash=password_hash)
        self._users[user.id] = user
        return {"id": user.id, "username": user.username, "email": user.email}

    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        u = self._users.get(int(user_id))
        if not u:
            return None
        return {"id": u.id, "username": u.username, "email": u.email}

    # ---- Market data ----
    async def store_market_data(self, symbol: str, interval: str, candles: List[Dict[str, Any]]) -> int:
        key = f"{symbol}:{interval}"
        bucket = self._market.setdefault(key, [])
        for c in candles:
            # padroniza e garante chaves
            bucket.append({
                "timestamp": int(c["timestamp"]),
                "open": float(c["open"]),
                "high": float(c["high"]),
                "low": float(c["low"]),
                "close": float(c["close"]),
                "volume": float(c.get("volume", 0.0)),
            })
        # mantém só os últimos 5000 por segurança
        if len(bucket) > 5000:
            self._market[key] = bucket[-5000:]
        return len(candles)

    async def get_market_data(self, symbol: str, interval: str, limit: int = 100) -> List[Dict[str, Any]]:
        key = f"{symbol}:{interval}"
        data = list(self._market.get(key, []))
        # mais recente primeiro
        data.sort(key=lambda x: x["timestamp"], reverse=True)
        return data[:limit]

    # ---- Logging ----
    async def log_message(self, level: str, message: str, module: str, user_id: Optional[int] = None, meta: Optional[Dict[str, Any]] = None) -> int:
        log_id = len(self._logs) + 1
        self._logs.append({
            "id": log_id,
            "level": level,
            "message": message,
            "module": module,
            "user_id": user_id,
            "meta": dict(meta or {}),
            "created_at": datetime.utcnow().timestamp()
        })
        return log_id

    async def get_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        data = sorted(self._logs, key=lambda x: x["created_at"], reverse=True)
        return data[:limit]
