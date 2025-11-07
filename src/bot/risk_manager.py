from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from .interfaces import (
    OrderRequest,
    OrderSide,
    Position,
    PositionSide,
    MarketData,
)


class RiskManager:
    """
    Implementação mínima compatível com os testes.

    - Atributos públicos:
        max_position_size, max_daily_loss, max_open_positions, risk_per_trade
        daily_loss, daily_trades
    - Construtor aceita dict opcional com overrides.
    - validate_order é assíncrono.
    - Métodos de cálculo: calculate_position_size, calculate_stop_loss, calculate_take_profit
    - Limites diários: check_daily_limits, update_daily_loss, reset_daily_stats
    """

    def __init__(self, config: Optional[Dict] = None) -> None:
        cfg = config or {}
        self.max_position_size: float = float(cfg.get("max_position_size", 1000.0))  # nocional (USDT)
        self.max_daily_loss: float = float(cfg.get("max_daily_loss", 100.0))
        self.max_open_positions: int = int(cfg.get("max_open_positions", 5))
        self.risk_per_trade: float = float(cfg.get("risk_per_trade", 0.02))

        # estatísticas/dia
        self.daily_loss: float = 0.0
        self.daily_trades: List[Dict] = []  # [{"timestamp": datetime, "pnl": float}, ...]

    # ---------- getters/updates ----------
    def get_max_position_size(self) -> float:
        return self.max_position_size

    def update_risk_parameters(self, params: Dict) -> None:
        if "max_position_size" in params:
            self.max_position_size = float(params["max_position_size"])
        if "max_daily_loss" in params:
            self.max_daily_loss = float(params["max_daily_loss"])
        if "max_open_positions" in params:
            self.max_open_positions = int(params["max_open_positions"])
        if "risk_per_trade" in params:
            self.risk_per_trade = float(params["risk_per_trade"])

    # ---------- validações principais ----------
    async def validate_order(
        self,
        order_request: OrderRequest,
        positions: List[Position],
        account_balance: Dict[str, float],
        market_data: MarketData,
    ) -> bool:
        # 1) limite de perda diária
        if self.daily_loss > self.max_daily_loss:
            return False

        # 2) limite de quantidade de posições
        if len(positions) >= self.max_open_positions:
            return False

        # 3) saldo suficiente
        usdt = float(account_balance.get("USDT", 0.0))
        notional = float(order_request.quantity) * float(market_data.price)
        if usdt < notional:
            return False

        # 4) risco por trade (orçamento máximo)
        budget_by_risk = usdt * self.risk_per_trade
        # 5) limite de tamanho máximo por posição (nocional)
        budget_by_cap = self.max_position_size
        max_budget = min(budget_by_risk, budget_by_cap)
        if notional > max_budget:
            return False

        return True

    # ---------- cálculos ----------
    def calculate_position_size(self, account_balance: Dict[str, float], current_price: float) -> float:
        if current_price <= 0:
            return 0.0
        usdt = float(account_balance.get("USDT", 0.0))
        budget_by_risk = usdt * self.risk_per_trade
        budget = min(budget_by_risk, self.max_position_size)  # respeita o teto nocional
        size = budget / current_price
        return max(0.0, size)

    def calculate_stop_loss(self, entry_price: float, side: PositionSide, stop_loss_pct: float) -> float:
        if side == PositionSide.LONG:
            return entry_price * (1.0 - stop_loss_pct)
        return entry_price * (1.0 + stop_loss_pct)

    def calculate_take_profit(self, entry_price: float, side: PositionSide, take_profit_pct: float) -> float:
        if side == PositionSide.LONG:
            return entry_price * (1.0 + take_profit_pct)
        return entry_price * (1.0 - take_profit_pct)

    # ---------- limites diários ----------
    async def check_daily_limits(self) -> bool:
        """Retorna True se ainda está dentro do limite diário de perda."""
        return self.daily_loss <= self.max_daily_loss

    def update_daily_loss(self, pnl: float) -> None:
        """
        Atualiza a métrica de 'daily_loss' com base no PnL de um trade/ciclo.
        Convenção:
          - pnl < 0 (perda): aumenta daily_loss pelo valor absoluto da perda
          - pnl > 0 (lucro): reduz daily_loss até o mínimo zero
        Também registra o evento em 'daily_trades'.
        """
        if pnl < 0:
            self.daily_loss += abs(pnl)
        elif pnl > 0:
            self.daily_loss = max(0.0, self.daily_loss - pnl)

        self.daily_trades.append({"timestamp": datetime.now(), "pnl": float(pnl)})

    def reset_daily_stats(self) -> None:
        self.daily_loss = 0.0
        self.daily_trades.clear()
