# AUTOGERADO por quick_fix.py
from __future__ import annotations
from typing import Optional, List, Dict

class RiskManager:
    def __init__(self, config: Optional[dict] = None):
        cfg = config or {}
        self.max_position_size: float = float(cfg.get("max_position_size", 1000.0))
        self.max_daily_loss: float = float(cfg.get("max_daily_loss", 100.0))
        self.max_open_positions: int = int(cfg.get("max_open_positions", 5))
        self.risk_per_trade: float = float(cfg.get("risk_per_trade", 0.02))
        self._daily_pnl: float = 0.0

    def get_max_position_size(self) -> float:
        return self.max_position_size

    def update_daily_pnl(self, delta: float):
        self._daily_pnl += float(delta)

    def reset_daily(self):
        self._daily_pnl = 0.0

    def check_position_limits(self, open_positions: List[dict]) -> bool:
        return len(open_positions) < self.max_open_positions

    def calculate_position_size(self, balance: float, price: float) -> float:
        if price <= 0:
            return 0.0
        size_by_risk = (balance * self.risk_per_trade) / price
        return max(0.0, min(size_by_risk, self.max_position_size))

    def validate_order(self, side: str, balance: float, price: float, open_positions: List[dict]) -> Dict[str, object]:
        if self._daily_pnl <= -abs(self.max_daily_loss):
            return {"valid": False, "reason": "daily_loss_exceeded"}
        if not self.check_position_limits(open_positions):
            return {"valid": False, "reason": "too_many_positions"}
        size = self.calculate_position_size(balance, price)
        if size <= 0:
            return {"valid": False, "reason": "insufficient_balance"}
        return {"valid": True, "size": size}

class RiskManager:
    def __init__(self, config: dict | None = None):
        cfg = config or {}
        self.max_position_size = float(cfg.get("max_position_size", 1000.0))
        self.max_daily_loss = float(cfg.get("max_daily_loss", 100.0))
        self.max_open_positions = int(cfg.get("max_open_positions", 5))
        self.risk_per_trade = float(cfg.get("risk_per_trade", 0.01))
        self.daily_loss = 0.0

    def get_max_position_size(self):
        return self.max_position_size

    def calculate_position_size(self, price: float, stop_loss: float, risk_amount: float):
        if price <= 0:
            return 0.0
        # tamanho = risco_em_$ / (distância SL)
        dist = abs(stop_loss)
        dist = dist if dist > 1e-9 else max(price*0.005, 1e-6)
        size = risk_amount / dist
        return min(size, self.max_position_size)

    def check_position_limits(self, open_positions: list) -> bool:
        return len(open_positions) < self.max_open_positions

    def validate_order(self, balance: float, price: float, size: float, side: str):
        cost = abs(size) * price
        if cost > balance:
            raise ValueError("Saldo insuficiente")
        if abs(size) > self.max_position_size:
            raise ValueError("Tamanho de posição excede o máximo")
        return True

    def check_daily_limits(self) -> bool:
        return self.daily_loss <= self.max_daily_loss

    def update_daily_loss(self, pnl: float):
        # pnl negativo aumenta perda diária
        if pnl < 0:
            self.daily_loss += abs(pnl)
        return self.daily_loss

    def reset_daily_stats(self):
        self.daily_loss = 0.0

    def calculate_stop_loss(self, entry_price: float, side: str, atr: float | None = None):
        atr = atr or entry_price * 0.005
        return entry_price - atr if side.lower() in ("long","buy") else entry_price + atr

    def calculate_take_profit(self, entry_price: float, side: str, rr: float = 2.0, atr: float | None = None):
        sl = self.calculate_stop_loss(entry_price, side, atr)
        dist = abs(entry_price - sl) * rr
        return entry_price + dist if side.lower() in ("long","buy") else entry_price - dist

    def get_risk_parameters(self):
        return {
            "max_position_size": self.max_position_size,
            "max_daily_loss": self.max_daily_loss,
            "max_open_positions": self.max_open_positions,
            "risk_per_trade": self.risk_per_trade,
        }

    def update_risk_parameters(self, params: dict | None = None):
        p = params or {}
        if "max_position_size" in p: self.max_position_size = float(p["max_position_size"])
        if "max_daily_loss" in p: self.max_daily_loss = float(p["max_daily_loss"])
        if "max_open_positions" in p: self.max_open_positions = int(p["max_open_positions"])
        if "risk_per_trade" in p: self.risk_per_trade = float(p["risk_per_trade"])
        return self.get_risk_parameters()
