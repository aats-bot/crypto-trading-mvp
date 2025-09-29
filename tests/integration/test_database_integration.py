"""
Testes de integração do banco de dados e cache Redis
Compatível com Windows - Semana 2 da Onda 1
"""
import pytest
import asyncio
import json
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
import sys
import os
import sqlite3
from typing import Dict, List, Optional, Any

# Adicionar o diretório do projeto ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))


class DatabaseManager:
    """
    Gerenciador de banco de dados para o sistema de trading
    Usando SQLite para compatibilidade com Windows
    """
    
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self.connection = None
        self.is_connected = False
    
    async def connect(self):
        """Conectar ao banco de dados"""
        try:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row  # Para acessar colunas por nome
            self.is_connected = True
            await self._create_tables()
            return {"status": "connected", "db_path": self.db_path}
        except Exception as e:
            raise ConnectionError(f"Erro ao conectar ao banco: {e}")
    
    async def disconnect(self):
        """Desconectar do banco de dados"""
        if self.connection:
            self.connection.close()
            self.connection = None
        self.is_connected = False
        return {"status": "disconnected"}
    
    def _check_connection(self):
        """Verificar se está conectado"""
        if not self.is_connected or not self.connection:
            raise ConnectionError("Banco de dados não está conectado")
    
    async def _create_tables(self):
        """Criar tabelas necessárias"""
        cursor = self.connection.cursor()
        
        # Tabela de usuários
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                api_key TEXT,
                api_secret TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabela de estratégias
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS strategies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                parameters TEXT,  -- JSON
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        # Tabela de posições
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                strategy_id INTEGER NOT NULL,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,  -- 'buy' ou 'sell'
                size REAL NOT NULL,
                entry_price REAL NOT NULL,
                exit_price REAL,
                status TEXT DEFAULT 'open',  -- 'open', 'closed', 'cancelled'
                pnl REAL DEFAULT 0,
                fees REAL DEFAULT 0,
                opened_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                closed_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (strategy_id) REFERENCES strategies (id)
            )
        """)
        
        # Tabela de ordens
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                position_id INTEGER,
                exchange_order_id TEXT,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                type TEXT NOT NULL,  -- 'market', 'limit', 'stop'
                quantity REAL NOT NULL,
                price REAL,
                filled_quantity REAL DEFAULT 0,
                status TEXT DEFAULT 'pending',  -- 'pending', 'filled', 'cancelled', 'rejected'
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (position_id) REFERENCES positions (id)
            )
        """)
        
        # Tabela de dados de mercado (cache)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS market_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                timestamp INTEGER NOT NULL,
                open_price REAL NOT NULL,
                high_price REAL NOT NULL,
                low_price REAL NOT NULL,
                close_price REAL NOT NULL,
                volume REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(symbol, timeframe, timestamp)
            )
        """)
        
        # Tabela de logs do sistema
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level TEXT NOT NULL,  -- 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
                message TEXT NOT NULL,
                module TEXT,
                user_id INTEGER,
                additional_data TEXT,  -- JSON
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        self.connection.commit()
    
    # Métodos para usuários
    async def create_user(self, username: str, email: str, password_hash: str, api_key: str = None, api_secret: str = None):
        """Criar novo usuário"""
        self._check_connection()
        
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, api_key, api_secret)
                VALUES (?, ?, ?, ?, ?)
            """, (username, email, password_hash, api_key, api_secret))
            
            user_id = cursor.lastrowid
            self.connection.commit()
            
            return await self.get_user_by_id(user_id)
        except sqlite3.IntegrityError as e:
            raise ValueError(f"Usuário já existe: {e}")
    
    async def get_user_by_id(self, user_id: int):
        """Obter usuário por ID"""
        self._check_connection()
        
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
    
    async def get_user_by_username(self, username: str):
        """Obter usuário por username"""
        self._check_connection()
        
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
    
    async def update_user(self, user_id: int, **kwargs):
        """Atualizar usuário"""
        self._check_connection()
        
        if not kwargs:
            return await self.get_user_by_id(user_id)
        
        # Construir query dinamicamente
        set_clauses = []
        values = []
        
        for key, value in kwargs.items():
            if key in ['username', 'email', 'password_hash', 'api_key', 'api_secret', 'is_active']:
                set_clauses.append(f"{key} = ?")
                values.append(value)
        
        if not set_clauses:
            return await self.get_user_by_id(user_id)
        
        set_clauses.append("updated_at = CURRENT_TIMESTAMP")
        values.append(user_id)
        
        query = f"UPDATE users SET {', '.join(set_clauses)} WHERE id = ?"
        
        cursor = self.connection.cursor()
        cursor.execute(query, values)
        self.connection.commit()
        
        return await self.get_user_by_id(user_id)
    
    # Métodos para estratégias
    async def create_strategy(self, user_id: int, name: str, strategy_type: str, parameters: dict = None):
        """Criar nova estratégia"""
        self._check_connection()
        
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO strategies (user_id, name, type, parameters)
            VALUES (?, ?, ?, ?)
        """, (user_id, name, strategy_type, json.dumps(parameters or {})))
        
        strategy_id = cursor.lastrowid
        self.connection.commit()
        
        return await self.get_strategy_by_id(strategy_id)
    
    async def get_strategy_by_id(self, strategy_id: int):
        """Obter estratégia por ID"""
        self._check_connection()
        
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM strategies WHERE id = ?", (strategy_id,))
        row = cursor.fetchone()
        
        if row:
            strategy = dict(row)
            strategy['parameters'] = json.loads(strategy['parameters'])
            return strategy
        return None
    
    async def get_user_strategies(self, user_id: int, active_only: bool = True):
        """Obter estratégias do usuário"""
        self._check_connection()
        
        cursor = self.connection.cursor()
        if active_only:
            cursor.execute("SELECT * FROM strategies WHERE user_id = ? AND is_active = 1", (user_id,))
        else:
            cursor.execute("SELECT * FROM strategies WHERE user_id = ?", (user_id,))
        
        rows = cursor.fetchall()
        strategies = []
        
        for row in rows:
            strategy = dict(row)
            strategy['parameters'] = json.loads(strategy['parameters'])
            strategies.append(strategy)
        
        return strategies
    
    # Métodos para posições
    async def create_position(self, user_id: int, strategy_id: int, symbol: str, side: str, size: float, entry_price: float):
        """Criar nova posição"""
        self._check_connection()
        
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO positions (user_id, strategy_id, symbol, side, size, entry_price)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, strategy_id, symbol, side, size, entry_price))
        
        position_id = cursor.lastrowid
        self.connection.commit()
        
        return await self.get_position_by_id(position_id)
    
    async def get_position_by_id(self, position_id: int):
        """Obter posição por ID"""
        self._check_connection()
        
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM positions WHERE id = ?", (position_id,))
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
    
    async def get_user_positions(self, user_id: int, status: str = None):
        """Obter posições do usuário"""
        self._check_connection()
        
        cursor = self.connection.cursor()
        if status:
            cursor.execute("SELECT * FROM positions WHERE user_id = ? AND status = ?", (user_id, status))
        else:
            cursor.execute("SELECT * FROM positions WHERE user_id = ?", (user_id,))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    async def close_position(self, position_id: int, exit_price: float, pnl: float = 0, fees: float = 0):
        """Fechar posição"""
        self._check_connection()
        
        cursor = self.connection.cursor()
        cursor.execute("""
            UPDATE positions 
            SET exit_price = ?, pnl = ?, fees = ?, status = 'closed', closed_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (exit_price, pnl, fees, position_id))
        
        self.connection.commit()
        return await self.get_position_by_id(position_id)
    
    # Métodos para dados de mercado
    async def store_market_data(self, symbol: str, timeframe: str, candles: List[Dict]):
        """Armazenar dados de mercado"""
        self._check_connection()
        
        cursor = self.connection.cursor()
        
        for candle in candles:
            cursor.execute("""
                INSERT OR REPLACE INTO market_data 
                (symbol, timeframe, timestamp, open_price, high_price, low_price, close_price, volume)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                symbol, timeframe, candle['timestamp'],
                candle['open'], candle['high'], candle['low'], candle['close'], candle['volume']
            ))
        
        self.connection.commit()
        return len(candles)
    
    async def get_market_data(self, symbol: str, timeframe: str, limit: int = 100, start_time: int = None):
        """Obter dados de mercado"""
        self._check_connection()
        
        cursor = self.connection.cursor()
        
        if start_time:
            cursor.execute("""
                SELECT * FROM market_data 
                WHERE symbol = ? AND timeframe = ? AND timestamp >= ?
                ORDER BY timestamp DESC LIMIT ?
            """, (symbol, timeframe, start_time, limit))
        else:
            cursor.execute("""
                SELECT * FROM market_data 
                WHERE symbol = ? AND timeframe = ?
                ORDER BY timestamp DESC LIMIT ?
            """, (symbol, timeframe, limit))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    # Métodos para logs
    async def log_message(self, level: str, message: str, module: str = None, user_id: int = None, additional_data: dict = None):
        """Registrar log do sistema"""
        self._check_connection()
        
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO system_logs (level, message, module, user_id, additional_data)
            VALUES (?, ?, ?, ?, ?)
        """, (level, message, module, user_id, json.dumps(additional_data or {})))
        
        self.connection.commit()
        return cursor.lastrowid
    
    async def get_logs(self, level: str = None, module: str = None, user_id: int = None, limit: int = 100):
        """Obter logs do sistema"""
        self._check_connection()
        
        cursor = self.connection.cursor()
        
        conditions = []
        params = []
        
        if level:
            conditions.append("level = ?")
            params.append(level)
        
        if module:
            conditions.append("module = ?")
            params.append(module)
        
        if user_id:
            conditions.append("user_id = ?")
            params.append(user_id)
        
        where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
        params.append(limit)
        
        query = f"SELECT * FROM system_logs{where_clause} ORDER BY created_at DESC LIMIT ?"
        cursor.execute(query, params)
        
        rows = cursor.fetchall()
        logs = []
        
        for row in rows:
            log = dict(row)
            log['additional_data'] = json.loads(log['additional_data'])
            logs.append(log)
        
        return logs


