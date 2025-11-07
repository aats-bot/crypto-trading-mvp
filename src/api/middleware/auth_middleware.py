# 🔐 Middleware de Autenticação - API
"""
Middleware para autenticação JWT e controle de acesso
Localização: /src/api/middleware/auth_middleware.py
"""
import jwt
from fastapi import HTTPException, Depends, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
import logging
from datetime import datetime, timedelta, UTC
import asyncio
from functools import wraps

from config.environments import current_config
from src.models.client import Client
from src.models.database import get_db_session


logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)


class AuthMiddleware:
    """Middleware principal de autenticação"""
    
    def __init__(self):
        self.secret_key = current_config.SECRET_KEY
        self.algorithm = "HS256"
        self.token_expiration = current_config.JWT_EXPIRATION_HOURS
        self.active_tokens = set()  # Cache de tokens ativos
        
    async def __call__(self, request: Request, call_next):
        """Processa requisição com autenticação"""
        
        # Pular autenticação para endpoints públicos
        if self._is_public_endpoint(request.url.path):
            return await call_next(request)
        
        # Extrair token do header
        token = self._extract_token(request)
        
        if not token:
            # Endpoints que requerem autenticação
            if self._requires_auth(request.url.path):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token de acesso requerido",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        else:
            # Verificar e validar token
            try:
                payload = self._verify_token(token)
                request.state.user_id = payload.get("sub")
                request.state.client_id = payload.get("client_id")
                request.state.token = token
                
                # Adicionar token aos ativos
                self.active_tokens.add(token)
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Erro na verificação do token: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token inválido",
                )
        
        return await call_next(request)
    
    def _is_public_endpoint(self, path: str) -> bool:
        """Verifica se endpoint é público"""
        public_endpoints = [
            "/",
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/api/auth/register",
            "/api/auth/login",
            "/metrics",
        ]
        
        return any(path.startswith(endpoint) for endpoint in public_endpoints)
    
    def _requires_auth(self, path: str) -> bool:
        """Verifica se endpoint requer autenticação"""
        auth_required_patterns = [
            "/api/clients/",
            "/api/trading/",
        ]
        
        return any(path.startswith(pattern) for pattern in auth_required_patterns)
    
    def _extract_token(self, request: Request) -> Optional[str]:
        """Extrai token do header Authorization"""
        auth_header = request.headers.get("Authorization")
        
        if not auth_header:
            return None
        
        try:
            scheme, token = auth_header.split()
            if scheme.lower() != "bearer":
                return None
            return token
        except ValueError:
            return None
    
    def _verify_token(self, token: str) -> Dict[str, Any]:
        """Verifica e decodifica token JWT"""
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            
            # Verificar expiração
            exp = payload.get("exp")
            if exp and datetime.now(UTC).timestamp() > exp:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token expirado",
                )
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expirado",
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
            )
    
    def create_access_token(self, client_id: int, email: str) -> str:
        """Cria token de acesso JWT"""
        now = datetime.now(UTC)
        expire = now + timedelta(hours=self.token_expiration)
        
        payload = {
            "sub": str(client_id),
            "client_id": client_id,
            "email": email,
            "iat": now.timestamp(),
            "exp": expire.timestamp(),
            "type": "access_token"
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        self.active_tokens.add(token)
        
        return token
    
    def revoke_token(self, token: str) -> bool:
        """Revoga token (adiciona à blacklist)"""
        try:
            self.active_tokens.discard(token)
            return True
        except Exception as e:
            logger.error(f"Erro ao revogar token: {str(e)}")
            return False
    
    def is_token_active(self, token: str) -> bool:
        """Verifica se token está ativo"""
        return token in self.active_tokens


# Instância global do middleware
auth_middleware = AuthMiddleware()


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[Client]:
    """
    Dependency para obter usuário atual autenticado
    
    Returns:
        Client object se autenticado, None caso contrário
    """
    if not credentials:
        return None
    
    try:
        payload = auth_middleware._verify_token(credentials.credentials)
        client_id = payload.get("client_id")
        
        if not client_id:
            return None
        
        # Buscar cliente no banco de dados
        async with get_db_session() as session:
            client = await session.get(Client, client_id)
            return client
            
    except HTTPException:
        return None
    except Exception as e:
        logger.error(f"Erro ao obter usuário atual: {str(e)}")
        return None


async def require_auth(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Client:
    """
    Dependency que requer autenticação obrigatória
    
    Returns:
        Client object
        
    Raises:
        HTTPException se não autenticado
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de acesso requerido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        payload = auth_middleware._verify_token(credentials.credentials)
        client_id = payload.get("client_id")
        
        if not client_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
            )
        
        # Buscar cliente no banco de dados
        async with get_db_session() as session:
            client = await session.get(Client, client_id)
            
            if not client:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Cliente não encontrado",
                )
            
            return client
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro na autenticação obrigatória: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno de autenticação",
        )


def verify_token(token: str) -> Dict[str, Any]:
    """
    Verifica token JWT de forma síncrona
    
    Args:
        token: Token JWT para verificar
        
    Returns:
        Payload do token decodificado
        
    Raises:
        HTTPException se token inválido
    """
    return auth_middleware._verify_token(token)


def create_access_token(client_id: int, email: str) -> str:
    """
    Cria token de acesso para cliente
    
    Args:
        client_id: ID do cliente
        email: Email do cliente
        
    Returns:
        Token JWT
    """
    return auth_middleware.create_access_token(client_id, email)


def revoke_token(token: str) -> bool:
    """
    Revoga token de acesso
    
    Args:
        token: Token para revogar
        
    Returns:
        True se revogado com sucesso
    """
    return auth_middleware.revoke_token(token)


class TokenManager:
    """Gerenciador avançado de tokens"""
    
    def __init__(self):
        self.blacklisted_tokens = set()
        self.refresh_tokens = {}
        
    def blacklist_token(self, token: str) -> None:
        """Adiciona token à blacklist"""
        self.blacklisted_tokens.add(token)
        auth_middleware.active_tokens.discard(token)
    
    def is_blacklisted(self, token: str) -> bool:
        """Verifica se token está na blacklist"""
        return token in self.blacklisted_tokens
    
    def create_refresh_token(self, client_id: int) -> str:
        """Cria token de refresh"""
        now = datetime.now(UTC)
        expire = now + timedelta(days=30)  # Refresh token válido por 30 dias
        
        payload = {
            "sub": str(client_id),
            "client_id": client_id,
            "iat": now.timestamp(),
            "exp": expire.timestamp(),
            "type": "refresh_token"
        }
        
        refresh_token = jwt.encode(
            payload,
            current_config.SECRET_KEY,
            algorithm="HS256"
        )
        
        self.refresh_tokens[client_id] = refresh_token
        return refresh_token
    
    def verify_refresh_token(self, refresh_token: str) -> Optional[int]:
        """Verifica token de refresh e retorna client_id"""
        try:
            payload = jwt.decode(
                refresh_token,
                current_config.SECRET_KEY,
                algorithms=["HS256"]
            )
            
            if payload.get("type") != "refresh_token":
                return None
            
            client_id = payload.get("client_id")
            
            # Verificar se refresh token ainda é válido
            if client_id in self.refresh_tokens:
                if self.refresh_tokens[client_id] == refresh_token:
                    return client_id
            
            return None
            
        except jwt.InvalidTokenError:
            return None


# Instância global do gerenciador de tokens
token_manager = TokenManager()


def auth_required(f):
    """
    Decorator para funções que requerem autenticação
    
    Usage:
        @auth_required
        def protected_function(client: Client):
            pass
    """
    @wraps(f)
    async def wrapper(*args, **kwargs):
        # Extrair cliente dos argumentos
        client = None
        for arg in args:
            if isinstance(arg, Client):
                client = arg
                break
        
        if not client:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Autenticação requerida",
            )
        
        return await f(*args, **kwargs)
    
    return wrapper


def admin_required(f):
    """
    Decorator para funções que requerem privilégios de admin
    (Para implementação futura)
    """
    @wraps(f)
    async def wrapper(*args, **kwargs):
        # Implementar lógica de admin no futuro
        return await f(*args, **kwargs)
    
    return wrapper


class SessionManager:
    """Gerenciador de sessões de usuário"""
    
    def __init__(self):
        self.active_sessions = {}  # client_id -> session_info
        
    def create_session(self, client_id: int, token: str) -> str:
        """Cria nova sessão para cliente"""
        session_id = f"session_{client_id}_{datetime.now(UTC).timestamp()}"
        
        self.active_sessions[client_id] = {
            "session_id": session_id,
            "token": token,
            "created_at": datetime.now(UTC),
            "last_activity": datetime.now(UTC),
            "ip_address": None,  # Será preenchido pelo middleware
            "user_agent": None,  # Será preenchido pelo middleware
        }
        
        return session_id
    
    def update_activity(self, client_id: int) -> None:
        """Atualiza última atividade da sessão"""
        if client_id in self.active_sessions:
            self.active_sessions[client_id]["last_activity"] = datetime.now(UTC)
    
    def end_session(self, client_id: int) -> bool:
        """Encerra sessão do cliente"""
        if client_id in self.active_sessions:
            session_info = self.active_sessions.pop(client_id)
            # Revogar token associado
            auth_middleware.revoke_token(session_info["token"])
            return True
        return False
    
    def get_active_sessions(self) -> Dict[int, Dict[str, Any]]:
        """Retorna todas as sessões ativas"""
        return self.active_sessions.copy()
    
    def cleanup_expired_sessions(self) -> int:
        """Remove sessões expiradas"""
        now = datetime.now(UTC)
        expired_sessions = []
        
        for client_id, session_info in self.active_sessions.items():
            last_activity = session_info["last_activity"]
            if (now - last_activity).total_seconds() > 3600:  # 1 hora de inatividade
                expired_sessions.append(client_id)
        
        for client_id in expired_sessions:
            self.end_session(client_id)
        
        return len(expired_sessions)


# Instância global do gerenciador de sessões
session_manager = SessionManager()


# Exportar funções e classes principais
__all__ = [
    "AuthMiddleware",
    "auth_middleware",
    "get_current_user",
    "require_auth",
    "verify_token",
    "create_access_token",
    "revoke_token",
    "TokenManager",
    "token_manager",
    "auth_required",
    "admin_required",
    "SessionManager",
    "session_manager",
]

