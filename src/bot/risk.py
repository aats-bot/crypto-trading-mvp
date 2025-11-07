# src/bot/risk.py
from __future__ import annotations
from typing import Any, Dict


class RiskManager:
    """
    Implementação simples de gerenciador de risco usada pelos testes.
    Expõe métodos:
      - get_risk_parameters()
      - update_risk_parameters(...)
      - assess_risk(balance, price, volatility=0.0)
      - compute_position_size(balance, price)
    """

    def __init__(self, params: Dict[str, Any] | None = None) -> None:
        defaults: Dict[str, Any] = {
            "risk_per_trade": 0.01,     # 1% do saldo por trade
            "max_position_size": 1000.0,  # valor máximo em USD por posição
            "stop_loss_pct": 0.02,      # 2%
            "take_profit_pct": 0.04,    # 4%
        }
        self._params: Dict[str, Any] = {**defaults, **(params or {})}

    def get_risk_parameters(self) -> Dict[str, Any]:
        return dict(self._params)

    def update_risk_parameters(self, new_params: Dict[str, Any] | None = None) -> None:
        if new_params:
            self._params.update(new_params)

    def compute_position_size(self, balance: float, price: float) -> float:
        """
        Calcula um tamanho de posição simples limitado tanto por risco
        quanto por tamanho máximo configurado.
        """
        if price <= 0:
            return 0.0

        # limite por tamanho máximo em USD
        max_qty = float(self._params["max_position_size"]) / float(price)

        # limite por risco (% do balance dividido pela perda por stop)
        risk_amount = float(balance) * float(self._params["risk_per_trade"])
        stop_loss_pct = float(self._params["stop_loss_pct"]) or 1.0
        # perda por unidade ~ price * stop_loss_pct
        qty_by_risk = risk_amount / (float(price) * stop_loss_pct)

        qty = min(max_qty, qty_by_risk)
        return float(max(0.0, qty))

    def assess_risk(self, balance: float, price: float, volatility: float = 0.0) -> Dict[str, float]:
        """
        Retorna parâmetros básicos de risco para uma entrada simulada.
        """
        pos_size = self.compute_position_size(balance, price)
        sl = float(price) * (1.0 - float(self._params["stop_loss_pct"]))
        tp = float(price) * (1.0 + float(self._params["take_profit_pct"]))
        return {
            "position_size": float(pos_size),
            "stop_loss": float(sl),
            "take_profit": float(tp),
        }
