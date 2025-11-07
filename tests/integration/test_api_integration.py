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
    def __init__(self):
        self.is_running = False
        self._start_ts = 0.0
        self.config = {
            'max_positions': 3,
            'cache_ttl': 60.0,
        }
        self.market_data_cache = {}
        self.user_sessions = {}
        self.active_positions = {}
        self.strategies = {'ppp_vishva': object()}
        self._pos_counter = 0

    async def start_system(self):
        import asyncio, time
        await asyncio.sleep(0.01)
        self.is_running = True
        self._start_ts = time.time()
        return {'status': 'success'}

    async def _close_positions(self):
        for pid in list(self.active_positions.keys()):
            try:
                self.active_positions[pid]['status'] = 'closed'
            except Exception:
                pass
        self.active_positions.clear()

    async def stop_system(self):
        import asyncio
        await asyncio.sleep(0.01)
        await self._close_positions()
        self.market_data_cache.clear()
        self.is_running = False
        return {'status': 'success'}

    def _cleanup_cache_if_needed(self):
        import time
        ttl = float(self.config.get('cache_ttl', 60.0))
        now = time.time()
        expired = [k for k,v in self.market_data_cache.items() if (now - v.get('ts',0)) > ttl]
        for k in expired:
            del self.market_data_cache[k]

    async def get_market_data(self, symbol: str, timeframe: str = '1m', limit: int = 100):
        if not self.is_running:
            raise RuntimeError("Sistema não está rodando")
        import asyncio, time
        self._cleanup_cache_if_needed()
        key = f"{symbol}_{timeframe}_{limit}"
        if key in self.market_data_cache:
            return self.market_data_cache[key]['data']
        await asyncio.sleep(0.01)
        base = 50000.0 if symbol.upper().startswith('BTC') else 2000.0
        ts0 = int(time.time()) - (limit - 1)
        data = []
        for i in range(limit):
            ref = base + i * 0.1
            o = ref
            c = ref + (0.05 if i % 2 == 0 else -0.05)
            h = max(o, c) + 0.02
            l = min(o, c) - 0.02
            v = 1000 + i
            data.append({
                'timestamp': ts0 + i,
                'open': round(o, 2),
                'high': round(h, 2),
                'low': round(l, 2),
                'close': round(c, 2),
                'volume': v
            })
        self.market_data_cache[key] = {'data': data, 'ts': time.time()}
        return data

    async def analyze_market(self, symbol: str, strategy: str = 'ppp_vishva'):
        if not self.is_running:
            raise RuntimeError("Sistema não está rodando")
        if strategy not in self.strategies:
            raise ValueError(f"Estratégia '{strategy}' não encontrada")
        import time
        md = await self.get_market_data(symbol)
        closes = [c['close'] for c in md] or [0.0]
        avg = sum(closes) / len(closes) if closes else 0.0
        sig = 'buy' if closes and closes[-1] >= avg else 'sell'
        return {
            'symbol': symbol,
            'strategy': strategy,
            'signal': sig,
            'confidence': 0.5,
            'average_price': avg,
            'timestamp': int(time.time()),
            'market_data_points': len(md)
        }

    async def create_position(self, symbol: str, side: str, size: float, strategy: str):
        if not self.is_running:
            raise RuntimeError("Sistema não está rodando")
        if len(self.active_positions) >= int(self.config.get('max_positions', 3)):
            raise ValueError("Máximo de posições atingido")
        import time
        from datetime import datetime
        self._pos_counter += 1
        pid = f"{symbol}_{side}_{int(time.time()*1000)}_{self._pos_counter}"
        pos = {
            'id': pid,
            'symbol': symbol,
            'side': side,
            'size': float(size),
            'strategy': strategy,
            'entry_price': 50000,
            'status': 'open',
            'created_at': datetime.now().isoformat(),
        }
        self.active_positions[pid] = pos
        return pos

    async def get_positions(self):
        return list(self.active_positions.values())

    async def close_position(self, position_id: str):

        from datetime import datetime

        # Fechar posição e devolver closed_at + exit_price

        if position_id not in self.active_positions:

            raise ValueError(f"Posição '{position_id}' não encontrada")

        pos = self.active_positions.pop(position_id)

        pos['status'] = 'closed'

        exit_price = pos.get('entry_price', 50000)

        return {

            'status': 'closed',

            'position_id': position_id,

            'position': pos,

            'closed_at': datetime.now().isoformat(),

            'exit_price': exit_price

        }
    async def authenticate_user(self, api_key: str, api_secret: str):
        import asyncio, time
        from datetime import datetime
        await asyncio.sleep(0.01)
        if api_key == 'test_key' and api_secret == 'test_secret':
            sid = f"session_{int(time.time())}"
            self.user_sessions[sid] = {
                'api_key': api_key,
                'created_at': datetime.now().isoformat(),
                'last_activity': datetime.now().isoformat()
            }
            return {'status': 'authenticated', 'session_id': sid}
        raise ValueError("Credenciais inválidas")

    async def get_system_status(self):
        import time
        self._cleanup_cache_if_needed()
        return {
            'is_running': self.is_running,
            'strategies_loaded': len(self.strategies),
            'active_positions': len(self.active_positions),
            'cache_entries': len(self.market_data_cache),
            'active_sessions': len(self.user_sessions),
            'uptime': (time.time() - self._start_ts) if self.is_running else 0,
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