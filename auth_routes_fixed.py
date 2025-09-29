"""
Sistema de autenticação corrigido para resolver erro 500
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from sqlalchemy import text
import bcrypt
import jwt
import datetime
from typing import Optional
import logging
import traceback

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Modelos Pydantic
class UserRegister(BaseModel):
    email: EmailStr
    name: str
    password: str
    bybit_api_key: Optional[str] = ""
    bybit_api_secret: Optional[str] = ""

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    is_active: bool
    created_at: datetime.datetime

# Configurações JWT
JWT_SECRET = "jwt-crypto-trading-mvp-secret-key-2024-very-secure"
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# Security
security = HTTPBearer()

# Router
router = APIRouter(prefix="/api/auth", tags=["authentication"])

def get_database():
    """Simulação de dependência do banco - será substituída pela real"""
    pass

def hash_password(password: str) -> str:
    """Hash da senha usando bcrypt"""
    try:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    except Exception as e:
        logger.error(f"Erro ao fazer hash da senha: {e}")
        raise HTTPException(status_code=500, detail="Erro interno no processamento da senha")

def verify_password(password: str, hashed_password: str) -> bool:
    """Verifica se a senha está correta"""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception as e:
        logger.error(f"Erro ao verificar senha: {e}")
        return False

def create_jwt_token(user_id: str, email: str) -> str:
    """Cria token JWT"""
    try:
        payload = {
            "user_id": user_id,
            "email": email,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=JWT_EXPIRATION_HOURS),
            "iat": datetime.datetime.utcnow()
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return token
    except Exception as e:
        logger.error(f"Erro ao criar token JWT: {e}")
        raise HTTPException(status_code=500, detail="Erro interno na geração do token")

@router.post("/register")
async def register_user(user_data: UserRegister):
    """Registra um novo usuário"""
    try:
        logger.info(f"Tentativa de registro para: {user_data.email}")
        
        # Importar dependências do banco aqui para evitar imports circulares
        from src.models.database import get_db
        from sqlalchemy import create_engine, text
        from config.settings import settings
        
        # Conectar ao banco
        engine = create_engine(settings.database_url_sync)
        
        with engine.connect() as conn:
            # Verificar se email já existe
            result = conn.execute(
                text("SELECT id FROM clients WHERE email = :email"),
                {"email": user_data.email}
            )
            
            if result.fetchone():
                raise HTTPException(
                    status_code=400,
                    detail="Email já está em uso"
                )
            
            # Hash da senha
            hashed_password = hash_password(user_data.password)
            
            # Inserir usuário
            import uuid
            user_id = str(uuid.uuid4())
            
            conn.execute(
                text("""
                    INSERT INTO clients (id, email, name, password_hash, is_active, created_at)
                    VALUES (:id, :email, :name, :password_hash, :is_active, :created_at)
                """),
                {
                    "id": user_id,
                    "email": user_data.email,
                    "name": user_data.name,
                    "password_hash": hashed_password,
                    "is_active": True,
                    "created_at": datetime.datetime.utcnow()
                }
            )
            
            conn.commit()
            
            logger.info(f"Usuário registrado com sucesso: {user_data.email}")
            
            return {
                "message": "Usuário registrado com sucesso",
                "user": {
                    "id": user_id,
                    "email": user_data.email,
                    "name": user_data.name,
                    "is_active": True
                }
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no registro: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Erro interno no servidor: {str(e)}")

@router.post("/login")
async def login_user(login_data: UserLogin):
    """Faz login do usuário"""
    try:
        logger.info(f"Tentativa de login para: {login_data.email}")
        
        # Importar dependências do banco
        from sqlalchemy import create_engine, text
        from config.settings import settings
        
        # Conectar ao banco
        engine = create_engine(settings.database_url_sync)
        
        with engine.connect() as conn:
            # Buscar usuário
            result = conn.execute(
                text("SELECT id, email, name, password_hash, is_active FROM clients WHERE email = :email"),
                {"email": login_data.email}
            )
            
            user = result.fetchone()
            
            if not user:
                logger.warning(f"Usuário não encontrado: {login_data.email}")
                raise HTTPException(
                    status_code=401,
                    detail="Email ou senha incorretos"
                )
            
            # Verificar senha
            if not verify_password(login_data.password, user.password_hash):
                logger.warning(f"Senha incorreta para: {login_data.email}")
                raise HTTPException(
                    status_code=401,
                    detail="Email ou senha incorretos"
                )
            
            # Verificar se usuário está ativo
            if not user.is_active:
                logger.warning(f"Usuário inativo: {login_data.email}")
                raise HTTPException(
                    status_code=401,
                    detail="Conta desativada"
                )
            
            # Criar token JWT
            token = create_jwt_token(user.id, user.email)
            
            logger.info(f"Login realizado com sucesso: {login_data.email}")
            
            return {
                "message": "Login realizado com sucesso",
                "access_token": token,
                "token_type": "bearer",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "name": user.name,
                    "is_active": user.is_active
                }
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no login: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Erro interno no servidor: {str(e)}")

@router.get("/me")
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Retorna dados do usuário atual"""
    try:
        # Decodificar token
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("user_id")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Token inválido")
        
        # Buscar usuário no banco
        from sqlalchemy import create_engine, text
        from config.settings import settings
        
        engine = create_engine(settings.database_url_sync)
        
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT id, email, name, is_active, created_at FROM clients WHERE id = :id"),
                {"id": user_id}
            )
            
            user = result.fetchone()
            
            if not user:
                raise HTTPException(status_code=401, detail="Usuário não encontrado")
            
            return {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "is_active": user.is_active,
                "created_at": user.created_at
            }
            
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")
    except Exception as e:
        logger.error(f"Erro ao buscar usuário: {e}")
        raise HTTPException(status_code=500, detail="Erro interno no servidor")
