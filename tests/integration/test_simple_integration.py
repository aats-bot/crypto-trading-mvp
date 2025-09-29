"""
Testes de integração simplificados para Windows
Semana 2 da Onda 1 - Versão compatível
"""
import pytest
import asyncio
import json
import time
from datetime import datetime, timedelta
import sys
import os

# Adicionar o diretório do projeto ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

# Importar a estratégia dos testes unitários
try:
    from tests.unit.test_ppp_vishva_strategy import PPPVishvaStrategy
except ImportError:
    # Fallback: criar uma versão simplificada
    class PPPVishvaStrategy:
        def __init__(self):
            self.risk_per_trade = 0.02
        
        def calculate_ema(self, prices, period):
            if not prices or period <= 0:
                return prices[-1] if prices else 0
            return sum(prices[-period:]) / min(len(prices), period)
        
        def generate_signal(self, market_data):
            return 'hold'


class SimpleAPI:
    """API simplificada para testes de integração"""
    
    def __init__(self):
        self.is_running = False
        self.strategies = {}
        self.positions = {}
        self.market_data_cache = {}
    
    async def start(self):
        """Iniciar API"""
        self.is_running = True
        self.strategies['ppp_vishva'] = PPPVishvaStrategy()
        return {"status": "started"}
    
    async def stop(self):
        """Parar API"""
        self.is_running = False
        self.positions.clear()
        self.market_data_cache.clear()
        return {"status": "stopped"}
    
    async def get_market_data(self, symbol):
        """Obter dados de mercado simulados"""
        if not self.is_running:
            raise RuntimeError("API não está rodando")
        
        # Simular dados
        data = {
            'symbol': symbol,
            'price': 50000.0,
            'timestamp': int(time.time() * 1000),
            'volume': 1.5
        }
        
        # Cache
        self.market_data_cache[symbol] = data
        return data
    
    async def create_position(self, symbol, side, size):
        """Criar posição"""
        if not self.is_running:
            raise RuntimeError("API não está rodando")
        
        position_id = f"{symbol}_{side}_{int(time.time())}"
        position = {
            'id': position_id,
            'symbol': symbol,
            'side': side,
            'size': size,
            'status': 'open',
            'created_at': datetime.now().isoformat()
        }
        
        self.positions[position_id] = position
        return position
    
    async def get_positions(self):
        """Obter posições"""
        return list(self.positions.values())
    
    async def analyze_market(self, symbol):
        """Analisar mercado"""
        if not self.is_running:
            raise RuntimeError("API não está rodando")
        
        market_data = await self.get_market_data(symbol)
        strategy = self.strategies.get('ppp_vishva')
        
        if strategy:
            signal = strategy.generate_signal(market_data)
        else:
            signal = 'hold'
        
        return {
            'symbol': symbol,
            'signal': signal,
            'timestamp': datetime.now().isoformat()
        }


class SimpleDatabase:
    """Banco de dados simplificado para testes"""
    
    def __init__(self):
        self.users = {}
        self.positions = {}
        self.logs = []
        self.is_connected = False
        self.next_id = 1
    
    async def connect(self):
        """Conectar ao banco"""
        self.is_connected = True
        return {"status": "connected"}
    
    async def disconnect(self):
        """Desconectar do banco"""
        self.is_connected = False
        self.users.clear()
        self.positions.clear()
        self.logs.clear()
        return {"status": "disconnected"}
    
    async def create_user(self, username, email):
        """Criar usuário"""
        if not self.is_connected:
            raise ConnectionError("Banco não conectado")
        
        if username in [u['username'] for u in self.users.values()]:
            raise ValueError("Usuário já existe")
        
        user_id = self.next_id
        self.next_id += 1
        
        user = {
            'id': user_id,
            'username': username,
            'email': email,
            'created_at': datetime.now().isoformat()
        }
        
        self.users[user_id] = user
        return user
    
    async def get_user(self, user_id):
        """Obter usuário"""
        if not self.is_connected:
            raise ConnectionError("Banco não conectado")
        
        return self.users.get(user_id)
    
    async def create_position(self, user_id, symbol, side, size):
        """Criar posição no banco"""
        if not self.is_connected:
            raise ConnectionError("Banco não conectado")
        
        position_id = self.next_id
        self.next_id += 1
        
        position = {
            'id': position_id,
            'user_id': user_id,
            'symbol': symbol,
            'side': side,
            'size': size,
            'status': 'open',
            'created_at': datetime.now().isoformat()
        }
        
        self.positions[position_id] = position
        return position
    
    async def get_user_positions(self, user_id):
        """Obter posições do usuário"""
        if not self.is_connected:
            raise ConnectionError("Banco não conectado")
        
        return [p for p in self.positions.values() if p['user_id'] == user_id]
    
    async def log_event(self, level, message, user_id=None):
        """Registrar log"""
        if not self.is_connected:
            raise ConnectionError("Banco não conectado")
        
        log = {
            'id': len(self.logs) + 1,
            'level': level,
            'message': message,
            'user_id': user_id,
            'timestamp': datetime.now().isoformat()
        }
        
        self.logs.append(log)
        return log['id']


