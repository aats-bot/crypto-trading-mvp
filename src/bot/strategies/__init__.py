"""# src/bot/strategies/__init__.py
Trading strategies module
"""
from .ppp_vishva_strategy import PPPVishvaStrategy
from __future__ import annotations
from importlib import import_module
from pathlib import Path
from types import ModuleType
from typing import Any, Dict

_REGISTRY: Dict[str, Any] = {}
_PKG_NAME = __name__
_DIR = Path(__file__).parent

def _load_strategy_from_module(mod: ModuleType) -> Any | None:
    """
    Convenções aceitas:
      - classe 'Strategy'
      - função 'get_strategy()' que retorna a instância/cls
      - variável 'STRATEGY'
    """
    if hasattr(mod, "get_strategy") and callable(mod.get_strategy):
        return mod.get_strategy()
    for name in ("Strategy", "STRATEGY", "strategy"):
        if hasattr(mod, name):
            return getattr(mod, name)
    return None

def _discover() -> None:
    for py in _DIR.glob("*.py"):
        if py.name in ("__init__.py", "base.py"):
            continue
        mod_name = f"{_PKG_NAME}.{py.stem}"
        try:
            mod = import_module(mod_name)
            obj = _load_strategy_from_module(mod)
            if obj is not None:
                _REGISTRY[py.stem] = obj
        except Exception:
            # não quebra import de pacote se uma estratégia falhar
            continue

_discover()

def get_available_strategies() -> list[str]:
    return sorted(_REGISTRY.keys())

def get_strategy(name: str) -> Any:
    if name in _REGISTRY:
        return _REGISTRY[name]
    # tenta lazy-importar se ainda não carregou
    try:
        mod = import_module(f"{_PKG_NAME}.{name}")
        obj = _load_strategy_from_module(mod)
        if obj is not None:
            _REGISTRY[name] = obj
            return obj
    except Exception as exc:
        raise ImportError(f"Strategy '{name}' not found") from exc
    raise ImportError(f"Strategy '{name}' not found")

def get_strategy_info(name: str) -> dict:
    s = get_strategy(name)
    desc = getattr(s, "__doc__", "") or getattr(s, "description", "") or ""
    return {"name": name, "description": desc}


__all__ = ['PPPVishvaStrategy']
