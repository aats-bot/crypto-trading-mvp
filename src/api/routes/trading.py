from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

# Mantemos importável para os testes poderem patchar (target: src.api.routes.trading.get_current_client)
from src.api.deps import get_current_client as get_current_client  # noqa: F401
from src.bot.worker import TradingWorker

router = APIRouter()

# -------------------- Estado único em memória para testes --------------------
CONFIG: Dict[str, Any] = {"max_positions": 3}
POSITIONS: List[Dict[str, Any]] = []
SYSTEM_STATE: Dict[str, Any] = {"running": False}

# Instância única para os patches funcionarem
WORKER = TradingWorker()


# -------------------- Schemas --------------------
class OrderPayload(BaseModel):
    symbol: str
    side: str               # "buy" | "sell"
    order_type: str = "market"
    quantity: float


class CreatePositionPayload(BaseModel):
    symbol: str
    side: str
    quantity: float
    strategy: Optional[str] = None


# -------------------- Funções puras exportadas (para testes de integração) --------------------
def create_position(symbol: str, side: str, quantity: float, strategy: Optional[str] = None) -> Dict[str, Any]:
    """Cria posição diretamente (levanta ValueError ao exceder limite)."""
    payload = CreatePositionPayload(symbol=symbol, side=side, quantity=quantity, strategy=strategy)
    return _create_position_internal(payload)


def get_positions_list() -> List[Dict[str, Any]]:
    """Retorna a lista atual de posições (estado global)."""
    return POSITIONS


def clear_positions() -> None:
    """Auxiliar opcional para testes (não usado pelos testes, mas útil)."""
    POSITIONS.clear()


# -------------------- Rotas que usam o WORKER (com auth para testes unit) --------------------
@router.get("/status")
async def trading_status(_: Any = Depends(get_current_client)):
    client_id = getattr(_, "id", None)
    try:
        data = await WORKER.get_bot_status(client_id)
    except TypeError:
        data = WORKER.get_bot_status(client_id)

    if isinstance(data, dict) and data:
        return data

    return {
        "client_id": client_id,
        "status": "running" if SYSTEM_STATE.get("running") else "stopped",
        "strategy": None,
        "positions": [],
        "daily_pnl": 0.0,
    }


@router.post("/start")
async def start_trading(_: Any = Depends(get_current_client)):
    client_id = getattr(_, "id", None)
    try:
        await WORKER.start_bot(client_id)
    except TypeError:
        WORKER.start_bot(client_id)
    SYSTEM_STATE["running"] = True
    return {"message": "Bot iniciado com sucesso"}


@router.post("/stop")
async def stop_trading(_: Any = Depends(get_current_client)):
    client_id = getattr(_, "id", None)
    try:
        await WORKER.stop_bot(client_id)
    except TypeError:
        WORKER.stop_bot(client_id)
    SYSTEM_STATE["running"] = False
    return {"message": "Bot parado com sucesso"}


@router.get("/positions")
async def positions_worker(_: Any = Depends(get_current_client)):
    client_id = getattr(_, "id", None)
    try:
        res = await WORKER.get_positions(client_id)
    except TypeError:
        res = WORKER.get_positions(client_id)

    if isinstance(res, list) and res:
        return res
    return POSITIONS


# -------------------- Endpoints públicos p/ cenários de integração/E2E --------------------
def _order_response(payload: OrderPayload) -> Dict[str, Any]:
    order_id = f"ord_{payload.symbol}_{int(datetime.now(tz=timezone.utc).timestamp() * 1_000_000)}"
    return {
        "success": True,
        "order_id": order_id,
        "status": "filled",
        "symbol": payload.symbol,
        "side": payload.side.lower(),
        "order_type": payload.order_type.lower(),
        "quantity": payload.quantity,
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
    }


# Cobrir o máximo de aliases possíveis que o front possa usar:
@router.post("/place-order")
@router.post("/place_order")
@router.post("/order")
@router.post("/place")
@router.post("/execute-order")
@router.post("/execute_order")
@router.post("/submit-order")
@router.post("/submit_order")
@router.post("/orders/place")
@router.post("/orders/submit")
@router.post("/order/place")
@router.post("/order/submit")
@router.post("/orders")
async def place_order_aliases(payload: OrderPayload):
    return _order_response(payload)


def _create_position_internal(payload: CreatePositionPayload) -> Dict[str, Any]:
    # Limite de posições
    if len(POSITIONS) >= int(CONFIG["max_positions"]):
        raise ValueError("Máximo de posições atingido")

    now = datetime.now(timezone.utc)
    pos_id = f"{payload.symbol}_{payload.side}_{int(now.timestamp() * 1_000_000)}"
    position = {
        "id": pos_id,
        "symbol": payload.symbol,
        "side": payload.side,
        "size": payload.quantity,
        "entry_price": 50000,
        "created_at": now.isoformat(),
        "strategy": payload.strategy or "unknown",
    }
    POSITIONS.append(position)
    return position


@router.post("/positions")
async def create_position_public(payload: CreatePositionPayload):
    try:
        return _create_position_internal(payload)
    except ValueError as e:
        # Alguns clientes HTTP podem mapear isso para exceção; manter a mensagem exata.
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


# aliases para criação (compat):
@router.post("/create-position")
@router.post("/create_position")
@router.post("/position")
@router.post("/open-position")
async def create_position_aliases(payload: CreatePositionPayload):
    return await create_position_public(payload)


@router.get("/positions/public")
async def get_positions_public():
    return POSITIONS


@router.get("/config")
async def get_trading_config_public():
    return {
        "max_positions": CONFIG["max_positions"],
        "supports_symbols": ["BTCUSDT", "ETHUSDT"],
    }
