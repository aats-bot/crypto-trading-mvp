"""
Test script to verify Bybit API connectivity
"""
import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from pybit.unified_trading import HTTP
from config.settings import settings


async def test_bybit_connection():
    """Test basic connection to Bybit API"""
    print("🔄 Testing Bybit API connection...")
    
    try:
        # Initialize Bybit client for testnet
        session = HTTP(
            testnet=True,
            api_key=settings.bybit_api_key,
            api_secret=settings.bybit_api_secret,
        )
        
        # Test public endpoint (no authentication required)
        print("📡 Testing public endpoint...")
        server_time = session.get_server_time()
        print(f"✅ Server time: {server_time}")
        
        # Test market data
        print("📊 Testing market data...")
        tickers = session.get_tickers(category="linear", symbol="BTCUSDT")
        if tickers and tickers.get('result'):
            btc_price = tickers['result']['list'][0]['lastPrice']
            print(f"✅ BTC/USDT price: ${btc_price}")
        
        # Test authenticated endpoints if API keys are provided
        if settings.bybit_api_key and settings.bybit_api_secret:
            print("🔐 Testing authenticated endpoints...")
            
            # Get account info
            account_info = session.get_wallet_balance(accountType="UNIFIED")
            print(f"✅ Account info retrieved: {account_info.get('retMsg', 'Success')}")
            
            # Get positions
            positions = session.get_positions(category="linear", settleCoin="USDT")
            print(f"✅ Positions retrieved: {len(positions.get('result', {}).get('list', []))} positions")
            
        else:
            print("⚠️  No API keys provided - skipping authenticated tests")
            print("   Set BYBIT_API_KEY and BYBIT_API_SECRET environment variables to test authenticated endpoints")
        
        print("🎉 All tests passed! Bybit API connection is working.")
        return True
        
    except Exception as e:
        print(f"❌ Error testing Bybit connection: {e}")
        return False


def test_websocket_connection():
    """Test WebSocket connection to Bybit"""
    print("\n🔄 Testing WebSocket connection...")
    
    try:
        from pybit.unified_trading import WebSocket
        
        def handle_message(message):
            print(f"📨 WebSocket message: {message}")
        
        # Create WebSocket connection for public data
        ws = WebSocket(
            testnet=True,
            channel_type="linear",
        )
        
        # Subscribe to ticker data
        ws.ticker_stream(
            symbol="BTCUSDT",
            callback=handle_message
        )
        
        print("✅ WebSocket connection established")
        
        # Let it run for a few seconds to receive some data
        import time
        time.sleep(3)
        
        print("🎉 WebSocket test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing WebSocket connection: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Starting Bybit API connectivity tests...\n")
    
    # Test HTTP connection
    http_success = asyncio.run(test_bybit_connection())
    
    # Test WebSocket connection
    ws_success = test_websocket_connection()
    
    print(f"\n📋 Test Results:")
    print(f"   HTTP API: {'✅ PASS' if http_success else '❌ FAIL'}")
    print(f"   WebSocket: {'✅ PASS' if ws_success else '❌ FAIL'}")
    
    if http_success and ws_success:
        print("\n🎉 All connectivity tests passed! Ready to proceed with development.")
    else:
        print("\n⚠️  Some tests failed. Please check your configuration and network connection.")