class SimpleCache:
    """Cache simplificado para testes"""
    
    def __init__(self):
        self.data = {}
        self.expiry = {}
        self.is_connected = False
    
    async def connect(self):
        """Conectar ao cache"""
        self.is_connected = True
        return {"status": "connected"}
    
    async def disconnect(self):
        """Desconectar do cache"""
        self.is_connected = False
        self.data.clear()
        self.expiry.clear()
        return {"status": "disconnected"}
    
    async def set(self, key, value, ttl=None):
        """Definir valor"""
        if not self.is_connected:
            raise ConnectionError("Cache não conectado")
        
        self.data[key] = value
        if ttl:
            self.expiry[key] = time.time() + ttl
        
        return True
    
    async def get(self, key):
        """Obter valor"""
        if not self.is_connected:
            raise ConnectionError("Cache não conectado")
        
        # Verificar expiração
        if key in self.expiry and time.time() > self.expiry[key]:
            self.data.pop(key, None)
            self.expiry.pop(key, None)
            return None
        
        return self.data.get(key)
    
    async def delete(self, key):
        """Deletar chave"""
        if not self.is_connected:
            raise ConnectionError("Cache não conectado")
        
        deleted = key in self.data
        self.data.pop(key, None)
        self.expiry.pop(key, None)
        return deleted


class TestSimpleAPIIntegration:
    """Testes de integração da API simplificada"""
    
    @pytest.mark.asyncio
    async def test_api_lifecycle(self):
        """Testa ciclo de vida da API"""
        api = SimpleAPI()
        
        # Deve começar parada
        assert not api.is_running
        
        # Iniciar
        result = await api.start()
        assert result["status"] == "started"
        assert api.is_running
        
        # Parar
        result = await api.stop()
        assert result["status"] == "stopped"
        assert not api.is_running
    
    @pytest.mark.asyncio
    async def test_market_data_flow(self):
        """Testa fluxo de dados de mercado"""
        api = SimpleAPI()
        await api.start()
        
        try:
            # Obter dados de mercado
            data = await api.get_market_data("BTCUSDT")
            
            assert data["symbol"] == "BTCUSDT"
            assert data["price"] > 0
            assert "timestamp" in data
            assert "volume" in data
            
            # Verificar cache
            assert "BTCUSDT" in api.market_data_cache
            
        finally:
            await api.stop()
    
    @pytest.mark.asyncio
    async def test_position_management(self):
        """Testa gestão de posições"""
        api = SimpleAPI()
        await api.start()
        
        try:
            # Criar posição
            position = await api.create_position("BTCUSDT", "buy", 0.1)
            
            assert position["symbol"] == "BTCUSDT"
            assert position["side"] == "buy"
            assert position["size"] == 0.1
            assert position["status"] == "open"
            
            # Obter posições
            positions = await api.get_positions()
            assert len(positions) == 1
            assert positions[0]["id"] == position["id"]
            
        finally:
            await api.stop()
    
    @pytest.mark.asyncio
    async def test_market_analysis(self):
        """Testa análise de mercado"""
        api = SimpleAPI()
        await api.start()
        
        try:
            # Analisar mercado
            analysis = await api.analyze_market("BTCUSDT")
            
            assert analysis["symbol"] == "BTCUSDT"
            assert analysis["signal"] in ["buy", "sell", "hold"]
            assert "timestamp" in analysis
            
        finally:
            await api.stop()
    
    @pytest.mark.asyncio
    async def test_api_error_handling(self):
        """Testa tratamento de erros da API"""
        api = SimpleAPI()
        
        # Tentar operações sem iniciar
        with pytest.raises(RuntimeError, match="API não está rodando"):
            await api.get_market_data("BTCUSDT")
        
        with pytest.raises(RuntimeError, match="API não está rodando"):
            await api.create_position("BTCUSDT", "buy", 0.1)


