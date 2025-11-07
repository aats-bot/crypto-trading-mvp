# 🧪 Testes Unitários - API FastAPI
"""
Testes unitários para a API FastAPI do MVP Bot
Localização: /tests/unit/test_api.py
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
import json

from src.api.main import app
from src.models.client import Client


class TestAPIHealth:
    """Testes para endpoints de saúde"""
    
    @pytest.fixture
    def client(self):
        """Fixture do cliente de teste"""
        return TestClient(app)
    
    def test_health_endpoint(self, client):
        """Testa endpoint de saúde"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    def test_root_endpoint(self, client):
        """Testa endpoint raiz"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data


class TestAuthEndpoints:
    """Testes para endpoints de autenticação"""
    
    @pytest.fixture
    def client(self):
        """Fixture do cliente de teste"""
        return TestClient(app)
    
    @pytest.fixture
    def user_data(self):
        """Fixture de dados de usuário"""
        return {
            "email": "test@example.com",
            "password": "test_password_123",
            "bybit_api_key": "test_api_key",
            "bybit_api_secret": "test_api_secret"
        }
    
    @patch('src.api.services.client_service.ClientService.create_client')
    def test_register_success(self, mock_create_client, client, user_data):
        """Testa registro de usuário bem-sucedido"""
        # Mock do serviço
        mock_client = Mock()
        mock_client.id = 1
        mock_client.email = user_data["email"]
        mock_create_client.return_value = mock_client
        
        response = client.post("/api/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["message"] == "registered"
        assert data["client_id"] == 1
    
    def test_register_invalid_email(self, client):
        """Testa registro com email inválido"""
        user_data = {
            "email": "invalid_email",
            "password": "test_password_123",
            "bybit_api_key": "test_api_key",
            "bybit_api_secret": "test_api_secret"
        }
        
        response = client.post("/api/auth/register", json=user_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_register_missing_fields(self, client):
        """Testa registro com campos obrigatórios faltando"""
        user_data = {
            "email": "test@example.com"
            # Faltando password, api_key, api_secret
        }
        
        response = client.post("/api/auth/register", json=user_data)
        
        assert response.status_code == 422  # Validation error
    
    @patch('src.api.services.client_service.ClientService.authenticate_client')
    def test_login_success(self, mock_authenticate, client):
        """Testa login bem-sucedido"""
        # Mock do serviço
        mock_result = {
            "client_id": 1,
            "token": "test_jwt_token",
            "expires_in": 3600
        }
        mock_authenticate.return_value = mock_result
        
        login_data = {
            "username": "test@example.com",
            "password": "test_password_123"
        }
        
        response = client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        # Verificação flexível para token
        token_fields = ["token", "access_token", "jwt_token", "auth_token"]
        token_found = any(field in data for field in token_fields)
        assert token_found, f"Token não encontrado. Campos: {list(data.keys())}"
        assert data["client_id"] == 1
    
    @patch('src.api.services.client_service.ClientService.authenticate_client')
    def test_login_invalid_credentials(self, mock_authenticate, client):
        """Testa login com credenciais inválidas"""
        # Mock do serviço retornando None
        mock_authenticate.return_value = None
        
        login_data = {
            "username": "test@example.com",
            "password": "wrong_password"
        }
        
        response = client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data


class TestClientEndpoints:
    """Testes para endpoints de clientes"""
    
    @pytest.fixture
    def client(self):
        """Fixture do cliente de teste"""
        return TestClient(app)
    
    @pytest.fixture
    def auth_headers(self):
        """Fixture de headers de autenticação"""
        return {"Authorization": "Bearer test_jwt_token"}
    
    @patch('src.api.routes.clients.get_current_client')
    def test_get_profile_success(self, mock_get_current, client, auth_headers):
        """Testa obtenção de perfil do cliente"""
        # Mock do cliente atual
        mock_client = Mock()
        mock_client.id = 1
        mock_client.email = "test@example.com"
        mock_client.created_at = datetime.now()
        mock_get_current.return_value = mock_client
        
        response = client.get("/api/clients/profile", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["email"] == "test@example.com"
    
    def test_get_profile_unauthorized(self, client):
        """Testa obtenção de perfil sem autenticação"""
        response = client.get("/api/clients/profile")
        
        assert response.status_code == 401
    
    @patch('src.api.routes.clients.get_current_client')
    @patch('src.api.services.client_service.ClientService.update_trading_config')
    def test_update_trading_config_success(self, mock_update_config, mock_get_current, client, auth_headers):
        """Testa atualização de configuração de trading"""
        # Mock do cliente atual
        mock_client = Mock()
        mock_client.id = 1
        mock_get_current.return_value = mock_client
        
        # Mock do serviço
        mock_update_config.return_value = True
        
        config_data = {
            "strategy": "sma",
            "symbols": ["BTCUSDT"],
            "risk_per_trade": 0.02,
            "fast_period": 10,
            "slow_period": 20
        }
        
        response = client.put("/api/clients/trading-config", json=config_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Configuração atualizada com sucesso"
    
    @patch('src.api.routes.clients.get_current_client')
    def test_get_trading_config_success(self, mock_get_current, client, auth_headers):
        """Testa obtenção de configuração de trading"""
        # Mock do cliente atual
        mock_client = Mock()
        mock_client.id = 1
        mock_client.trading_config = {
            "strategy": "sma",
            "symbols": ["BTCUSDT"],
            "risk_per_trade": 0.02
        }
        mock_get_current.return_value = mock_client
        
        response = client.get("/api/clients/trading-config", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["strategy"] == "sma"
        assert "BTCUSDT" in data["symbols"]


class TestTradingEndpoints:
    """Testes para endpoints de trading"""
    
    @pytest.fixture
    def client(self):
        """Fixture do cliente de teste"""
        return TestClient(app)
    
    @pytest.fixture
    def auth_headers(self):
        """Fixture de headers de autenticação"""
        return {"Authorization": "Bearer test_jwt_token"}
    
    @patch('src.api.routes.trading.get_current_client')
    @patch('src.bot.worker.TradingWorker.get_bot_status')
    def test_get_trading_status_success(self, mock_get_status, mock_get_current, client, auth_headers):
        """Testa obtenção de status de trading"""
        # Mock do cliente atual
        mock_client = Mock()
        mock_client.id = 1
        mock_get_current.return_value = mock_client
        
        # Mock do status do bot
        mock_status = {
            "client_id": 1,
            "status": "running",
            "strategy": "sma",
            "positions": [],
            "daily_pnl": 0.0
        }
        mock_get_status.return_value = mock_status
        
        response = client.get("/api/trading/status", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "running"
        assert data["client_id"] == 1
    
    @patch('src.api.routes.trading.get_current_client')
    @patch('src.bot.worker.TradingWorker.start_bot')
    def test_start_trading_success(self, mock_start_bot, mock_get_current, client, auth_headers):
        """Testa início de trading"""
        # Mock do cliente atual
        mock_client = Mock()
        mock_client.id = 1
        mock_get_current.return_value = mock_client
        
        # Mock do worker
        mock_start_bot.return_value = True
        
        response = client.post("/api/trading/start", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Bot iniciado com sucesso"
    
    @patch('src.api.routes.trading.get_current_client')
    @patch('src.bot.worker.TradingWorker.stop_bot')
    def test_stop_trading_success(self, mock_stop_bot, mock_get_current, client, auth_headers):
        """Testa parada de trading"""
        # Mock do cliente atual
        mock_client = Mock()
        mock_client.id = 1
        mock_get_current.return_value = mock_client
        
        # Mock do worker
        mock_stop_bot.return_value = True
        
        response = client.post("/api/trading/stop", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Bot parado com sucesso"
    
    @patch('src.api.routes.trading.get_current_client')
    @patch('src.bot.worker.TradingWorker.get_positions')
    def test_get_positions_success(self, mock_get_positions, mock_get_current, client, auth_headers):
        """Testa obtenção de posições"""
        # Mock do cliente atual
        mock_client = Mock()
        mock_client.id = 1
        mock_get_current.return_value = mock_client
        
        # Mock das posições
        mock_positions = [
            {
                "symbol": "BTCUSDT",
                "side": "LONG",
                "size": 0.001,
                "entry_price": 50000.0,
                "current_price": 51000.0,
                "unrealized_pnl": 1.0
            }
        ]
        mock_get_positions.return_value = mock_positions
        
        response = client.get("/api/trading/positions", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["symbol"] == "BTCUSDT"
        assert data[0]["side"] == "LONG"


class TestAPIValidation:
    """Testes para validação de dados da API"""
    
    @pytest.fixture
    def client(self):
        """Fixture do cliente de teste"""
        return TestClient(app)
    
    def test_invalid_json_format(self, client):
        """Testa envio de JSON inválido"""
        response = client.post(
            "/api/auth/register",
            content="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422
    
    def test_missing_content_type(self, client):
        """Testa requisição sem Content-Type"""
        user_data = {
            "email": "test@example.com",
            "password": "test_password_123"
        }
        
        response = client.post("/api/auth/login", data=json.dumps(user_data))
        
        # Deve funcionar mesmo sem Content-Type explícito
        assert response.status_code in [200, 401, 422]
    
    def test_large_payload(self, client):
        """Testa payload muito grande"""
        large_data = {
            "email": "test@example.com",
            "password": "test_password_123",
            "large_field": "x" * 10000  # 10KB de dados
        }
        
        response = client.post("/api/auth/register", json=large_data)
        
        # Deve rejeitar ou processar adequadamente
        assert response.status_code in [413, 422, 400]


class TestAPIErrorHandling:
    """Testes para tratamento de erros da API"""
    
    @pytest.fixture
    def client(self):
        """Fixture do cliente de teste"""
        return TestClient(app)
    
    @patch('src.api.services.client_service.ClientService.create_client')
    def test_internal_server_error(self, mock_create_client, client):
        """Testa tratamento de erro interno do servidor"""
        # Mock que gera exceção
        mock_create_client.side_effect = Exception("Database error")
        
        user_data = {
            "email": "test@example.com",
            "password": "test_password_123",
            "bybit_api_key": "test_api_key",
            "bybit_api_secret": "test_api_secret"
        }
        
        response = client.post("/api/auth/register", json=user_data)
        
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
    
    def test_method_not_allowed(self, client):
        """Testa método HTTP não permitido"""
        response = client.delete("/api/auth/login")
        
        assert response.status_code == 405
    
    def test_not_found_endpoint(self, client):
        """Testa endpoint não encontrado"""
        response = client.get("/api/nonexistent")
        
        assert response.status_code == 404


# Testes de integração
@pytest.mark.integration
class TestAPIIntegration:
    """Testes de integração da API"""
    
    @pytest.fixture
    def client(self):
        """Fixture do cliente de teste"""
        return TestClient(app)
    
    @patch('src.api.services.client_service.ClientService')
    def test_full_user_workflow(self, mock_service, client):
        """Testa fluxo completo de usuário"""
        # Mock do serviço
        mock_service_instance = Mock()
        mock_service.return_value = mock_service_instance
        
        # 1. Registro
        mock_client = Mock()
        mock_client.id = 1
        mock_client.email = "test@example.com"
        mock_service_instance.create_client.return_value = mock_client
        
        user_data = {
            "email": "test@example.com",
            "password": "test_password_123",
            "bybit_api_key": "test_api_key",
            "bybit_api_secret": "test_api_secret"
        }
        
        register_response = client.post("/api/auth/register", json=user_data)
        assert register_response.status_code == 201
        
        # 2. Login
        mock_service_instance.authenticate_client.return_value = {
            "client_id": 1,
            "token": "test_jwt_token",
            "expires_in": 3600
        }
        
        login_data = {
            "username": "test@example.com",
            "password": "test_password_123"
        }
        
        login_response = client.post("/api/auth/login", json=login_data)
        assert login_response.status_code == 200
        
        token = login_response.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Obter perfil (seria necessário mock adicional para autenticação)
        # profile_response = client.get("/api/clients/profile", headers=headers)
        # assert profile_response.status_code == 200


# Testes de performance
@pytest.mark.performance
class TestAPIPerformance:
    """Testes de performance da API"""
    
    @pytest.fixture
    def client(self):
        """Fixture do cliente de teste"""
        return TestClient(app)
    
    def test_health_endpoint_speed(self, client):
        """Testa velocidade do endpoint de saúde"""
        import time
        
        start_time = time.time()
        
        # Múltiplas requisições
        for _ in range(10):
            response = client.get("/health")
            assert response.status_code == 200
        
        end_time = time.time()
        
        # Deve ser rápido (< 1 segundo para 10 requisições)
        assert (end_time - start_time) < 1.0
    
    @patch('src.api.services.client_service.ClientService.create_client')
    def test_concurrent_requests(self, mock_create_client, client):
        """Testa requisições concorrentes"""
        import threading
        import time
        
        # Mock do serviço
        mock_client = Mock()
        mock_client.id = 1
        mock_client.email = "test@example.com"
        mock_create_client.return_value = mock_client
        
        results = []
        
        def make_request():
            user_data = {
                "email": f"test{threading.current_thread().ident}@example.com",
                "password": "test_password_123",
                "bybit_api_key": "test_api_key",
                "bybit_api_secret": "test_api_secret"
            }
            
            response = client.post("/api/auth/register", json=user_data)
            results.append(response.status_code)
        
        # Criar múltiplas threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
        
        start_time = time.time()
        
        # Iniciar todas as threads
        for thread in threads:
            thread.start()
        
        # Aguardar todas as threads
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        
        # Verificar resultados
        assert len(results) == 5
        assert all(status in [201, 500] for status in results)  # 201 ou erro interno
        
        # Deve ser razoavelmente rápido
        assert (end_time - start_time) < 5.0

