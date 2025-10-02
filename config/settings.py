# config/settings.py
from __future__ import annotations

try:
    # Pydantic v2
    from pydantic_settings import BaseSettings, SettingsConfigDict
    _V2 = True
except Exception:  # fallback p/ v1 se alguém trocar a versão
    from pydantic import BaseSettings  # type: ignore
    SettingsConfigDict = None  # type: ignore
    _V2 = False


class Settings(BaseSettings):
    """
    Centraliza variáveis de ambiente. Mantemos 'extra=allow' para não quebrar
    caso existam novas chaves no .env que o modelo não declare.
    Adicione aqui os campos que o projeto usar explicitamente, ex.:
      bybit_api_key: str | None = None
      bybit_api_secret: str | None = None
      database_url: str | None = None
    """
    if _V2:
        model_config = SettingsConfigDict(env_file=".env", extra="allow")
    else:  # pydantic v1
        class Config:
            env_file = ".env"
            extra = "allow"


settings = Settings()