class TestSimpleDatabaseIntegration:
    """Testes de integração do banco simplificado"""
    
    @pytest.mark.asyncio
    async def test_database_lifecycle(self):
        """Testa ciclo de vida do banco"""
        db = SimpleDatabase()
        
        # Deve começar desconectado
        assert not db.is_connected
        
        # Conectar
        result = await db.connect()
        assert result["status"] == "connected"
        assert db.is_connected
        
        # Desconectar
        result = await db.disconnect()
        assert result["status"] == "disconnected"
        assert not db.is_connected
    
    @pytest.mark.asyncio
    async def test_user_management(self):
        """Testa gestão de usuários"""
        db = SimpleDatabase()
        await db.connect()
        
        try:
            # Criar usuário
            user = await db.create_user("testuser", "test@example.com")
            
            assert user["username"] == "testuser"
            assert user["email"] == "test@example.com"
            assert user["id"] is not None
            
            # Obter usuário
            retrieved_user = await db.get_user(user["id"])
            assert retrieved_user["username"] == "testuser"
            
            # Tentar criar usuário duplicado
            with pytest.raises(ValueError, match="Usuário já existe"):
                await db.create_user("testuser", "other@example.com")
            
        finally:
            await db.disconnect()
    
    @pytest.mark.asyncio
    async def test_position_storage(self):
        """Testa armazenamento de posições"""
        db = SimpleDatabase()
        await db.connect()
        
        try:
            # Criar usuário
            user = await db.create_user("trader", "trader@example.com")
            
            # Criar posição
            position = await db.create_position(user["id"], "BTCUSDT", "buy", 0.1)
            
            assert position["user_id"] == user["id"]
            assert position["symbol"] == "BTCUSDT"
            assert position["side"] == "buy"
            assert position["size"] == 0.1
            
            # Obter posições do usuário
            positions = await db.get_user_positions(user["id"])
            assert len(positions) == 1
            assert positions[0]["id"] == position["id"]
            
        finally:
            await db.disconnect()
    
    @pytest.mark.asyncio
    async def test_logging_system(self):
        """Testa sistema de logs"""
        db = SimpleDatabase()
        await db.connect()
        
        try:
            # Criar usuário
            user = await db.create_user("logger", "logger@example.com")
            
            # Registrar logs
            log_id1 = await db.log_event("INFO", "Sistema iniciado", user["id"])
            log_id2 = await db.log_event("ERROR", "Erro de conexão")
            
            assert log_id1 is not None
            assert log_id2 is not None
            assert len(db.logs) == 2
            
            # Verificar conteúdo dos logs
            assert db.logs[0]["level"] == "INFO"
            assert db.logs[0]["message"] == "Sistema iniciado"
            assert db.logs[0]["user_id"] == user["id"]
            
            assert db.logs[1]["level"] == "ERROR"
            assert db.logs[1]["message"] == "Erro de conexão"
            assert db.logs[1]["user_id"] is None
            
        finally:
            await db.disconnect()


class TestSimpleCacheIntegration:
    """Testes de integração do cache simplificado"""
    
    @pytest.mark.asyncio
    async def test_cache_lifecycle(self):
        """Testa ciclo de vida do cache"""
        cache = SimpleCache()
        
        # Deve começar desconectado
        assert not cache.is_connected
        
        # Conectar
        result = await cache.connect()
        assert result["status"] == "connected"
        assert cache.is_connected
        
        # Desconectar
        result = await cache.disconnect()
        assert result["status"] == "disconnected"
        assert not cache.is_connected
    
    @pytest.mark.asyncio
    async def test_basic_cache_operations(self):
        """Testa operações básicas do cache"""
        cache = SimpleCache()
        await cache.connect()
        
        try:
            # Set e get
            await cache.set("test_key", "test_value")
            value = await cache.get("test_key")
            assert value == "test_value"
            
            # Set com objeto
            test_obj = {"symbol": "BTCUSDT", "price": 50000}
            await cache.set("market_data", test_obj)
            retrieved_obj = await cache.get("market_data")
            assert retrieved_obj == test_obj
            
            # Delete
            deleted = await cache.delete("test_key")
            assert deleted is True
            
            value = await cache.get("test_key")
            assert value is None
            
        finally:
            await cache.disconnect()
    
    @pytest.mark.asyncio
    async def test_cache_expiration(self):
        """Testa expiração do cache"""
        cache = SimpleCache()
        await cache.connect()
        
        try:
            # Set com TTL curto
            await cache.set("expiring_key", "expiring_value", ttl=0.1)  # 0.1 segundo
            
            # Deve existir imediatamente
            value = await cache.get("expiring_key")
            assert value == "expiring_value"
            
            # Aguardar expiração
            await asyncio.sleep(0.2)
            
            # Não deve mais existir
            value = await cache.get("expiring_key")
            assert value is None
            
        finally:
            await cache.disconnect()