class RedisCache:
    """
    Simulação de cache Redis para Windows
    Usando dicionário em memória para compatibilidade
    """
    
    def __init__(self):
        self.cache = {}
        self.expiry_times = {}
        self.is_connected = False
    
    async def connect(self):
        """Conectar ao Redis (simulado)"""
        self.is_connected = True
        return {"status": "connected", "type": "simulated"}
    
    async def disconnect(self):
        """Desconectar do Redis"""
        self.cache.clear()
        self.expiry_times.clear()
        self.is_connected = False
        return {"status": "disconnected"}
    
    def _check_connection(self):
        """Verificar se está conectado"""
        if not self.is_connected:
            raise ConnectionError("Cache Redis não está conectado")
    
    def _is_expired(self, key: str) -> bool:
        """Verificar se a chave expirou"""
        if key in self.expiry_times:
            return time.time() > self.expiry_times[key]
        return False
    
    def _cleanup_expired(self):
        """Limpar chaves expiradas"""
        current_time = time.time()
        expired_keys = [key for key, expiry in self.expiry_times.items() if current_time > expiry]
        
        for key in expired_keys:
            self.cache.pop(key, None)
            self.expiry_times.pop(key, None)
    
    async def set(self, key: str, value: Any, ttl: int = None):
        """Definir valor no cache"""
        self._check_connection()
        self._cleanup_expired()
        
        self.cache[key] = json.dumps(value) if not isinstance(value, str) else value
        
        if ttl:
            self.expiry_times[key] = time.time() + ttl
        
        return True
    
    async def get(self, key: str):
        """Obter valor do cache"""
        self._check_connection()
        self._cleanup_expired()
        
        if key in self.cache and not self._is_expired(key):
            value = self.cache[key]
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        
        return None
    
    async def delete(self, key: str):
        """Deletar chave do cache"""
        self._check_connection()
        
        deleted = key in self.cache
        self.cache.pop(key, None)
        self.expiry_times.pop(key, None)
        
        return deleted
    
    async def exists(self, key: str):
        """Verificar se chave existe"""
        self._check_connection()
        self._cleanup_expired()
        
        return key in self.cache and not self._is_expired(key)
    
    async def keys(self, pattern: str = "*"):
        """Listar chaves (simulado)"""
        self._check_connection()
        self._cleanup_expired()
        
        if pattern == "*":
            return list(self.cache.keys())
        
        # Simulação simples de pattern matching
        import fnmatch
        return [key for key in self.cache.keys() if fnmatch.fnmatch(key, pattern)]
    
    async def flushall(self):
        """Limpar todo o cache"""
        self._check_connection()
        
        self.cache.clear()
        self.expiry_times.clear()
        return True


