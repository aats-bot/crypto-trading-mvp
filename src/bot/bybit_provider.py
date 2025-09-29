"""
Bybit implementation of trading interfaces
"""
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from pybit.unified_trading import HTTP, WebSocket

from .interfaces import (
    MarketDataProvider, OrderExecutor, AccountManager,
    MarketData, OrderRequest, Order, Position, Balance,
    OrderSide, OrderType, PositionSide
)

logger = logging.getLogger(__name__)


class BybitMarketDataProvider(MarketDataProvider):
    """Bybit market data provider implementation"""
    
    def __init__(self, api_key: str = None, api_secret: str = None, testnet: bool = True):
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        self.session = HTTP(
            testnet=testnet,
            api_key=api_key,
            api_secret=api_secret
        )
        self.ws = None
        self._subscriptions = {}
    
    async def get_ticker(self, symbol: str) -> MarketData:
        """Get current ticker data for a symbol"""
        try:
            response = self.session.get_tickers(category="linear", symbol=symbol)
            
            if response['retCode'] != 0:
                raise Exception(f"Bybit API error: {response['retMsg']}")
            
            ticker_data = response['result']['list'][0]
            
            return MarketData(
                symbol=symbol,
                timestamp=datetime.now(),
                price=float(ticker_data['lastPrice']),
                volume=float(ticker_data['volume24h']),
                bid=float(ticker_data.get('bid1Price', 0)) or None,
                ask=float(ticker_data.get('ask1Price', 0)) or None,
                high_24h=float(ticker_data['highPrice24h']),
                low_24h=float(ticker_data['lowPrice24h']),
                change_24h=float(ticker_data['price24hPcnt']) * 100
            )
        except Exception as e:
            logger.error(f"Error getting ticker for {symbol}: {e}")
            raise
    
    async def get_orderbook(self, symbol: str, limit: int = 20) -> Dict[str, Any]:
        """Get orderbook data for a symbol"""
        try:
            response = self.session.get_orderbook(category="linear", symbol=symbol, limit=limit)
            
            if response['retCode'] != 0:
                raise Exception(f"Bybit API error: {response['retMsg']}")
            
            return response['result']
        except Exception as e:
            logger.error(f"Error getting orderbook for {symbol}: {e}")
            raise
    
    async def get_klines(self, symbol: str, interval: str, limit: int = 100) -> List[Dict]:
        """Get kline/candlestick data"""
        try:
            response = self.session.get_kline(
                category="linear",
                symbol=symbol,
                interval=interval,
                limit=limit
            )
            
            if response['retCode'] != 0:
                raise Exception(f"Bybit API error: {response['retMsg']}")
            
            return response['result']['list']
        except Exception as e:
            logger.error(f"Error getting klines for {symbol}: {e}")
            raise
    
    async def subscribe_ticker(self, symbol: str, callback: Callable) -> None:
        """Subscribe to real-time ticker updates"""
        if not self.ws:
            self._init_websocket()
        
        topic = f"tickers.{symbol}"
        self._subscriptions[topic] = callback
        
        # Subscribe to the topic
        self.ws.ticker_stream(symbol=symbol, callback=self._handle_ticker_message)
    
    async def subscribe_orderbook(self, symbol: str, callback: Callable) -> None:
        """Subscribe to real-time orderbook updates"""
        if not self.ws:
            self._init_websocket()
        
        topic = f"orderbook.1.{symbol}"
        self._subscriptions[topic] = callback
        
        # Subscribe to orderbook
        self.ws.orderbook_stream(depth=1, symbol=symbol, callback=self._handle_orderbook_message)
    
    def _init_websocket(self):
        """Initialize WebSocket connection"""
        self.ws = WebSocket(
            testnet=self.testnet,
            channel_type="linear"
        )
    
    def _handle_ticker_message(self, message):
        """Handle ticker WebSocket messages"""
        try:
            if 'topic' in message and 'data' in message:
                topic = message['topic']
                if topic in self._subscriptions:
                    callback = self._subscriptions[topic]
                    # Convert to MarketData format
                    data = message['data']
                    market_data = MarketData(
                        symbol=data['symbol'],
                        timestamp=datetime.now(),
                        price=float(data['lastPrice']),
                        volume=float(data['volume24h']),
                        high_24h=float(data['highPrice24h']),
                        low_24h=float(data['lowPrice24h']),
                        change_24h=float(data['price24hPcnt']) * 100
                    )
                    callback(market_data)
        except Exception as e:
            logger.error(f"Error handling ticker message: {e}")
    
    def _handle_orderbook_message(self, message):
        """Handle orderbook WebSocket messages"""
        try:
            if 'topic' in message and 'data' in message:
                topic = message['topic']
                if topic in self._subscriptions:
                    callback = self._subscriptions[topic]
                    callback(message['data'])
        except Exception as e:
            logger.error(f"Error handling orderbook message: {e}")


