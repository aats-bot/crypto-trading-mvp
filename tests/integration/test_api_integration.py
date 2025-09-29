"""
Testes de integração da API do sistema de trading
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

# Adicionar o diretório do projeto ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

# Importar a estratégia
from tests.unit.test_ppp_vishva_strategy import PPPVishvaStrategy
class TradingAPI:
    """
    Simulação da API principal do sistema de trading
    Baseada na estrutura do main.py analisado anteriormente
    """
    
    def __init__(self):
        self.is_running = False
        self.strategies = {}
        self.active_positions = {}
        self.market_data_cache = {}
        self.user_sessions = {}
        self.config = {
            'max_positions': 5,
            'risk_per_trade': 0.02,
            'api_timeout': 30,
            'cache_ttl': 60
        }
    
    async def start_system(self):
        """Inicializar sistema de trading"""
        self.is_running = True
        await self._initialize_strategies()
        await self._connect_market_data()
        return {"status": "success", "message": "Sistema iniciado"}
    
    async def stop_system(self):
        """Parar sistema de trading"""
        await self._close_positions()
        await self._disconnect_market_data()
        self.is_running = False
        return {"status": "success", "message": "Sistema parado"}
    
    async def _initialize_strategies(self):
        """Inicializar estratégias de trading"""
        from test_ppp_vishva_strategy import PPPVishvaStrategy
        
        self.strategies = {
            'ppp_vishva': PPPVishvaStrategy(),
            'sma_cross': Mock(),  # Simular outras estratégias
            'rsi_divergence': Mock()
        }
    
    async def _connect_market_data(self):
        """Conectar ao feed de dados de mercado"""
        # Simular conexão com Bybit
        await asyncio.sleep(0.1)  # Simular latência
        return True
    
    async def _disconnect_market_data(self):
        """Desconectar do feed de dados"""
        await asyncio.sleep(0.1)
        return True
    
    async def _close_positions(self):
        """Fechar todas as posições abertas"""
        for position_id in list(self.active_positions.keys()):
            await self.close_position(position_id)
    
    async def get_market_data(self, symbol: str, timeframe: str = '1m', limit: int = 100):
        """Obter dados de mercado"""
        cache_key = f"{symbol}_{timeframe}_{limit}"
        
        # Verificar cache
        if cache_key in self.market_data_cache:
            cache_time, data = self.market_data_cache[cache_key]
            if time.time() - cache_time < self.config['cache_ttl']:
                return data
        
        # Simular chamada à API externa
        await asyncio.sleep(0.05)  # Simular latência de rede
        
        # Gerar dados simulados
        data = self._generate_mock_market_data(symbol, limit)
        
        # Armazenar no cache
        self.market_data_cache[cache_key] = (time.time(), data)
        
        return data
    
    def _generate_mock_market_data(self, symbol: str, limit: int):
        """Gerar dados de mercado simulados"""
        import random
        
        base_price = 50000 if symbol == 'BTCUSDT' else 3000
        data = []
        
        for i in range(limit):
            timestamp = int(time.time() * 1000) - (limit - i) * 60000  # 1 minuto por candle
            
            # Simular movimento de preço
            change = random.uniform(-0.01, 0.01)  # ±1%
            base_price *= (1 + change)
            
            volatility = random.uniform(0.001, 0.005)  # 0.1% a 0.5%
            
            candle = {
                'timestamp': timestamp,
                'open': base_price,
                'high': base_price * (1 + volatility),
                'low': base_price * (1 - volatility),
                'close': base_price * (1 + change/2),
                'volume': random.uniform(100, 1000)
            }
            data.append(candle)
        
        return data
    
    async def analyze_market(self, symbol: str, strategy: str = 'ppp_vishva'):
        """Analisar mercado usando estratégia específica"""
        if not self.is_running:
            raise RuntimeError("Sistema não está rodando")
        
        if strategy not in self.strategies:
            raise ValueError(f"Estratégia '{strategy}' não encontrada")
        
        # Obter dados de mercado
        market_data = await self.get_market_data(symbol)
        
        if not market_data:
            raise ValueError("Dados de mercado não disponíveis")
        
        # Analisar com a estratégia
        strategy_obj = self.strategies[strategy]
        
        if hasattr(strategy_obj, 'generate_signal'):
            last_candle = market_data[-1]
            signal = strategy_obj.generate_signal(last_candle)
        else:
            signal = 'hold'  # Mock para outras estratégias
        
        return {
            'symbol': symbol,
            'strategy': strategy,
            'signal': signal,
            'timestamp': datetime.now().isoformat(),
            'market_data_points': len(market_data)
        }
    
    async def create_position(self, symbol: str, side: str, size: float, strategy: str):
        """Criar nova posição"""
        if not self.is_running:
            raise RuntimeError("Sistema não está rodando")
        
        if len(self.active_positions) >= self.config['max_positions']:
            raise ValueError("Máximo de posições atingido")
        
        position_id = f"{symbol}_{side}_{int(time.time())}"
        
        # Simular criação de posição
        await asyncio.sleep(0.1)
        
        position = {
            'id': position_id,
            'symbol': symbol,
            'side': side,
            'size': size,
            'strategy': strategy,
            'entry_price': 50000,  # Simular preço de entrada
            'created_at': datetime.now().isoformat(),
            'status': 'open'
        }
        
        self.active_positions[position_id] = position
        
        return position
    
    async def close_position(self, position_id: str):
        """Fechar posição"""
        if position_id not in self.active_positions:
            raise ValueError(f"Posição '{position_id}' não encontrada")
        
        # Simular fechamento
        await asyncio.sleep(0.1)
        
        position = self.active_positions[position_id]
        position['status'] = 'closed'
        position['closed_at'] = datetime.now().isoformat()
        position['exit_price'] = 50100  # Simular preço de saída
        
        # Remover das posições ativas
        del self.active_positions[position_id]
        
        return position
    
    async def get_positions(self):
        """Obter todas as posições ativas"""
        return list(self.active_positions.values())
    
    async def authenticate_user(self, api_key: str, api_secret: str):
        """Autenticar usuário"""
        # Simular autenticação
        await asyncio.sleep(0.05)
        
        if api_key == 'test_key' and api_secret == 'test_secret':
            session_id = f"session_{int(time.time())}"
            self.user_sessions[session_id] = {
                'api_key': api_key,
                'created_at': datetime.now().isoformat(),
                'last_activity': datetime.now().isoformat()
            }
            return {'session_id': session_id, 'status': 'authenticated'}
        else:
            raise ValueError("Credenciais inválidas")
    
    async def get_system_status(self):
        """Obter status do sistema"""
        return {
            'is_running': self.is_running,
            'strategies_loaded': len(self.strategies),
            'active_positions': len(self.active_positions),
            'cache_entries': len(self.market_data_cache),
            'active_sessions': len(self.user_sessions),
            'uptime': time.time() if self.is_running else 0,
            'config': self.config
        }


class TestAPIIntegration:
    """Testes de integração da API principal"""
    
    @pytest_asyncio.fixture
    async def api(self):
        """Fixture da API para testes"""
        api = TradingAPI()
        await api.start_system()
        try:
            yield api
        finally:
            await api.stop_system()
    
    @pytest.mark.asyncio
    async def test_system_startup_shutdown(self):
        """Testa inicialização e parada do sistema"""
        api = TradingAPI()
        
        # Sistema deve começar parado
        assert not api.is_running
        
        # Inicializar sistema
        result = await api.start_system()
        assert result['status'] == 'success'
        assert api.is_running
        
        # Parar sistema
        result = await api.stop_system()
        assert result['status'] == 'success'
        assert not api.is_running
    
    @pytest.mark.asyncio
    async def test_market_data_retrieval(self, api):
        """Testa obtenção de dados de mercado"""
        symbol = 'BTCUSDT'
        
        # Obter dados de mercado
        data = await api.get_market_data(symbol, '1m', 100)
        
        assert isinstance(data, list)
        assert len(data) == 100
        
        # Verificar estrutura dos dados
        candle = data[0]
        required_fields = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        for field in required_fields:
            assert field in candle
            assert isinstance(candle[field], (int, float))
    
    @pytest.mark.asyncio
    async def test_market_data_caching(self, api):
        """Testa cache de dados de mercado"""
        symbol = 'BTCUSDT'
        
        # Primeira chamada
        start_time = time.time()
        data1 = await api.get_market_data(symbol, '1m', 50)
        first_call_time = time.time() - start_time
        
        # Segunda chamada (deve usar cache)
        start_time = time.time()
        data2 = await api.get_market_data(symbol, '1m', 50)
        second_call_time = time.time() - start_time
        
        # Dados devem ser iguais
        assert data1 == data2
        
        # Segunda chamada deve ser mais rápida (cache)
        assert second_call_time < first_call_time
    
    @pytest.mark.asyncio
    async def test_market_analysis_integration(self, api):
        """Testa integração da análise de mercado"""
        symbol = 'BTCUSDT'
        
        # Analisar mercado
        analysis = await api.analyze_market(symbol, 'ppp_vishva')
        
        assert analysis['symbol'] == symbol
        assert analysis['strategy'] == 'ppp_vishva'
        assert analysis['signal'] in ['buy', 'sell', 'hold']
        assert 'timestamp' in analysis
        assert analysis['market_data_points'] > 0
    
    @pytest.mark.asyncio
    async def test_position_management_flow(self, api):
        """Testa fluxo completo de gestão de posições"""
        symbol = 'BTCUSDT'
        
        # Verificar posições iniciais (deve estar vazio)
        positions = await api.get_positions()
        assert len(positions) == 0
        
        # Criar posição
        position = await api.create_position(symbol, 'buy', 0.1, 'ppp_vishva')
        
        assert position['symbol'] == symbol
        assert position['side'] == 'buy'
        assert position['size'] == 0.1
        assert position['strategy'] == 'ppp_vishva'
        assert position['status'] == 'open'
        
        # Verificar posições ativas
        positions = await api.get_positions()
        assert len(positions) == 1
        assert positions[0]['id'] == position['id']
        
        # Fechar posição
        closed_position = await api.close_position(position['id'])
        
        assert closed_position['status'] == 'closed'
        assert 'closed_at' in closed_position
        assert 'exit_price' in closed_position
        
        # Verificar que não há mais posições ativas
        positions = await api.get_positions()
        assert len(positions) == 0
    
    @pytest.mark.asyncio
    async def test_authentication_flow(self, api):
        """Testa fluxo de autenticação"""
        # Autenticação válida
        auth_result = await api.authenticate_user('test_key', 'test_secret')
        
        assert auth_result['status'] == 'authenticated'
        assert 'session_id' in auth_result
        
        # Verificar sessão criada
        status = await api.get_system_status()
        assert status['active_sessions'] == 1
        
        # Autenticação inválida
        with pytest.raises(ValueError, match="Credenciais inválidas"):
            await api.authenticate_user('wrong_key', 'wrong_secret')
    
    @pytest.mark.asyncio
    async def test_system_limits(self, api):
        """Testa limites do sistema"""
        symbol = 'BTCUSDT'
        
        # Criar posições até o limite
        positions = []
        for i in range(api.config['max_positions']):
            position = await api.create_position(symbol, 'buy', 0.1, 'ppp_vishva')
            positions.append(position)
        
        # Tentar criar posição além do limite
        with pytest.raises(ValueError, match="Máximo de posições atingido"):
            await api.create_position(symbol, 'buy', 0.1, 'ppp_vishva')
        
        # Fechar uma posição
        await api.close_position(positions[0]['id'])
        
        # Agora deve conseguir criar nova posição
        new_position = await api.create_position(symbol, 'sell', 0.2, 'ppp_vishva')
        assert new_position['side'] == 'sell'
    
    @pytest.mark.asyncio
    async def test_error_handling_system_not_running(self):
        """Testa tratamento de erros quando sistema não está rodando"""
        api = TradingAPI()
        
        # Tentar operações sem inicializar sistema
        with pytest.raises(RuntimeError, match="Sistema não está rodando"):
            await api.analyze_market('BTCUSDT')
        
        with pytest.raises(RuntimeError, match="Sistema não está rodando"):
            await api.create_position('BTCUSDT', 'buy', 0.1, 'ppp_vishva')
    
    @pytest.mark.asyncio
    async def test_invalid_strategy_handling(self, api):
        """Testa tratamento de estratégia inválida"""
        with pytest.raises(ValueError, match="Estratégia 'invalid_strategy' não encontrada"):
            await api.analyze_market('BTCUSDT', 'invalid_strategy')
    
    @pytest.mark.asyncio
    async def test_invalid_position_handling(self, api):
        """Testa tratamento de posição inválida"""
        with pytest.raises(ValueError, match="Posição 'invalid_id' não encontrada"):
            await api.close_position('invalid_id')
    
    @pytest.mark.asyncio
    async def test_system_status_monitoring(self, api):
        """Testa monitoramento de status do sistema"""
        status = await api.get_system_status()
        
        assert status['is_running'] is True
        assert status['strategies_loaded'] >= 1
        assert status['active_positions'] == 0
        assert isinstance(status['cache_entries'], int)
        assert isinstance(status['active_sessions'], int)
        assert status['uptime'] > 0
        assert 'config' in status


class TestAPIPerformance:
    """Testes de performance da API"""
    
    @pytest.fixture
    async def api(self):
        api = TradingAPI()
        await api.start_system()
        yield api
        await api.stop_system()
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_market_data_performance(self, api):
        """Testa performance da obtenção de dados de mercado"""
        symbol = 'BTCUSDT'
        
        # Testar múltiplas chamadas
        start_time = time.time()
        
        tasks = []
        for _ in range(10):
            task = api.get_market_data(symbol, '1m', 100)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        total_time = time.time() - start_time
        
        # Todas as chamadas devem retornar dados
        assert len(results) == 10
        for result in results:
            assert len(result) == 100
        
        # Deve executar em tempo razoável (benefício do cache)
        assert total_time < 2.0  # Menos de 2 segundos para 10 chamadas
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_concurrent_analysis(self, api):
        """Testa análise concorrente de múltiplos símbolos"""
        symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT']
        
        start_time = time.time()
        
        # Analisar múltiplos símbolos simultaneamente
        tasks = []
        for symbol in symbols:
            task = api.analyze_market(symbol, 'ppp_vishva')
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        total_time = time.time() - start_time
        
        # Verificar resultados
        assert len(results) == len(symbols)
        for i, result in enumerate(results):
            assert result['symbol'] == symbols[i]
            assert result['strategy'] == 'ppp_vishva'
        
        # Deve executar em tempo razoável
        assert total_time < 1.0  # Menos de 1 segundo para 3 análises


class TestAPIResilience:
    """Testes de resiliência da API"""
    
    @pytest.fixture
    async def api(self):
        api = TradingAPI()
        await api.start_system()
        yield api
        await api.stop_system()
    
    @pytest.mark.asyncio
    async def test_graceful_shutdown_with_active_positions(self, api):
        """Testa parada graciosa com posições ativas"""
        # Criar algumas posições
        positions = []
        for i in range(3):
            position = await api.create_position('BTCUSDT', 'buy', 0.1, 'ppp_vishva')
            positions.append(position)
        
        # Verificar posições ativas
        active_positions = await api.get_positions()
        assert len(active_positions) == 3
        
        # Parar sistema (deve fechar todas as posições)
        await api.stop_system()
        
        # Sistema deve estar parado
        assert not api.is_running
        
        # Posições devem ter sido fechadas
        assert len(api.active_positions) == 0
    
    @pytest.mark.asyncio
    async def test_cache_cleanup_behavior(self, api):
        """Testa comportamento de limpeza do cache"""
        # Preencher cache
        symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT']
        for symbol in symbols:
            await api.get_market_data(symbol, '1m', 50)
        
        # Verificar cache populado
        assert len(api.market_data_cache) == len(symbols)
        
        # Simular expiração do cache alterando TTL
        original_ttl = api.config['cache_ttl']
        api.config['cache_ttl'] = 0  # Cache expira imediatamente
        
        # Nova chamada deve ignorar cache expirado
        new_data = await api.get_market_data('BTCUSDT', '1m', 50)
        assert isinstance(new_data, list)
        
        # Restaurar TTL
        api.config['cache_ttl'] = original_ttl
    
    @pytest.mark.asyncio
    async def test_multiple_restart_cycles(self, api):
        """Testa múltiplos ciclos de reinicialização"""
        # Parar sistema atual
        await api.stop_system()
        
        # Testar múltiplos ciclos
        for cycle in range(3):
            # Iniciar
            await api.start_system()
            assert api.is_running
            
            # Criar posição
            position = await api.create_position('BTCUSDT', 'buy', 0.1, 'ppp_vishva')
            assert position['status'] == 'open'
            
            # Parar
            await api.stop_system()
            assert not api.is_running
            assert len(api.active_positions) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])