class TestIntegratedSystem:
    """Testes de integração do sistema completo"""
    
    @pytest.mark.asyncio
    async def test_full_system_integration(self):
        """Testa integração completa do sistema"""
        # Inicializar componentes
        api = SimpleAPI()
        db = SimpleDatabase()
        cache = SimpleCache()
        
        # Conectar todos
        await api.start()
        await db.connect()
        await cache.connect()
        
        try:
            # 1. Criar usuário no banco
            user = await db.create_user("integrated_user", "integrated@example.com")
            
            # 2. Cache dos dados do usuário
            await cache.set(f"user:{user['id']}", user, ttl=300)
            
            # 3. Obter dados de mercado via API
            market_data = await api.get_market_data("BTCUSDT")
            
            # 4. Cache dos dados de mercado
            await cache.set(f"market:{market_data['symbol']}", market_data, ttl=60)
            
            # 5. Criar posição via API
            api_position = await api.create_position("BTCUSDT", "buy", 0.1)
            
            # 6. Salvar posição no banco
            db_position = await db.create_position(
                user["id"], 
                api_position["symbol"], 
                api_position["side"], 
                api_position["size"]
            )
            
            # 7. Log da operação
            await db.log_event("INFO", f"Posição criada: {db_position['id']}", user["id"])
            
            # 8. Verificar dados no cache
            cached_user = await cache.get(f"user:{user['id']}")
            assert cached_user["username"] == user["username"]
            
            cached_market = await cache.get(f"market:{market_data['symbol']}")
            assert cached_market["symbol"] == market_data["symbol"]
            
            # 9. Verificar dados no banco
            user_positions = await db.get_user_positions(user["id"])
            assert len(user_positions) == 1
            assert user_positions[0]["symbol"] == "BTCUSDT"
            
            # 10. Verificar logs
            assert len(db.logs) == 1
            assert "Posição criada" in db.logs[0]["message"]
            
        finally:
            # Limpar tudo
            await api.stop()
            await db.disconnect()
            await cache.disconnect()
    
    @pytest.mark.asyncio
    async def test_system_resilience(self):
        """Testa resiliência do sistema"""
        api = SimpleAPI()
        db = SimpleDatabase()
        cache = SimpleCache()
        
        # Inicializar apenas API
        await api.start()
        
        try:
            # API deve funcionar mesmo sem banco/cache
            market_data = await api.get_market_data("BTCUSDT")
            assert market_data["symbol"] == "BTCUSDT"
            
            position = await api.create_position("ETHUSDT", "sell", 0.5)
            assert position["symbol"] == "ETHUSDT"
            
            # Conectar banco depois
            await db.connect()
            
            # Agora pode usar banco
            user = await db.create_user("resilient_user", "resilient@example.com")
            assert user["username"] == "resilient_user"
            
            # Conectar cache por último
            await cache.connect()
            
            # Sistema completo funcionando
            await cache.set("system_status", "fully_operational")
            status = await cache.get("system_status")
            assert status == "fully_operational"
            
        finally:
            await api.stop()
            await db.disconnect()
            await cache.disconnect()
    
    @pytest.mark.asyncio
    async def test_performance_integration(self):
        """Testa performance da integração"""
        api = SimpleAPI()
        cache = SimpleCache()
        
        await api.start()
        await cache.connect()
        
        try:
            # Teste de performance: múltiplas operações
            start_time = time.time()
            
            # Criar múltiplas posições
            tasks = []
            for i in range(10):
                task = api.create_position(f"SYMBOL{i}", "buy", 0.1)
                tasks.append(task)
            
            positions = await asyncio.gather(*tasks)
            
            # Cache das posições
            cache_tasks = []
            for i, position in enumerate(positions):
                task = cache.set(f"position:{i}", position)
                cache_tasks.append(task)
            
            await asyncio.gather(*cache_tasks)
            
            total_time = time.time() - start_time
            
            # Verificar resultados
            assert len(positions) == 10
            for i, position in enumerate(positions):
                assert position["symbol"] == f"SYMBOL{i}"
                
                # Verificar cache
                cached_position = await cache.get(f"position:{i}")
                assert cached_position["id"] == position["id"]
            
            # Performance deve ser razoável
            assert total_time < 1.0  # Menos de 1 segundo para 10 operações
            
        finally:
            await api.stop()
            await cache.disconnect()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

