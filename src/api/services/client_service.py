from __future__ import annotations

from typing import Optional, Dict, Any

class ClientService:
    """
    Service de clientes *minimamente* implementado para os testes.
    Os testes frequentemente fazem patch/mocks desses métodos.
    """

    # -------- Registro --------
    def create_client(self, email: str, password: str, bybit_api_key: str, bybit_api_secret: str):
        """
        Retorne um objeto com 'id' e 'email'.
        Em produção você conectaria DB; nos testes isso é mockado.
        """
        class _Client:
            def __init__(self, id_: int, email_: str):
                self.id = id_
                self.email = email_
        return _Client(1, email)

    # -------- Autenticação --------
    def authenticate_client(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Deve retornar dict com {client_id, token, expires_in} ou None.
        Nos testes, este método é patchado.
        """
        if username and password:
            return {"client_id": 1, "token": "dummy", "expires_in": 3600}
        return None

    # -------- Trading config --------
    def update_trading_config(self, client_id: int, config: Dict[str, Any]) -> bool:
        """
        Retorna True/False. Testes patcham este método.
        """
        return True
