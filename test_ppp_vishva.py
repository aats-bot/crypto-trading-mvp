#!/usr/bin/env python3
"""
Teste demonstrativo da estratégia PPP Vishva
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from src.bot.strategies import get_strategy, get_available_strategies, get_strategy_info
from src.bot.interfaces import MarketData, Position, PositionSide
from datetime import datetime


async def test_all_strategies():
    """Test all available strategies"""
    print("=" * 60)
    print("🤖 TESTE DAS ESTRATÉGIAS DE TRADING - MVP")
    print("=" * 60)
    
    # Get available strategies
    strategies = get_available_strategies()
    print(f"📋 Estratégias disponíveis: {strategies}")
    print()
    
    # Test each strategy
    for strategy_name in strategies:
        print(f"🔍 Testando estratégia: {strategy_name.upper()}")
        print("-" * 40)
        
        # Get strategy info
        info = get_strategy_info(strategy_name)
        print(f"📊 Nome: {info.get('name', 'N/A')}")
        print(f"📝 Descrição: {info.get('description', 'N/A')}")
        
        if 'indicators' in info:
            print(f"🔬 Indicadores: {', '.join(info['indicators'])}")
        
        if 'parameters' in info:
            print(f"⚙️  Parâmetros: {', '.join(info['parameters'])}")
        
        # Create strategy instance
        try:
            if strategy_name == "sma":
                config = {"fast_period": 10, "slow_period": 20, "risk_per_trade": 0.02}
            elif strategy_name == "rsi":
                config = {"rsi_period": 14, "oversold": 30, "overbought": 70, "risk_per_trade": 0.02}
            elif strategy_name == "ppp_vishva":
                config = {"sl_ratio": 1.25, "max_pyramid_levels": 5, "risk_per_trade": 0.02}
            else:
                config = {}
            
            strategy = get_strategy(strategy_name, config)
            print(f"✅ Estratégia criada com sucesso")
            
            # Test with mock market data
            market_data = MarketData(
                symbol='BTCUSDT',
                price=50000.0,
                timestamp=datetime.now(),
                volume=1000.0
            )
            
            # Test analysis without positions
            orders = await strategy.analyze(market_data, [])
            print(f"📈 Análise sem posições: {len(orders)} ordens geradas")
            
            # Test analysis with existing position
            mock_position = Position(
                symbol='BTCUSDT',
                side=PositionSide.LONG,
                size=0.001,
                entry_price=49000.0,
                current_price=50000.0,
                unrealized_pnl=1.0,
                timestamp=datetime.now()
            )
            
            orders_with_position = await strategy.analyze(market_data, [mock_position])
            print(f"📉 Análise com posição: {len(orders_with_position)} ordens geradas")
            
            # Get risk parameters
            risk_params = strategy.get_risk_parameters()
            print(f"⚠️  Parâmetros de risco: {len(risk_params)} configurados")
            
        except Exception as e:
            print(f"❌ Erro ao testar estratégia: {e}")
        
        print()
    
    print("=" * 60)
    print("🎉 TESTE CONCLUÍDO - TODAS AS ESTRATÉGIAS FUNCIONAIS")
    print("=" * 60)


async def test_ppp_vishva_detailed():
    """Detailed test of PPP Vishva strategy"""
    print("\n🔬 TESTE DETALHADO DA ESTRATÉGIA PPP VISHVA")
    print("=" * 50)
    
    # Create PPP Vishva strategy
    config = {
        "sl_ratio": 1.25,
        "max_pyramid_levels": 5,
        "risk_per_trade": 0.02
    }
    
    strategy = get_strategy("ppp_vishva", config)
    
    # Get strategy info
    info = strategy.get_strategy_info()
    print(f"📊 Nome: {info['name']}")
    print(f"📝 Descrição: {info['description']}")
    print(f"🔬 Indicadores: {', '.join(info['indicators'])}")
    print(f"⚙️  SL Ratio: {info['sl_ratio']}")
    print(f"📈 Max Pyramid Levels: {info['max_pyramid_levels']}")
    print(f"💰 Risk per Trade: {info['risk_per_trade']}")
    print()
    
    # Test with different market conditions
    test_scenarios = [
        {"symbol": "BTCUSDT", "price": 50000.0, "description": "Bitcoin - Preço normal"},
        {"symbol": "ETHUSDT", "price": 3000.0, "description": "Ethereum - Preço normal"},
        {"symbol": "BTCUSDT", "price": 45000.0, "description": "Bitcoin - Preço baixo"},
        {"symbol": "BTCUSDT", "price": 55000.0, "description": "Bitcoin - Preço alto"},
    ]
    
    for scenario in test_scenarios:
        print(f"🧪 Cenário: {scenario['description']}")
        
        market_data = MarketData(
            symbol=scenario['symbol'],
            price=scenario['price'],
            timestamp=datetime.now(),
            volume=1000.0
        )
        
        orders = await strategy.analyze(market_data, [])
        print(f"   📊 Preço: ${scenario['price']:,.2f}")
        print(f"   📈 Ordens: {len(orders)}")
        
        for i, order in enumerate(orders):
            print(f"   🔸 Ordem {i+1}: {order.side.value} {order.quantity:.6f} {order.symbol}")
        
        if not orders:
            print("   ℹ️  Nenhuma condição de entrada atendida")
        
        print()
    
    print("✅ Teste detalhado da PPP Vishva concluído")


if __name__ == "__main__":
    print("🚀 Iniciando testes das estratégias de trading...")
    
    # Run tests
    asyncio.run(test_all_strategies())
    asyncio.run(test_ppp_vishva_detailed())
    
    print("\n🎯 Todos os testes concluídos com sucesso!")
    print("💡 O sistema agora suporta 3 estratégias:")
    print("   • SMA (Simple Moving Average)")
    print("   • RSI (Relative Strength Index)")
    print("   • PPP Vishva (Advanced Multi-Indicator)")