class TestDatabaseIntegration:
    """Testes de integração do banco de dados"""
    
    @pytest.fixture
    async def db(self):
        """Fixture do banco de dados para testes"""
        db = DatabaseManager(":memory:")  # Banco em memória para testes
        await db.connect()
        yield db
        await db.disconnect()
    
    @pytest.mark.asyncio
    async def test_database_connection(self):
        """Testa conexão e desconexão do banco"""
        db = DatabaseManager(":memory:")
        
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
    async def test_user_management(self, db):
        """Testa gestão de usuários"""
        # Criar usuário
        user = await db.create_user(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        
        assert user["username"] == "testuser"
        assert user["email"] == "test@example.com"
        assert user["is_active"] == 1
        assert user["id"] is not None
        
        # Obter usuário por ID
        retrieved_user = await db.get_user_by_id(user["id"])
        assert retrieved_user["username"] == "testuser"
        
        # Obter usuário por username
        retrieved_user = await db.get_user_by_username("testuser")
        assert retrieved_user["email"] == "test@example.com"
        
        # Atualizar usuário
        updated_user = await db.update_user(user["id"], email="newemail@example.com")
        assert updated_user["email"] == "newemail@example.com"
        
        # Tentar criar usuário duplicado
        with pytest.raises(ValueError, match="Usuário já existe"):
            await db.create_user("testuser", "other@example.com", "hash")
    
    @pytest.mark.asyncio
    async def test_strategy_management(self, db):
        """Testa gestão de estratégias"""
        # Criar usuário primeiro
        user = await db.create_user("trader", "trader@example.com", "hash")
        
        # Criar estratégia
        strategy_params = {
            "risk_per_trade": 0.02,
            "max_positions": 5,
            "indicators": ["EMA", "RSI"]
        }
        
        strategy = await db.create_strategy(
            user_id=user["id"],
            name="PPP Vishva Strategy",
            strategy_type="ppp_vishva",
            parameters=strategy_params
        )
        
        assert strategy["name"] == "PPP Vishva Strategy"
        assert strategy["type"] == "ppp_vishva"
        assert strategy["parameters"] == strategy_params
        assert strategy["is_active"] == 1
        
        # Obter estratégia por ID
        retrieved_strategy = await db.get_strategy_by_id(strategy["id"])
        assert retrieved_strategy["parameters"]["risk_per_trade"] == 0.02
        
        # Obter estratégias do usuário
        user_strategies = await db.get_user_strategies(user["id"])
        assert len(user_strategies) == 1
        assert user_strategies[0]["name"] == "PPP Vishva Strategy"
    
    @pytest.mark.asyncio
    async def test_position_management(self, db):
        """Testa gestão de posições"""
        # Criar usuário e estratégia
        user = await db.create_user("trader", "trader@example.com", "hash")
        strategy = await db.create_strategy(user["id"], "Test Strategy", "test", {})
        
        # Criar posição
        position = await db.create_position(
            user_id=user["id"],
            strategy_id=strategy["id"],
            symbol="BTCUSDT",
            side="buy",
            size=0.1,
            entry_price=50000.0
        )
        
        assert position["symbol"] == "BTCUSDT"
        assert position["side"] == "buy"
        assert position["size"] == 0.1
        assert position["entry_price"] == 50000.0
        assert position["status"] == "open"
        
        # Obter posição por ID
        retrieved_position = await db.get_position_by_id(position["id"])
        assert retrieved_position["symbol"] == "BTCUSDT"
        
        # Obter posições do usuário
        user_positions = await db.get_user_positions(user["id"])
        assert len(user_positions) == 1
        
        # Obter apenas posições abertas
        open_positions = await db.get_user_positions(user["id"], status="open")
        assert len(open_positions) == 1
        
        # Fechar posição
        closed_position = await db.close_position(
            position_id=position["id"],
            exit_price=51000.0,
            pnl=100.0,
            fees=5.0
        )
        
        assert closed_position["status"] == "closed"
        assert closed_position["exit_price"] == 51000.0
        assert closed_position["pnl"] == 100.0
        assert closed_position["fees"] == 5.0
        assert closed_position["closed_at"] is not None
        
        # Verificar que não há mais posições abertas
        open_positions = await db.get_user_positions(user["id"], status="open")
        assert len(open_positions) == 0
    
    @pytest.mark.asyncio
    async def test_market_data_storage(self, db):
        """Testa armazenamento de dados de mercado"""
        # Dados de mercado simulados
        candles = [
            {
                "timestamp": int(time.time() * 1000) - 60000,
                "open": 50000.0,
                "high": 50100.0,
                "low": 49900.0,
                "close": 50050.0,
                "volume": 1.5
            },
            {
                "timestamp": int(time.time() * 1000),
                "open": 50050.0,
                "high": 50200.0,
                "low": 50000.0,
                "close": 50150.0,
                "volume": 2.1
            }
        ]
        
        # Armazenar dados
        stored_count = await db.store_market_data("BTCUSDT", "1m", candles)
        assert stored_count == 2
        
        # Recuperar dados
        retrieved_data = await db.get_market_data("BTCUSDT", "1m", limit=10)
        assert len(retrieved_data) == 2
        
        # Verificar ordem (mais recente primeiro)
        assert retrieved_data[0]["timestamp"] > retrieved_data[1]["timestamp"]
        assert retrieved_data[0]["close"] == 50150.0
        
        # Recuperar dados com filtro de tempo
        start_time = int(time.time() * 1000) - 30000  # Últimos 30 segundos
        recent_data = await db.get_market_data("BTCUSDT", "1m", start_time=start_time)
        assert len(recent_data) == 1
        assert recent_data[0]["close"] == 50150.0
    
    @pytest.mark.asyncio
    async def test_logging_system(self, db):
        """Testa sistema de logs"""
        # Criar usuário
        user = await db.create_user("logger", "logger@example.com", "hash")
        
        # Registrar logs
        log_id1 = await db.log_message("INFO", "Sistema iniciado", "main", user["id"])
        log_id2 = await db.log_message("ERROR", "Erro de conexão", "api", user["id"], {"error_code": 500})
        log_id3 = await db.log_message("DEBUG", "Debug message", "strategy")
        
        assert log_id1 is not None
        assert log_id2 is not None
        assert log_id3 is not None
        
        # Obter todos os logs
        all_logs = await db.get_logs(limit=10)
        assert len(all_logs) == 3
        
        # Logs devem estar ordenados por data (mais recente primeiro)
        assert all_logs[0]["id"] == log_id3
        
        # Obter logs por nível
        error_logs = await db.get_logs(level="ERROR")
        assert len(error_logs) == 1
        assert error_logs[0]["message"] == "Erro de conexão"
        assert error_logs[0]["additional_data"]["error_code"] == 500
        
        # Obter logs por módulo
        api_logs = await db.get_logs(module="api")
        assert len(api_logs) == 1
        assert api_logs[0]["level"] == "ERROR"
        
        # Obter logs por usuário
        user_logs = await db.get_logs(user_id=user["id"])
        assert len(user_logs) == 2


class TestRedisIntegration:
    """Testes de integração do cache Redis"""
    
    @pytest.fixture
    async def redis(self):
        """Fixture do Redis para testes"""
        redis = RedisCache()
        await redis.connect()
        yield redis
        await redis.disconnect()
    
    @pytest.mark.asyncio
    async def test_redis_connection(self):
        """Testa conexão e desconexão do Redis"""
        redis = RedisCache()
        
        # Deve começar desconectado
        assert not redis.is_connected
        
        # Conectar
        result = await redis.connect()
        assert result["status"] == "connected"
        assert redis.is_connected
        
        # Desconectar
        result = await redis.disconnect()
        assert result["status"] == "disconnected"
        assert not redis.is_connected
    
    @pytest.mark.asyncio
    async def test_basic_cache_operations(self, redis):
        """Testa operações básicas do cache"""
        # Set e get string
        await redis.set("test_key", "test_value")
        value = await redis.get("test_key")
        assert value == "test_value"
        
        # Set e get objeto
        test_obj = {"symbol": "BTCUSDT", "price": 50000}
        await redis.set("market_data", test_obj)
        retrieved_obj = await redis.get("market_data")
        assert retrieved_obj == test_obj
        
        # Verificar existência
        exists = await redis.exists("test_key")
        assert exists is True
        
        exists = await redis.exists("nonexistent_key")
        assert exists is False
        
        # Deletar chave
        deleted = await redis.delete("test_key")
        assert deleted is True
        
        # Verificar que foi deletada
        value = await redis.get("test_key")
        assert value is None
    
    @pytest.mark.asyncio
    async def test_cache_expiration(self, redis):
        """Testa expiração do cache"""
        # Set com TTL
        await redis.set("expiring_key", "expiring_value", ttl=1)  # 1 segundo
        
        # Deve existir imediatamente
        value = await redis.get("expiring_key")
        assert value == "expiring_value"
        
        # Aguardar expiração
        await asyncio.sleep(1.1)
        
        # Não deve mais existir
        value = await redis.get("expiring_key")
        assert value is None
        
        exists = await redis.exists("expiring_key")
        assert exists is False
    
    @pytest.mark.asyncio
    async def test_cache_keys_listing(self, redis):
        """Testa listagem de chaves"""
        # Adicionar várias chaves
        await redis.set("user:1", {"name": "Alice"})
        await redis.set("user:2", {"name": "Bob"})
        await redis.set("market:BTCUSDT", {"price": 50000})
        await redis.set("market:ETHUSDT", {"price": 3000})
        
        # Listar todas as chaves
        all_keys = await redis.keys("*")
        assert len(all_keys) == 4
        
        # Listar chaves com padrão
        user_keys = await redis.keys("user:*")
        assert len(user_keys) == 2
        assert "user:1" in user_keys
        assert "user:2" in user_keys
        
        market_keys = await redis.keys("market:*")
        assert len(market_keys) == 2
        assert "market:BTCUSDT" in market_keys
        assert "market:ETHUSDT" in market_keys
    
    @pytest.mark.asyncio
    async def test_cache_flush(self, redis):
        """Testa limpeza completa do cache"""
        # Adicionar dados
        await redis.set("key1", "value1")
        await redis.set("key2", "value2")
        await redis.set("key3", "value3")
        
        # Verificar que existem
        keys = await redis.keys("*")
        assert len(keys) == 3
        
        # Limpar tudo
        result = await redis.flushall()
        assert result is True
        
        # Verificar que foi limpo
        keys = await redis.keys("*")
        assert len(keys) == 0
    
    @pytest.mark.asyncio
    async def test_connection_required_operations(self):
        """Testa operações que requerem conexão"""
        redis = RedisCache()
        
        # Tentar operações sem conectar
        with pytest.raises(ConnectionError, match="Cache Redis não está conectado"):
            await redis.set("key", "value")
        
        with pytest.raises(ConnectionError, match="Cache Redis não está conectado"):
            await redis.get("key")
        
        with pytest.raises(ConnectionError, match="Cache Redis não está conectado"):
            await redis.delete("key")


class TestDatabaseCacheIntegration:
    """Testes de integração entre banco de dados e cache"""
    
    @pytest.fixture
    async def db_and_cache(self):
        """Fixture com banco e cache para testes"""
        db = DatabaseManager(":memory:")
        redis = RedisCache()
        
        await db.connect()
        await redis.connect()
        
        yield db, redis
        
        await db.disconnect()
        await redis.disconnect()
    
    @pytest.mark.asyncio
    async def test_market_data_caching_strategy(self, db_and_cache):
        """Testa estratégia de cache para dados de mercado"""
        db, redis = db_and_cache
        
        # Simular dados de mercado
        symbol = "BTCUSDT"
        timeframe = "1m"
        
        candles = [
            {
                "timestamp": int(time.time() * 1000),
                "open": 50000.0,
                "high": 50100.0,
                "low": 49900.0,
                "close": 50050.0,
                "volume": 1.5
            }
        ]
        
        # Armazenar no banco
        await db.store_market_data(symbol, timeframe, candles)
        
        # Armazenar no cache
        cache_key = f"market_data:{symbol}:{timeframe}"
        await redis.set(cache_key, candles, ttl=60)  # Cache por 1 minuto
        
        # Recuperar do cache (deve ser mais rápido)
        start_time = time.time()
        cached_data = await redis.get(cache_key)
        cache_time = time.time() - start_time
        
        # Recuperar do banco
        start_time = time.time()
        db_data = await db.get_market_data(symbol, timeframe, limit=1)
        db_time = time.time() - start_time
        
        # Verificar que os dados são equivalentes
        assert len(cached_data) == len(db_data)
        assert cached_data[0]["close"] == db_data[0]["close_price"]
        
        # Cache deve ser mais rápido (em teoria)
        # Nota: Em testes unitários a diferença pode ser mínima
        assert cache_time <= db_time + 0.01  # Tolerância para variações
    
    @pytest.mark.asyncio
    async def test_user_session_caching(self, db_and_cache):
        """Testa cache de sessões de usuário"""
        db, redis = db_and_cache
        
        # Criar usuário no banco
        user = await db.create_user("cached_user", "cached@example.com", "hash")
        
        # Simular sessão no cache
        session_data = {
            "user_id": user["id"],
            "username": user["username"],
            "login_time": datetime.now().isoformat(),
            "permissions": ["trade", "view_positions"]
        }
        
        session_key = f"session:user:{user['id']}"
        await redis.set(session_key, session_data, ttl=3600)  # 1 hora
        
        # Recuperar sessão do cache
        cached_session = await redis.get(session_key)
        assert cached_session["user_id"] == user["id"]
        assert cached_session["username"] == user["username"]
        assert "trade" in cached_session["permissions"]
        
        # Verificar que usuário existe no banco
        db_user = await db.get_user_by_id(user["id"])
        assert db_user["username"] == cached_session["username"]
    
    @pytest.mark.asyncio
    async def test_cache_invalidation_on_update(self, db_and_cache):
        """Testa invalidação de cache ao atualizar dados"""
        db, redis = db_and_cache
        
        # Criar usuário
        user = await db.create_user("test_user", "test@example.com", "hash")
        
        # Cache dos dados do usuário
        cache_key = f"user:{user['id']}"
        await redis.set(cache_key, user, ttl=300)
        
        # Verificar que está no cache
        cached_user = await redis.get(cache_key)
        assert cached_user["email"] == "test@example.com"
        
        # Atualizar usuário no banco
        updated_user = await db.update_user(user["id"], email="updated@example.com")
        
        # Invalidar cache (simular comportamento real)
        await redis.delete(cache_key)
        
        # Verificar que cache foi invalidado
        cached_user = await redis.get(cache_key)
        assert cached_user is None
        
        # Dados atualizados devem estar no banco
        db_user = await db.get_user_by_id(user["id"])
        assert db_user["email"] == "updated@example.com"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

