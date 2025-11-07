from __future__ import annotations
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime

class DatabaseManager:
    def __init__(self) -> None:
        self._users: Dict[int, Dict[str, Any]] = {}
        self._next_uid = 1

        # (symbol, interval) -> list[dict]
        self._market: Dict[Tuple[str, str], List[Dict[str, Any]]] = {}

        self._logs: List[Dict[str, Any]] = []
        self._next_log_id = 1

    # -------- users --------
    async def create_user(self, username: str, email: str, password_hash: str) -> Dict[str, Any]:
        uid = self._next_uid
        self._next_uid += 1
        rec = {"id": uid, "username": username, "email": email, "password_hash": password_hash}
        self._users[uid] = rec
        return rec

    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        return self._users.get(int(user_id))

    # -------- market data --------
    async def store_market_data(self, symbol: str, interval: str, candles: List[Dict[str, Any]]) -> int:
        key = (symbol, interval)
        buf = self._market.setdefault(key, [])
        for c in candles:
            buf.append({
                "timestamp": int(c["timestamp"]),
                "open": float(c["open"]),
                "high": float(c["high"]),
                "low": float(c["low"]),
                "close": float(c["close"]),  # os testes verificam esta chave
                "volume": float(c.get("volume", 0.0)),
            })
        return len(candles)

    async def get_market_data(self, symbol: str, interval: str, limit: int = 100) -> List[Dict[str, Any]]:
        key = (symbol, interval)
        data = sorted(self._market.get(key, []), key=lambda x: x["timestamp"], reverse=True)
        return data[:limit]

    # -------- logging --------
    async def log_message(self, level: str, message: str, source: str,
                          user_id: Optional[int] = None, extra: Optional[Dict[str, Any]] = None) -> int:
        lid = self._next_log_id
        self._next_log_id += 1
        rec = {
            "id": lid,
            "level": level,
            "message": message,
            "source": source,
            "user_id": user_id,
            "extra": extra or {},
            "created_at": datetime.utcnow().isoformat(),
        }
        self._logs.append(rec)
        return lid

    async def get_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        # mais recente primeiro (ids crescentes)
        ordered = sorted(self._logs, key=lambda r: r["id"], reverse=True)
        return ordered[:limit]
