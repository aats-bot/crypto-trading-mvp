from __future__ import annotations
from typing import Dict, Any, Optional

from .trading_bot import TradingBot
from .risk_manager import RiskManager


class TradingWorker:
    """
    Gerenciador de bots por cliente.
    - add_client_bot: adiciona/atualiza bot de um cliente
    - remove_client_bot: remove (e tenta parar) o bot do cliente
    - get_status: retorna visão geral, incluindo total_clients
    - get_bot_status: status de um cliente específico
    - start_bot/stop_bot: controla a execução do bot
    """
    def __init__(self) -> None:
        self.client_bots: Dict[int, TradingBot] = {}

    async def add_client_bot(
        self,
        client_config: Dict[str, Any],
        bybit_provider=None,
        risk_manager: Optional[RiskManager] = None,
    ) -> bool:
        client_id = int(client_config.get("client_id", 0))
        if client_id == 0:
            # garante um id válido se não vier
            client_id = max(self.client_bots.keys(), default=0) + 1
            client_config["client_id"] = client_id

        bot = TradingBot(
            client_config=client_config,
            bybit_provider=bybit_provider,
            risk_manager=risk_manager or RiskManager(),
        )
        self.client_bots[client_id] = bot
        return True

    async def remove_client_bot(self, client_id: int) -> bool:
        """
        Remove o bot do cliente (se existir) e tenta pará-lo de forma graciosa.
        """
        cid = int(client_id)
        bot = self.client_bots.pop(cid, None)
        if bot:
            try:
                await bot.stop()
            except Exception:
                # não falhar se o stop levantar erro
                pass
        return True

    async def get_status(self) -> Dict[str, Any]:
        """
        Estrutura esperada nos testes:
        {
          "active_bots": int,
          "total_clients": int,
          "clients": {
              <client_id>: {
                  "running": bool,
                  "strategy": str | None,
                  "symbols": list[str]
              }, ...
          }
        }
        """
        total = len(self.client_bots)
        active = sum(1 for b in self.client_bots.values() if getattr(b, "is_running", False))
        clients = {
            cid: {
                "running": getattr(bot, "is_running", False),
                "strategy": bot.client_config.get("strategy"),
                "symbols": bot.client_config.get("symbols", []),
            }
            for cid, bot in self.client_bots.items()
        }
        return {"active_bots": active, "total_clients": total, "clients": clients}

    async def get_bot_status(self, client_id: int) -> Dict[str, Any]:
        cid = int(client_id)
        bot = self.client_bots.get(cid)
        if not bot:
            return {"client_id": cid, "status": "stopped", "positions": [], "daily_pnl": 0.0}
        return {
            "client_id": cid,
            "status": "running" if getattr(bot, "is_running", False) else "stopped",
            "positions": [],
            "daily_pnl": 0.0,
            "strategy": bot.client_config.get("strategy"),
        }

    async def start_bot(self, client_id: int) -> bool:
        cid = int(client_id)
        bot = self.client_bots.get(cid)
        if not bot:
            # cria sob demanda com config mínima
            bot = TradingBot(
                client_config={"client_id": cid, "symbols": []},
                bybit_provider=None,
                risk_manager=RiskManager(),
            )
            self.client_bots[cid] = bot
        await bot.start()
        return True

    async def stop_bot(self, client_id: int) -> bool:
        cid = int(client_id)
        bot = self.client_bots.get(cid)
        if not bot:
            return True
        await bot.stop()
        return True

    async def get_positions(self, client_id: int):
        """
        Implementação mockada — os testes normalmente fazem patch desse método.
        """
        return []
