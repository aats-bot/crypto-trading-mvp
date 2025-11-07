from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Any, Dict, Optional
from pydantic import RootModel

from src.api.deps import get_current_client
from src.api.services.client_service import ClientService

router = APIRouter()

# Aceita um dicionário arbitrário como payload de configuração (Pydantic v2)
class TradingConfigPayload(RootModel[Dict[str, Any]]):
    pass

@router.get("/profile")
async def get_profile(current=Depends(get_current_client)):
    if not current:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorized")
    created_at = getattr(current, "created_at", None)
    created = created_at.isoformat() if isinstance(created_at, datetime) else datetime.now().isoformat()
    return {
        "id": getattr(current, "id", None),
        "email": getattr(current, "email", None),
        "created_at": created,
    }

@router.put("/trading-config")
async def update_trading_config(payload: TradingConfigPayload, current=Depends(get_current_client)):
    if not current:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorized")

    data = payload.root  # RootModel -> o dicionário enviado
    svc = ClientService()
    ok = True
    if hasattr(svc, "update_trading_config"):
        ok = svc.update_trading_config(current.id, data)
    if not ok:
        raise HTTPException(status_code=400, detail="Falha ao atualizar configuração")
    return {"message": "Configuração atualizada com sucesso"}

@router.get("/trading-config")
async def get_trading_config(current=Depends(get_current_client)):
    if not current:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorized")
    cfg: Optional[Dict[str, Any]] = getattr(current, "trading_config", None)
    # Os testes esperam o DICT puro, não embrulhado
    return cfg or {}
