"""
Testes unitários para o sistema de autenticação
"""
import pytest
import jwt
import bcrypt
from datetime import datetime, timedelta, UTC
from unittest.mock import Mock, patch, AsyncMock
import hashlib
import secrets
import time
from typing import Dict, Optional


# Mock das classes de autenticação baseadas no código analisado
class AuthenticationService:
    """
    Serviço de autenticação para o sistema de trading
    """
    
    def __init__(self, secret_key: str = "test_secret_key", algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.token_expiry_minutes = 30
        self.refresh_token_expiry_days = 7
        self.max_login_attempts = 5
        self.lockout_duration_minutes = 15
        
        # Rate limiting storage (em produção seria Redis)
        self.rate_limit_storage = {}
        self.failed_attempts = {}
        self.locked_accounts = {}
    
    def hash_password(self, password: str) -> str:
        """Hash da senha usando bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verifica se a senha está correta"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception:
            return False
    
    def generate_jwt_token(self, user_id: str, additional_claims: Dict = None) -> str:
        """Gera token JWT"""
        now = datetime.now(UTC)
        payload = {
            "sub": user_id,
            "iat": now,
            "exp": now + timedelta(minutes=self.token_expiry_minutes),
            "type": "access"
        }
        
        if additional_claims:
            payload.update(additional_claims)
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def generate_refresh_token(self, user_id: str) -> str:
        """Gera refresh token"""
        now = datetime.now(UTC)
        payload = {
            "sub": user_id,
            "iat": now,
            "exp": now + timedelta(days=self.refresh_token_expiry_days),
            "type": "refresh",
            "jti": secrets.token_urlsafe(32)  # Unique token ID
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_jwt_token(self, token: str) -> Optional[Dict]:
        """Verifica e decodifica token JWT"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def is_account_locked(self, user_id: str) -> bool:
        """Verifica se a conta está bloqueada"""
        if user_id not in self.locked_accounts:
            return False
        
        lock_time = self.locked_accounts[user_id]
        if datetime.now(UTC) > lock_time + timedelta(minutes=self.lockout_duration_minutes):
            # Desbloqueio automático
            del self.locked_accounts[user_id]
            if user_id in self.failed_attempts:
                del self.failed_attempts[user_id]
            return False
        
        return True
    
    def record_failed_attempt(self, user_id: str) -> None:
        """Registra tentativa de login falhada"""
        if user_id not in self.failed_attempts:
            self.failed_attempts[user_id] = []
        
        self.failed_attempts[user_id].append(datetime.now(UTC))
        
        # Limpar tentativas antigas (mais de 1 hora)
        cutoff_time = datetime.now(UTC) - timedelta(hours=1)
        self.failed_attempts[user_id] = [
            attempt for attempt in self.failed_attempts[user_id] 
            if attempt > cutoff_time
        ]
        
        # Bloquear conta se muitas tentativas
        if len(self.failed_attempts[user_id]) >= self.max_login_attempts:
            self.locked_accounts[user_id] = datetime.now(UTC)
    
    def clear_failed_attempts(self, user_id: str) -> None:
        """Limpa tentativas falhadas após login bem-sucedido"""
        if user_id in self.failed_attempts:
            del self.failed_attempts[user_id]
        if user_id in self.locked_accounts:
            del self.locked_accounts[user_id]
    
    def check_rate_limit(self, identifier: str, max_requests: int = 10, window_minutes: int = 1) -> bool:
        """Verifica rate limiting"""
        now = datetime.now(UTC)
        window_start = now - timedelta(minutes=window_minutes)
        
        if identifier not in self.rate_limit_storage:
            self.rate_limit_storage[identifier] = []
        
        # Limpar requests antigas
        self.rate_limit_storage[identifier] = [
            request_time for request_time in self.rate_limit_storage[identifier]
            if request_time > window_start
        ]
        
        # Verificar se excedeu o limite
        if len(self.rate_limit_storage[identifier]) >= max_requests:
            return False
        
        # Registrar nova request
        self.rate_limit_storage[identifier].append(now)
        return True


class User:
    """Modelo de usuário para testes"""
    
    def __init__(self, user_id: str, email: str, password_hash: str, is_active: bool = True):
        self.id = user_id
        self.email = email
        self.password_hash = password_hash
        self.is_active = is_active
        self.created_at = datetime.now(UTC)
        self.last_login = None
        self.login_count = 0


class TestAuthenticationService:
    """Testes para o serviço de autenticação"""
    
    @pytest.fixture
    def auth_service(self):
        """Fixture do serviço de autenticação"""
        return AuthenticationService()
    
    @pytest.fixture
    def sample_user(self, auth_service):
        """Fixture de usuário de exemplo"""
        password_hash = auth_service.hash_password("test_password_123")
        return User("test-user-123", "test@example.com", password_hash)
    
    def test_password_hashing(self, auth_service):
        """Testa hash de senhas"""
        password = "my_secure_password_123"
        hashed = auth_service.hash_password(password)
        
        # Hash deve ser diferente da senha original
        assert hashed != password
        
        # Hash deve ter formato bcrypt
        assert hashed.startswith('$2b$')
        
        # Deve ser possível verificar a senha
        assert auth_service.verify_password(password, hashed)
        
        # Senha incorreta deve falhar
        assert not auth_service.verify_password("wrong_password", hashed)
    
    def test_password_hashing_different_salts(self, auth_service):
        """Testa que senhas iguais geram hashes diferentes"""
        password = "same_password"
        hash1 = auth_service.hash_password(password)
        hash2 = auth_service.hash_password(password)
        
        # Hashes devem ser diferentes devido ao salt
        assert hash1 != hash2
        
        # Mas ambos devem verificar corretamente
        assert auth_service.verify_password(password, hash1)
        assert auth_service.verify_password(password, hash2)
    
    def test_password_verification_edge_cases(self, auth_service):
        """Testa casos extremos na verificação de senhas"""
        # Senha vazia
        assert not auth_service.verify_password("", "invalid_hash")
        
        # Hash inválido
        assert not auth_service.verify_password("password", "invalid_hash")
        
        # Hash vazio
        assert not auth_service.verify_password("password", "")
    
    def test_jwt_token_generation(self, auth_service):
        """Testa geração de tokens JWT"""
        user_id = "test-user-123"
        token = auth_service.generate_jwt_token(user_id)
        
        # Token deve ser uma string não vazia
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Token deve ter 3 partes separadas por pontos
        parts = token.split('.')
        assert len(parts) == 3
    
    def test_jwt_token_with_additional_claims(self, auth_service):
        """Testa geração de token com claims adicionais"""
        user_id = "test-user-123"
        additional_claims = {
            "role": "trader",
            "permissions": ["read", "write"]
        }
        
        token = auth_service.generate_jwt_token(user_id, additional_claims)
        payload = auth_service.verify_jwt_token(token)
        
        assert payload is not None
        assert payload["sub"] == user_id
        assert payload["role"] == "trader"
        assert payload["permissions"] == ["read", "write"]
    
    def test_jwt_token_verification_valid(self, auth_service):
        """Testa verificação de token válido"""
        user_id = "test-user-123"
        token = auth_service.generate_jwt_token(user_id)
        
        payload = auth_service.verify_jwt_token(token)
        
        assert payload is not None
        assert payload["sub"] == user_id
        assert payload["type"] == "access"
        assert "iat" in payload
        assert "exp" in payload
    
    def test_jwt_token_verification_invalid(self, auth_service):
        """Testa verificação de token inválido"""
        # Token malformado
        assert auth_service.verify_jwt_token("invalid.token") is None
        
        # Token vazio
        assert auth_service.verify_jwt_token("") is None
        
        # Token com assinatura inválida
        fake_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ0ZXN0In0.invalid_signature"
        assert auth_service.verify_jwt_token(fake_token) is None
    
    def test_jwt_token_expiration(self, auth_service):
        """Testa expiração de tokens"""
        # Criar serviço com expiração muito curta
        short_auth = AuthenticationService()
        short_auth.token_expiry_minutes = 0  # Expira imediatamente
        
        user_id = "test-user-123"
        token = short_auth.generate_jwt_token(user_id)
        
        # Aguardar um pouco para garantir expiração
        time.sleep(0.1)
        
        # Token deve estar expirado
        payload = short_auth.verify_jwt_token(token)
        assert payload is None
    
    def test_refresh_token_generation(self, auth_service):
        """Testa geração de refresh tokens"""
        user_id = "test-user-123"
        refresh_token = auth_service.generate_refresh_token(user_id)
        
        payload = auth_service.verify_jwt_token(refresh_token)
        
        assert payload is not None
        assert payload["sub"] == user_id
        assert payload["type"] == "refresh"
        assert "jti" in payload  # Unique token ID
        
        # Refresh token deve ter expiração mais longa
        exp_time = datetime.fromtimestamp(payload['exp'], UTC)
        now = datetime.now(UTC)
        time_diff = exp_time - now
        assert time_diff.days >= 6  # Pelo menos 6 dias
    
    def test_account_locking_mechanism(self, auth_service):
        """Testa mecanismo de bloqueio de conta"""
        user_id = "test-user-123"
        
        # Inicialmente não deve estar bloqueada
        assert not auth_service.is_account_locked(user_id)
        
        # Registrar tentativas falhadas
        for _ in range(auth_service.max_login_attempts):
            auth_service.record_failed_attempt(user_id)
        
        # Agora deve estar bloqueada
        assert auth_service.is_account_locked(user_id)
    
    def test_account_unlock_after_timeout(self, auth_service):
        """Testa desbloqueio automático após timeout"""
        user_id = "test-user-123"
        
        # Bloquear conta
        for _ in range(auth_service.max_login_attempts):
            auth_service.record_failed_attempt(user_id)
        
        assert auth_service.is_account_locked(user_id)
        
        # Simular passagem do tempo alterando o timestamp de bloqueio
        past_time = datetime.now(UTC) - timedelta(minutes=auth_service.lockout_duration_minutes + 1)
        auth_service.locked_accounts[user_id] = past_time
        
        # Agora não deve estar mais bloqueada
        assert not auth_service.is_account_locked(user_id)
    
    def test_clear_failed_attempts(self, auth_service):
        """Testa limpeza de tentativas falhadas"""
        user_id = "test-user-123"
        
        # Registrar algumas tentativas falhadas
        for _ in range(3):
            auth_service.record_failed_attempt(user_id)
        
        assert len(auth_service.failed_attempts[user_id]) == 3
        
        # Limpar tentativas
        auth_service.clear_failed_attempts(user_id)
        
        # Não deve haver mais tentativas registradas
        assert user_id not in auth_service.failed_attempts
    
    def test_rate_limiting_basic(self, auth_service):
        """Testa rate limiting básico"""
        identifier = "192.168.1.1"
        
        # Primeiras requests devem passar
        for _ in range(5):
            assert auth_service.check_rate_limit(identifier, max_requests=10)
        
        # Ainda dentro do limite
        assert auth_service.check_rate_limit(identifier, max_requests=10)
        
        # Exceder o limite
        for _ in range(5):
            auth_service.check_rate_limit(identifier, max_requests=10)
        
        # Agora deve ser bloqueado
        assert not auth_service.check_rate_limit(identifier, max_requests=10)
    
    def test_rate_limiting_window_reset(self, auth_service):
        """Testa reset da janela de rate limiting"""
        identifier = "192.168.1.1"
        
        # Exceder limite
        for _ in range(11):
            auth_service.check_rate_limit(identifier, max_requests=10, window_minutes=0.001)  # 0.06 segundos
        
        # Deve estar bloqueado
        assert not auth_service.check_rate_limit(identifier, max_requests=10, window_minutes=0.001)
        
        # Aguardar reset da janela (mais tempo para garantir reset)
        time.sleep(0.1)
        
        # Deve estar liberado novamente
        assert auth_service.check_rate_limit(identifier, max_requests=10, window_minutes=0.001)
    
    def test_failed_attempts_cleanup(self, auth_service):
        """Testa limpeza automática de tentativas antigas"""
        user_id = "test-user-123"
        
        # Simular tentativas antigas
        old_time = datetime.now(UTC) - timedelta(hours=2)
        auth_service.failed_attempts[user_id] = [old_time, old_time, old_time]
        
        # Registrar nova tentativa (deve limpar as antigas)
        auth_service.record_failed_attempt(user_id)
        
        # Deve ter apenas a tentativa recente
        assert len(auth_service.failed_attempts[user_id]) == 1
    
    @pytest.mark.security
    def test_token_secret_key_security(self):
        """Testa segurança da chave secreta"""
        # Tokens gerados com chaves diferentes devem ser incompatíveis
        auth1 = AuthenticationService(secret_key="key1")
        auth2 = AuthenticationService(secret_key="key2")
        
        user_id = "test-user-123"
        token = auth1.generate_jwt_token(user_id)
        
        # Token gerado com key1 não deve ser válido para auth2
        assert auth2.verify_jwt_token(token) is None
    
    @pytest.mark.security
    def test_password_strength_requirements(self, auth_service):
        """Testa que senhas fracas ainda são hasheadas corretamente"""
        # Mesmo senhas fracas devem ser hasheadas (validação de força seria em outro lugar)
        weak_passwords = ["123", "password", "abc"]
        
        for password in weak_passwords:
            hashed = auth_service.hash_password(password)
            assert auth_service.verify_password(password, hashed)
            assert hashed != password
    
    @pytest.mark.performance
    def test_password_hashing_performance(self, auth_service):
        """Testa performance do hash de senhas"""
        password = "test_password_123"
        
        start_time = time.time()
        auth_service.hash_password(password)
        hash_time = time.time() - start_time
        
        # Hash deve ser rápido mas não instantâneo (bcrypt tem custo computacional)
        assert 0.01 < hash_time < 1.0  # Entre 10ms e 1s
    
    @pytest.mark.performance
    def test_token_verification_performance(self, auth_service):
        """Testa performance da verificação de tokens"""
        user_id = "test-user-123"
        token = auth_service.generate_jwt_token(user_id)
        
        start_time = time.time()
        for _ in range(100):  # Verificar 100 tokens
            auth_service.verify_jwt_token(token)
        verification_time = time.time() - start_time
        
        # Verificação deve ser rápida
        assert verification_time < 0.1  # Menos de 100ms para 100 verificações


class TestAuthenticationIntegration:
    """Testes de integração do sistema de autenticação"""
    
    @pytest.fixture
    def auth_service(self):
        return AuthenticationService()
    
    def test_complete_authentication_flow(self, auth_service):
        """Testa fluxo completo de autenticação"""
        # 1. Criar usuário
        password = "secure_password_123"
        password_hash = auth_service.hash_password(password)
        user = User("test-user-123", "test@example.com", password_hash)
        
        # 2. Verificar senha
        assert auth_service.verify_password(password, user.password_hash)
        
        # 3. Gerar tokens
        access_token = auth_service.generate_jwt_token(user.id)
        refresh_token = auth_service.generate_refresh_token(user.id)
        
        # 4. Verificar tokens
        access_payload = auth_service.verify_jwt_token(access_token)
        refresh_payload = auth_service.verify_jwt_token(refresh_token)
        
        assert access_payload["sub"] == user.id
        assert refresh_payload["sub"] == user.id
        assert access_payload["type"] == "access"
        assert refresh_payload["type"] == "refresh"
    
    def test_failed_login_protection(self, auth_service):
        """Testa proteção contra tentativas de login falhadas"""
        user_id = "test-user-123"
        
        # Simular múltiplas tentativas falhadas
        for i in range(auth_service.max_login_attempts + 2):
            if not auth_service.is_account_locked(user_id):
                auth_service.record_failed_attempt(user_id)
        
        # Conta deve estar bloqueada
        assert auth_service.is_account_locked(user_id)
        
        # Mesmo com senha correta, não deve permitir login
        # (isso seria implementado na lógica de login)
        
        # Após limpeza, deve funcionar novamente
        auth_service.clear_failed_attempts(user_id)
        assert not auth_service.is_account_locked(user_id)
    
    def test_concurrent_rate_limiting(self, auth_service):
        """Testa rate limiting com múltiplos identificadores"""
        identifiers = ["ip1", "ip2", "ip3"]
        
        # Cada IP deve ter seu próprio limite
        for identifier in identifiers:
            for _ in range(10):
                assert auth_service.check_rate_limit(identifier, max_requests=10)
            
            # Exceder limite para este IP
            assert not auth_service.check_rate_limit(identifier, max_requests=10)
        
        # Outros IPs não devem ser afetados
        new_ip = "ip4"
        assert auth_service.check_rate_limit(new_ip, max_requests=10)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