class BybitOrderExecutor(OrderExecutor):
    """Bybit order executor implementation"""
    
    def __init__(self, api_key: str, api_secret: str, testnet: bool = True):
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        self.session = HTTP(
            testnet=testnet,
            api_key=api_key,
            api_secret=api_secret
        )
    
    async def place_order(self, order_request: OrderRequest) -> Order:
        """Place a new order"""
        try:
            # Convert order request to Bybit format
            bybit_order = {
                "category": "linear",
                "symbol": order_request.symbol,
                "side": order_request.side.value,
                "orderType": order_request.order_type.value,
                "qty": str(order_request.quantity),
                "timeInForce": order_request.time_in_force
            }
            
            if order_request.price:
                bybit_order["price"] = str(order_request.price)
            
            if order_request.stop_price:
                bybit_order["stopPrice"] = str(order_request.stop_price)
            
            if order_request.reduce_only:
                bybit_order["reduceOnly"] = True
            
            response = self.session.place_order(**bybit_order)
            
            if response['retCode'] != 0:
                raise Exception(f"Bybit API error: {response['retMsg']}")
            
            result = response['result']
            
            return Order(
                order_id=result['orderId'],
                symbol=order_request.symbol,
                side=order_request.side,
                order_type=order_request.order_type,
                quantity=order_request.quantity,
                price=order_request.price,
                filled_quantity=0.0,
                status="New",
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            raise
    
    async def cancel_order(self, symbol: str, order_id: str) -> bool:
        """Cancel an existing order"""
        try:
            response = self.session.cancel_order(
                category="linear",
                symbol=symbol,
                orderId=order_id
            )
            
            return response['retCode'] == 0
        except Exception as e:
            logger.error(f"Error canceling order {order_id}: {e}")
            return False
    
    async def get_order(self, symbol: str, order_id: str) -> Optional[Order]:
        """Get order details"""
        try:
            response = self.session.get_open_orders(
                category="linear",
                symbol=symbol,
                orderId=order_id
            )
            
            if response['retCode'] != 0 or not response['result']['list']:
                return None
            
            order_data = response['result']['list'][0]
            return self._convert_order(order_data)
        except Exception as e:
            logger.error(f"Error getting order {order_id}: {e}")
            return None
    
    async def get_open_orders(self, symbol: Optional[str] = None) -> List[Order]:
        """Get all open orders"""
        try:
            params = {"category": "linear"}
            if symbol:
                params["symbol"] = symbol
            
            response = self.session.get_open_orders(**params)
            
            if response['retCode'] != 0:
                return []
            
            orders = []
            for order_data in response['result']['list']:
                orders.append(self._convert_order(order_data))
            
            return orders
        except Exception as e:
            logger.error(f"Error getting open orders: {e}")
            return []
    
    async def get_order_history(self, symbol: Optional[str] = None, limit: int = 100) -> List[Order]:
        """Get order history"""
        try:
            params = {"category": "linear", "limit": limit}
            if symbol:
                params["symbol"] = symbol
            
            response = self.session.get_order_history(**params)
            
            if response['retCode'] != 0:
                return []
            
            orders = []
            for order_data in response['result']['list']:
                orders.append(self._convert_order(order_data))
            
            return orders
        except Exception as e:
            logger.error(f"Error getting order history: {e}")
            return []
    
    def _convert_order(self, order_data: Dict) -> Order:
        """Convert Bybit order data to Order object"""
        return Order(
            order_id=order_data['orderId'],
            symbol=order_data['symbol'],
            side=OrderSide(order_data['side']),
            order_type=OrderType(order_data['orderType']),
            quantity=float(order_data['qty']),
            price=float(order_data['price']) if order_data['price'] else None,
            filled_quantity=float(order_data['cumExecQty']),
            status=order_data['orderStatus'],
            timestamp=datetime.fromtimestamp(int(order_data['createdTime']) / 1000),
            avg_price=float(order_data['avgPrice']) if order_data['avgPrice'] else None
        )


class BybitAccountManager(AccountManager):
    """Bybit account manager implementation"""
    
    def __init__(self, api_key: str, api_secret: str, testnet: bool = True):
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        self.session = HTTP(
            testnet=testnet,
            api_key=api_key,
            api_secret=api_secret
        )
    
    async def get_balance(self) -> List[Balance]:
        """Get account balance"""
        try:
            response = self.session.get_wallet_balance(accountType="UNIFIED")
            
            if response['retCode'] != 0:
                raise Exception(f"Bybit API error: {response['retMsg']}")
            
            balances = []
            for account in response['result']['list']:
                for coin_data in account['coin']:
                    balance = Balance(
                        asset=coin_data['coin'],
                        free=float(coin_data['availableBalance']),
                        locked=float(coin_data['orderBalance']),
                        total=float(coin_data['walletBalance'])
                    )
                    balances.append(balance)
            
            return balances
        except Exception as e:
            logger.error(f"Error getting balance: {e}")
            raise
    
    async def get_positions(self, symbol: Optional[str] = None) -> List[Position]:
        """Get current positions"""
        try:
            params = {"category": "linear", "settleCoin": "USDT"}
            if symbol:
                params["symbol"] = symbol
            
            response = self.session.get_positions(**params)
            
            if response['retCode'] != 0:
                raise Exception(f"Bybit API error: {response['retMsg']}")
            
            positions = []
            for pos_data in response['result']['list']:
                if float(pos_data['size']) > 0:  # Only include non-zero positions
                    position = Position(
                        symbol=pos_data['symbol'],
                        side=PositionSide(pos_data['side']),
                        size=float(pos_data['size']),
                        entry_price=float(pos_data['avgPrice']),
                        mark_price=float(pos_data['markPrice']),
                        unrealized_pnl=float(pos_data['unrealisedPnl']),
                        realized_pnl=float(pos_data['cumRealisedPnl']),
                        timestamp=datetime.now()
                    )
                    positions.append(position)
            
            return positions
        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            return []
    
    async def get_position(self, symbol: str) -> Optional[Position]:
        """Get position for specific symbol"""
        positions = await self.get_positions(symbol=symbol)
        return positions[0] if positions else None
    
    async def close_position(self, symbol: str, quantity: Optional[float] = None) -> Order:
        """Close position (market order)"""
        try:
            # Get current position to determine side and quantity
            position = await self.get_position(symbol)
            if not position:
                raise Exception(f"No position found for {symbol}")
            
            # Determine opposite side for closing
            close_side = OrderSide.SELL if position.side == PositionSide.LONG else OrderSide.BUY
            close_quantity = quantity or position.size
            
            # Create close order request
            order_request = OrderRequest(
                symbol=symbol,
                side=close_side,
                order_type=OrderType.MARKET,
                quantity=close_quantity,
                reduce_only=True
            )
            
            # Use order executor to place the order
            executor = BybitOrderExecutor(self.api_key, self.api_secret, self.testnet)
            return await executor.place_order(order_request)
            
        except Exception as e:
            logger.error(f"Error closing position for {symbol}: {e}")
            raise

