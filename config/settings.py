from __future__ import annotations
import os
from pathlib import Path

try:
    # Pydantic v2: BaseSettings foi movido para pydantic-settings
    from pydantic_settings import BaseSettings, SettingsConfigDict
except Exception:  # fallback raro
    from pydantic import BaseSettings  # type: ignore
    class SettingsConfigDict(dict):  # compat ínfima
        pass

# Raiz do projeto (para montar caminhos relativos)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB_PATH = PROJECT_ROOT / "test.db"

class Settings(BaseSettings):
    # Defaults seguros para testes:
    database_url: str = f"sqlite+aiosqlite:///{DEFAULT_DB_PATH.as_posix()}"
    database_url_sync: str = f"sqlite:///{DEFAULT_DB_PATH.as_posix()}"
    debug: bool = False

    # Pydantic Settings config
    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

# Instância global
settings = Settings()
