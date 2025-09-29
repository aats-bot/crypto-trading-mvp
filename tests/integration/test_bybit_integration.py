"""
Testes de integração com a API da Bybit
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


class BybitAPIClient:
    """
    Simulação do cliente da API da Bybit
    Baseado na integração real do sistema
    """
    
    def __init__(self, api_key: str = None, api_secret: str = None, testnet: bool = True):
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        self.base_url = "https://api-testnet.bybit.com" if testnet else "https://api.bybit.com"
        self.is_connected = False
        self.rate_limit_remaining = 100
        self.last_request_time = 0
        
        # Simular dados de mercado em tempo real
        self.market_data_stream = {}
        self.order_book_cache = {}
        
    async def connect(self):
        """Conectar à API da Bybit"""
        if not self.api_key or not self.api_secret:
            raise ValueError("API key e secret são obrigatórios")
        
        # Simular handshake de conexão
        await asyncio.sleep(0.1)
        
        # Simular verificação de credenciais
        if self.api_key == "invalid_key":
            raise ConnectionError("Credenciais inválidas")
        
        self.is_connected = True
        return {"status": "connected", "testnet": self.testnet}
    
    async def disconnect(self):
        """Desconectar da API"""
        self.is_connected = False
        self.market_data_stream.clear()
        self.order_book_cache.clear()
        await asyncio.sleep(0.05)
        return {"status": "disconnected"}
    
    def _check_connection(self):
        """Verificar se está conectado"""
        if not self.is_connected:
            raise ConnectionError("Cliente não está conectado à Bybit")
    
    def _check_rate_limit(self):
        """Verificar rate limit"""
        current_time = time.time()
        if current_time - self.last_request_time < 0.1:  # 10 requests/second max
            if self.rate_limit_remaining <= 0:
                raise Exception("Rate limit excedido")
        else:
            self.rate_limit_remaining = 100  # Reset rate limit
        
        self.rate_limit_remaining -= 1
        self.last_request_time = current_time
    
    async def get_server_time(self):
        """Obter tempo do servidor"""
        self._check_connection()
        self._check_rate_limit()
        
        await asyncio.sleep(0.02)  # Simular latência
        
        return {
            "retCode": 0,
            "retMsg": "OK",
            "result": {
                "timeSecond": str(int(time.time())),
                "timeNano": str(int(time.time() * 1000000000))
            }
        }
    
    async def get_instruments_info(self, category: str = "spot", symbol: str = None):
        """Obter informações dos instrumentos"""
        self._check_connection()
        self._check_rate_limit()
        
        await asyncio.sleep(0.05)
        
        # Simular dados de instrumentos
        instruments = [
            {
                "symbol": "BTCUSDT",
                "contractType": "LinearPerpetual",
                "status": "Trading",
                "baseCoin": "BTC",
                "quoteCoin": "USDT",
                "launchTime": "1585526400000",
                "deliveryTime": "0",
                "deliveryFeeRate": "",
                "priceScale": "2",
                "leverageFilter": {
                    "minLeverage": "1",
                    "maxLeverage": "100.00",
                    "leverageStep": "0.01"
                },
                "priceFilter": {
                    "minPrice": "0.50",
                    "maxPrice": "999999.00",
                    "tickSize": "0.50"
                },
                "lotSizeFilter": {
                    "maxOrderQty": "100.000",
                    "minOrderQty": "0.001",
                    "qtyStep": "0.001",
                    "postOnlyMaxOrderQty": "1000.000"
                }
            },
            {
                "symbol": "ETHUSDT",
                "contractType": "LinearPerpetual",
                "status": "Trading",
                "baseCoin": "ETH",
                "quoteCoin": "USDT",
                "launchTime": "1585526400000",
                "deliveryTime": "0",
                "deliveryFeeRate": "",
                "priceScale": "2",
                "leverageFilter": {
                    "minLeverage": "1",
                    "maxLeverage": "50.00",
                    "leverageStep": "0.01"
                },
                "priceFilter": {
                    "minPrice": "0.05",
                    "maxPrice": "99999.00",
                    "tickSize": "0.05"
                },
                "lotSizeFilter": {
                    "maxOrderQty": "1000.000",
                    "minOrderQty": "0.01",
                    "qtyStep": "0.01",
                    "postOnlyMaxOrderQty": "10000.000"
                }
            }
        ]
        
        if symbol:
            instruments = [inst for inst in instruments if inst["symbol"] == symbol]
        
        return {
            "retCode": 0,
            "retMsg": "OK",
            "result": {
                "category": category,
                "list": instruments
            }
        }
    
    async def get_kline(self, category: str, symbol: str, interval: str, limit: int = 200, start: int = None, end: int = None):
        """Obter dados de kline (candlestick)"""
        self._check_connection()
        self._check_rate_limit()
        
        await asyncio.sleep(0.03)
        
        # Simular dados de kline
        import random
        
        base_price = 50000 if symbol == "BTCUSDT" else 3000
        klines = []
        
        current_time = int(time.time() * 1000)
        interval_ms = self._interval_to_ms(interval)
        
        for i in range(limit):
            timestamp = current_time - (limit - i) * interval_ms
            
            # Simular movimento de preço
            change = random.uniform(-0.02, 0.02)  # ±2%
            base_price *= (1 + change)
            
            volatility = random.uniform(0.001, 0.01)  # 0.1% a 1%
            
            open_price = base_price
            close_price = base_price * (1 + change/2)
            high_price = max(open_price, close_price) * (1 + volatility)
            low_price = min(open_price, close_price) * (1 - volatility)
            volume = random.uniform(100, 10000)
            
            kline = [
                str(timestamp),
                f"{open_price:.2f}",
                f"{high_price:.2f}",
                f"{low_price:.2f}",
                f"{close_price:.2f}",
                f"{volume:.3f}",
                f"{volume * (high_price + low_price) / 2:.2f}"  # turnover
            ]
            klines.append(kline)
        
        return {
            "retCode": 0,
            "retMsg": "OK",
            "result": {
                "symbol": symbol,
                "category": category,
                "list": klines
            }
        }
    
    def _interval_to_ms(self, interval: str) -> int:
        """Converter intervalo para milissegundos"""
        interval_map = {
            "1": 60000,      # 1 minuto
            "3": 180000,     # 3 minutos
            "5": 300000,     # 5 minutos
            "15": 900000,    # 15 minutos
            "30": 1800000,   # 30 minutos
            "60": 3600000,   # 1 hora
            "120": 7200000,  # 2 horas
            "240": 14400000, # 4 horas
            "360": 21600000, # 6 horas
            "720": 43200000, # 12 horas
            "D": 86400000,   # 1 dia
            "W": 604800000,  # 1 semana
            "M": 2592000000  # 1 mês (30 dias)
        }
        return interval_map.get(interval, 60000)
    
    async def get_orderbook(self, category: str, symbol: str, limit: int = 25):
        """Obter order book"""
        self._check_connection()
        self._check_rate_limit()
        
        await asyncio.sleep(0.02)
        
        # Simular order book
        import random
        
        base_price = 50000 if symbol == "BTCUSDT" else 3000
        
        # Gerar bids (ordens de compra)
        bids = []
        for i in range(limit):
            price = base_price * (1 - (i + 1) * 0.0001)  # Preços decrescentes
            size = random.uniform(0.1, 10.0)
            bids.append([f"{price:.2f}", f"{size:.3f}"])
        
        # Gerar asks (ordens de venda)
        asks = []
        for i in range(limit):
            price = base_price * (1 + (i + 1) * 0.0001)  # Preços crescentes
            size = random.uniform(0.1, 10.0)
            asks.append([f"{price:.2f}", f"{size:.3f}"])
        
        return {
            "retCode": 0,
            "retMsg": "OK",
            "result": {
                "s": symbol,
                "b": bids,
                "a": asks,
                "ts": int(time.time() * 1000),
                "u": random.randint(1000000, 9999999)  # Update ID
            }
        }
    
    async def get_tickers(self, category: str, symbol: str = None):
        """Obter tickers de preço"""
        self._check_connection()
        self._check_rate_limit()
        
        await asyncio.sleep(0.03)
        
        # Simular dados de ticker
        import random
        
        symbols = ["BTCUSDT", "ETHUSDT"] if not symbol else [symbol]
        tickers = []
        
        for sym in symbols:
            base_price = 50000 if sym == "BTCUSDT" else 3000
            change_24h = random.uniform(-0.05, 0.05)  # ±5%
            
            ticker = {
                "symbol": sym,
                "lastPrice": f"{base_price:.2f}",
                "indexPrice": f"{base_price * 0.999:.2f}",
                "markPrice": f"{base_price * 1.001:.2f}",
                "prevPrice24h": f"{base_price * (1 - change_24h):.2f}",
                "price24hPcnt": f"{change_24h:.4f}",
                "highPrice24h": f"{base_price * (1 + abs(change_24h)):.2f}",
                "lowPrice24h": f"{base_price * (1 - abs(change_24h)):.2f}",
                "prevPrice1h": f"{base_price * (1 - change_24h/24):.2f}",
                "openInterest": f"{random.uniform(10000, 100000):.3f}",
                "openInterestValue": f"{random.uniform(500000000, 5000000000):.2f}",
                "turnover24h": f"{random.uniform(1000000000, 10000000000):.2f}",
                "volume24h": f"{random.uniform(10000, 100000):.3f}",
                "fundingRate": f"{random.uniform(-0.001, 0.001):.6f}",
                "nextFundingTime": str(int(time.time() + 28800) * 1000),  # +8 horas
                "predictedDeliveryPrice": "",
                "basisRate": "",
                "deliveryFeeRate": "",
                "deliveryTime": "0",
                "ask1Size": f"{random.uniform(1, 100):.3f}",
                "bid1Price": f"{base_price * 0.9999:.2f}",
                "ask1Price": f"{base_price * 1.0001:.2f}",
                "bid1Size": f"{random.uniform(1, 100):.3f}"
            }
            tickers.append(ticker)
        
        return {
            "retCode": 0,
            "retMsg": "OK",
            "result": {
                "category": category,
                "list": tickers
            }
        }
    
    async def place_order(self, category: str, symbol: str, side: str, orderType: str, qty: str, price: str = None, **kwargs):
        """Colocar ordem"""
        self._check_connection()
        self._check_rate_limit()
        
        await asyncio.sleep(0.1)  # Simular latência de ordem
        
        # Simular validações
        if float(qty) <= 0:
            raise ValueError("Quantidade deve ser positiva")
        
        if orderType == "Limit" and not price:
            raise ValueError("Preço é obrigatório para ordens limit")
        
        # Simular criação de ordem
        order_id = f"order_{int(time.time() * 1000)}_{symbol}_{side}"
        
        return {
            "retCode": 0,
            "retMsg": "OK",
            "result": {
                "orderId": order_id,
                "orderLinkId": kwargs.get("orderLinkId", ""),
                "symbol": symbol,
                "side": side,
                "orderType": orderType,
                "qty": qty,
                "price": price or "0",
                "timeInForce": kwargs.get("timeInForce", "GTC"),
                "orderStatus": "New",
                "createdTime": str(int(time.time() * 1000))
            }
        }
    
    async def cancel_order(self, category: str, symbol: str, orderId: str = None, orderLinkId: str = None):
        """Cancelar ordem"""
        self._check_connection()
        self._check_rate_limit()
        
        await asyncio.sleep(0.05)
        
        if not orderId and not orderLinkId:
            raise ValueError("orderId ou orderLinkId é obrigatório")
        
        return {
            "retCode": 0,
            "retMsg": "OK",
            "result": {
                "orderId": orderId or f"order_{int(time.time())}",
                "orderLinkId": orderLinkId or "",
                "symbol": symbol,
                "orderStatus": "Cancelled",
                "cancelledTime": str(int(time.time() * 1000))
            }
        }
    
    async def get_open_orders(self, category: str, symbol: str = None, limit: int = 20):
        """Obter ordens abertas"""
        self._check_connection()
        self._check_rate_limit()
        
        await asyncio.sleep(0.03)
        
        # Simular ordens abertas
        orders = []
        if symbol:
            symbols = [symbol]
        else:
            symbols = ["BTCUSDT", "ETHUSDT"]
        
        import random
        for sym in symbols[:2]:  # Limitar para não sobrecarregar
            for i in range(random.randint(0, 3)):  # 0-3 ordens por símbolo
                order = {
                    "orderId": f"order_{int(time.time())}_{i}_{sym}",
                    "orderLinkId": f"link_{i}",
                    "symbol": sym,
                    "side": random.choice(["Buy", "Sell"]),
                    "orderType": "Limit",
                    "qty": f"{random.uniform(0.1, 10):.3f}",
                    "price": f"{random.uniform(45000, 55000):.2f}",
                    "timeInForce": "GTC",
                    "orderStatus": "New",
                    "createdTime": str(int(time.time() * 1000) - random.randint(0, 3600000)),
                    "updatedTime": str(int(time.time() * 1000))
                }
                orders.append(order)
        
        return {
            "retCode": 0,
            "retMsg": "OK",
            "result": {
                "category": category,
                "list": orders[:limit]
            }
        }
    
    async def get_positions(self, category: str, symbol: str = None):
        """Obter posições"""
        self._check_connection()
        self._check_rate_limit()
        
        await asyncio.sleep(0.03)
        
        # Simular posições
        positions = []
        symbols = [symbol] if symbol else ["BTCUSDT", "ETHUSDT"]
        
        import random
        for sym in symbols:
            if random.choice([True, False]):  # 50% chance de ter posição
                position = {
                    "symbol": sym,
                    "side": random.choice(["Buy", "Sell"]),
                    "size": f"{random.uniform(0.1, 5):.3f}",
                    "avgPrice": f"{random.uniform(45000, 55000):.2f}",
                    "positionValue": f"{random.uniform(1000, 50000):.2f}",
                    "unrealisedPnl": f"{random.uniform(-1000, 1000):.2f}",
                    "cumRealisedPnl": f"{random.uniform(-500, 500):.2f}",
                    "positionMM": f"{random.uniform(100, 1000):.2f}",
                    "positionIM": f"{random.uniform(500, 5000):.2f}",
                    "liqPrice": f"{random.uniform(40000, 60000):.2f}",
                    "bustPrice": f"{random.uniform(35000, 65000):.2f}",
                    "positionStatus": "Normal",
                    "leverage": f"{random.randint(1, 10)}",
                    "markPrice": f"{random.uniform(49000, 51000):.2f}",
                    "createdTime": str(int(time.time() * 1000) - random.randint(0, 86400000)),
                    "updatedTime": str(int(time.time() * 1000))
                }
                positions.append(position)
        
        return {
            "retCode": 0,
            "retMsg": "OK",
            "result": {
                "category": category,
                "list": positions
            }
        }


class TestBybitIntegration:
    """Testes de integração com a API da Bybit"""
    
    @pytest.fixture
    async def bybit_client(self):
        """Fixture do cliente Bybit para testes"""
        client = BybitAPIClient("test_api_key", "test_api_secret", testnet=True)
        await client.connect()
        yield client
        await client.disconnect()
    
    @pytest.mark.asyncio
    async def test_connection_flow(self):
        """Testa fluxo de conexão e desconexão"""
        client = BybitAPIClient("test_api_key", "test_api_secret")
        
        # Cliente deve começar desconectado
        assert not client.is_connected
        
        # Conectar
        result = await client.connect()
        assert result["status"] == "connected"
        assert client.is_connected
        
        # Desconectar
        result = await client.disconnect()
        assert result["status"] == "disconnected"
        assert not client.is_connected
    
    @pytest.mark.asyncio
    async def test_invalid_credentials(self):
        """Testa tratamento de credenciais inválidas"""
        client = BybitAPIClient("invalid_key", "invalid_secret")
        
        with pytest.raises(ConnectionError, match="Credenciais inválidas"):
            await client.connect()
    
    @pytest.mark.asyncio
    async def test_server_time(self, bybit_client):
        """Testa obtenção do tempo do servidor"""
        result = await bybit_client.get_server_time()
        
        assert result["retCode"] == 0
        assert result["retMsg"] == "OK"
        assert "timeSecond" in result["result"]
        assert "timeNano" in result["result"]
        
        # Verificar se o tempo está próximo do atual
        server_time = int(result["result"]["timeSecond"])
        current_time = int(time.time())
        assert abs(server_time - current_time) < 5  # Diferença menor que 5 segundos
    
    @pytest.mark.asyncio
    async def test_instruments_info(self, bybit_client):
        """Testa obtenção de informações dos instrumentos"""
        # Obter todos os instrumentos
        result = await bybit_client.get_instruments_info("linear")
        
        assert result["retCode"] == 0
        assert result["retMsg"] == "OK"
        assert "list" in result["result"]
        assert len(result["result"]["list"]) > 0
        
        # Verificar estrutura do instrumento
        instrument = result["result"]["list"][0]
        required_fields = ["symbol", "status", "baseCoin", "quoteCoin", "leverageFilter", "priceFilter", "lotSizeFilter"]
        for field in required_fields:
            assert field in instrument
        
        # Obter instrumento específico
        result = await bybit_client.get_instruments_info("linear", "BTCUSDT")
        assert len(result["result"]["list"]) == 1
        assert result["result"]["list"][0]["symbol"] == "BTCUSDT"
    
    @pytest.mark.asyncio
    async def test_kline_data(self, bybit_client):
        """Testa obtenção de dados de kline"""
        result = await bybit_client.get_kline("linear", "BTCUSDT", "1", 100)
        
        assert result["retCode"] == 0
        assert result["retMsg"] == "OK"
        assert result["result"]["symbol"] == "BTCUSDT"
        assert len(result["result"]["list"]) == 100
        
        # Verificar estrutura do kline
        kline = result["result"]["list"][0]
        assert len(kline) == 7  # timestamp, open, high, low, close, volume, turnover
        
        # Verificar que os dados são válidos
        timestamp, open_price, high, low, close, volume, turnover = kline
        assert int(timestamp) > 0
        assert float(open_price) > 0
        assert float(high) >= float(open_price)
        assert float(low) <= float(open_price)
        assert float(close) > 0
        assert float(volume) >= 0
    
    @pytest.mark.asyncio
    async def test_orderbook_data(self, bybit_client):
        """Testa obtenção do order book"""
        result = await bybit_client.get_orderbook("linear", "BTCUSDT", 25)
        
        assert result["retCode"] == 0
        assert result["retMsg"] == "OK"
        assert result["result"]["s"] == "BTCUSDT"
        assert "b" in result["result"]  # bids
        assert "a" in result["result"]  # asks
        assert "ts" in result["result"]  # timestamp
        assert "u" in result["result"]   # update id
        
        # Verificar bids e asks
        bids = result["result"]["b"]
        asks = result["result"]["a"]
        
        assert len(bids) == 25
        assert len(asks) == 25
        
        # Verificar estrutura de bid/ask
        bid = bids[0]
        ask = asks[0]
        
        assert len(bid) == 2  # [price, size]
        assert len(ask) == 2  # [price, size]
        assert float(bid[0]) > 0  # price
        assert float(bid[1]) > 0  # size
        assert float(ask[0]) > 0  # price
        assert float(ask[1]) > 0  # size
        
        # Verificar que ask price > bid price
        assert float(ask[0]) > float(bid[0])
    
    @pytest.mark.asyncio
    async def test_ticker_data(self, bybit_client):
        """Testa obtenção de dados de ticker"""
        # Ticker específico
        result = await bybit_client.get_tickers("linear", "BTCUSDT")
        
        assert result["retCode"] == 0
        assert result["retMsg"] == "OK"
        assert len(result["result"]["list"]) == 1
        
        ticker = result["result"]["list"][0]
        assert ticker["symbol"] == "BTCUSDT"
        
        # Verificar campos obrigatórios
        required_fields = ["lastPrice", "prevPrice24h", "price24hPcnt", "highPrice24h", "lowPrice24h", "volume24h"]
        for field in required_fields:
            assert field in ticker
            assert ticker[field] != ""
        
        # Verificar que os preços são válidos
        assert float(ticker["lastPrice"]) > 0
        assert float(ticker["highPrice24h"]) >= float(ticker["lowPrice24h"])
    
    @pytest.mark.asyncio
    async def test_order_management_flow(self, bybit_client):
        """Testa fluxo completo de gestão de ordens"""
        symbol = "BTCUSDT"
        
        # Colocar ordem limit
        order_result = await bybit_client.place_order(
            category="linear",
            symbol=symbol,
            side="Buy",
            orderType="Limit",
            qty="0.001",
            price="45000.00",
            timeInForce="GTC"
        )
        
        assert order_result["retCode"] == 0
        assert order_result["result"]["symbol"] == symbol
        assert order_result["result"]["side"] == "Buy"
        assert order_result["result"]["orderStatus"] == "New"
        
        order_id = order_result["result"]["orderId"]
        
        # Verificar ordem nas ordens abertas
        open_orders = await bybit_client.get_open_orders("linear", symbol)
        assert open_orders["retCode"] == 0
        
        # Cancelar ordem
        cancel_result = await bybit_client.cancel_order("linear", symbol, orderId=order_id)
        
        assert cancel_result["retCode"] == 0
        assert cancel_result["result"]["orderId"] == order_id
        assert cancel_result["result"]["orderStatus"] == "Cancelled"
    
    @pytest.mark.asyncio
    async def test_position_monitoring(self, bybit_client):
        """Testa monitoramento de posições"""
        result = await bybit_client.get_positions("linear")
        
        assert result["retCode"] == 0
        assert result["retMsg"] == "OK"
        assert "list" in result["result"]
        
        # Se houver posições, verificar estrutura
        if result["result"]["list"]:
            position = result["result"]["list"][0]
            required_fields = ["symbol", "side", "size", "avgPrice", "unrealisedPnl", "leverage"]
            for field in required_fields:
                assert field in position
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self, bybit_client):
        """Testa comportamento do rate limiting"""
        # Fazer muitas requisições rapidamente
        tasks = []
        for _ in range(50):  # Tentar 50 requisições
            task = bybit_client.get_server_time()
            tasks.append(task)
        
        # Algumas podem falhar por rate limit
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        successful_requests = [r for r in results if not isinstance(r, Exception)]
        failed_requests = [r for r in results if isinstance(r, Exception)]
        
        # Deve ter pelo menos algumas requisições bem-sucedidas
        assert len(successful_requests) > 0
        
        # Se houver falhas, devem ser por rate limit
        for failure in failed_requests:
            assert "Rate limit" in str(failure)
    
    @pytest.mark.asyncio
    async def test_connection_required_operations(self):
        """Testa operações que requerem conexão"""
        client = BybitAPIClient("test_key", "test_secret")
        
        # Tentar operações sem conectar
        with pytest.raises(ConnectionError, match="Cliente não está conectado"):
            await client.get_server_time()
        
        with pytest.raises(ConnectionError, match="Cliente não está conectado"):
            await client.get_kline("linear", "BTCUSDT", "1")
        
        with pytest.raises(ConnectionError, match="Cliente não está conectado"):
            await client.place_order("linear", "BTCUSDT", "Buy", "Market", "0.001")


class TestBybitPerformance:
    """Testes de performance da integração com Bybit"""
    
    @pytest.fixture
    async def bybit_client(self):
        client = BybitAPIClient("test_key", "test_secret")
        await client.connect()
        yield client
        await client.disconnect()
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_concurrent_market_data_requests(self, bybit_client):
        """Testa requisições concorrentes de dados de mercado"""
        symbols = ["BTCUSDT", "ETHUSDT"]
        
        start_time = time.time()
        
        # Fazer requisições concorrentes
        tasks = []
        for symbol in symbols:
            tasks.append(bybit_client.get_kline("linear", symbol, "1", 100))
            tasks.append(bybit_client.get_orderbook("linear", symbol, 25))
            tasks.append(bybit_client.get_tickers("linear", symbol))
        
        results = await asyncio.gather(*tasks)
        
        total_time = time.time() - start_time
        
        # Verificar que todas as requisições foram bem-sucedidas
        assert len(results) == 6  # 3 tipos × 2 símbolos
        for result in results:
            assert result["retCode"] == 0
        
        # Deve executar em tempo razoável
        assert total_time < 2.0  # Menos de 2 segundos
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_kline_data_retrieval_performance(self, bybit_client):
        """Testa performance da obtenção de dados de kline"""
        start_time = time.time()
        
        # Obter dados históricos grandes
        result = await bybit_client.get_kline("linear", "BTCUSDT", "1", 1000)
        
        total_time = time.time() - start_time
        
        assert result["retCode"] == 0
        assert len(result["result"]["list"]) == 1000
        
        # Deve executar em tempo razoável
        assert total_time < 1.0  # Menos de 1 segundo


class TestBybitErrorHandling:
    """Testes de tratamento de erros da integração com Bybit"""
    
    @pytest.fixture
    async def bybit_client(self):
        client = BybitAPIClient("test_key", "test_secret")
        await client.connect()
        yield client
        await client.disconnect()
    
    @pytest.mark.asyncio
    async def test_invalid_order_parameters(self, bybit_client):
        """Testa tratamento de parâmetros inválidos em ordens"""
        # Quantidade inválida
        with pytest.raises(ValueError, match="Quantidade deve ser positiva"):
            await bybit_client.place_order("linear", "BTCUSDT", "Buy", "Market", "0")
        
        with pytest.raises(ValueError, match="Quantidade deve ser positiva"):
            await bybit_client.place_order("linear", "BTCUSDT", "Buy", "Market", "-0.1")
        
        # Ordem limit sem preço
        with pytest.raises(ValueError, match="Preço é obrigatório para ordens limit"):
            await bybit_client.place_order("linear", "BTCUSDT", "Buy", "Limit", "0.1")
    
    @pytest.mark.asyncio
    async def test_cancel_nonexistent_order(self, bybit_client):
        """Testa cancelamento de ordem inexistente"""
        # Tentar cancelar ordem que não existe
        with pytest.raises(ValueError, match="orderId ou orderLinkId é obrigatório"):
            await bybit_client.cancel_order("linear", "BTCUSDT")
    
    @pytest.mark.asyncio
    async def test_network_resilience(self, bybit_client):
        """Testa resiliência a problemas de rede simulados"""
        # Simular desconexão temporária
        original_connected = bybit_client.is_connected
        bybit_client.is_connected = False
        
        # Operações devem falhar graciosamente
        with pytest.raises(ConnectionError):
            await bybit_client.get_server_time()
        
        # Restaurar conexão
        bybit_client.is_connected = original_connected
        
        # Operações devem voltar a funcionar
        result = await bybit_client.get_server_time()
        assert result["retCode"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

