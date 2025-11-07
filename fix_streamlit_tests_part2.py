#!/usr/bin/env python3
"""
Script para aplicar correções adicionais no arquivo test_streamlit_interface.py
Resolve os erros restantes após a primeira rodada de correções.
"""

import re
import sys
from pathlib import Path


def apply_additional_fixes(file_path):
    """Aplica correções adicionais no arquivo"""
    
    print(f"📖 Lendo arquivo: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    fixes_applied = []
    
    # Fix 1: Atualizar layout do Dashboard com mais detalhes
    print("🔧 Aplicando Fix 1: Adicionar symbol_selector e outros componentes ao Dashboard")
    
    pattern1 = r"(        elif page_name == 'dashboard':\s+return \{\s+'page': 'dashboard',\s+'title': '🏠 Dashboard Principal',\s+'layout': \{\s+'sidebar': \{\s+'navigation': True,\s+'user_info': True\s+\},\s+'main': \{)\s+'overview_cards': True,\s+'recent_trades': True,\s+'performance_chart': True\s+\}"
    
    replacement1 = r"""\1
                        'metrics_row': True,
                        'market_data_card': True,
                        'positions_table': True
                    }
                },
                'components': {'overview': True}
            }
        else:
            return {
                'page': page_name,
                'title': title,
                'components': {}
            }
    
    async def handle_widget_interaction(self, widget_id: str, value, event_type: str):
        import asyncio, time
        await asyncio.sleep(0.01)

        # Campos do formulário de login
        if widget_id in ('username', 'password'):
            self.state[widget_id] = value
            return {'status': 'updated'}

        # Botão de login
        if widget_id == 'login_btn' and event_type == 'click':
            username = self.state.get('username')
            password = self.state.get('password')
            if username and password:
                self._authenticated = True
                self.session['authenticated'] = True
                self.session['user'] = username
                self.session['user_id'] = self.session.get('user_id') or f"uid_{int(time.time())}"
                return {'success': True, 'user': username}
            return {'success': False, 'error': 'missing credentials'}
        
        # Seletor de símbolo
        if widget_id == 'symbol_selector' and event_type == 'change':
            self.session['selected_symbol'] = value
            return {'symbol_changed': True, 'new_symbol': value}

        # Campos do formulário de ordem
        if widget_id in ('order_symbol', 'order_side', 'order_quantity'):
            self.state[widget_id] = value
            return {'status': 'updated'}

        # Execução da ordem
        if widget_id == 'place_order_btn' and event_type == 'click':
            order = {
                'symbol': self.state.get('order_symbol', 'BTCUSDT'),
                'side': self.state.get('order_side', 'buy'),
                'quantity': self.state.get('order_quantity', 0.1),
                'timestamp': int(time.time())
            }
            trade_result = {
                'status': 'filled',
                'filled_qty': order['quantity'],
                'avg_price': 50000
            }
            return {
                'success': True,
                'order': order,
                'trade_result': trade_result,
                'message': 'Ordem executada com sucesso'
            }
        
        # Criação de estratégia
        if widget_id in ('strategy_name', 'strategy_type', 'strategy_risk'):
            self.state[widget_id] = value
            return {'status': 'updated'}
        
        if widget_id == 'create_strategy_btn' and event_type == 'click':
            strategy = {
                'name': self.state.get('strategy_name', 'New Strategy'),
                'type': self.state.get('strategy_type', 'ppp_vishva'),
                'risk': self.state.get('strategy_risk', 1.0),
                'created_at': int(time.time())
            }
            return {
                'success': True,
                'strategy': strategy,
                'message': 'Estratégia criada com sucesso'
            }
        
        # Configurações
        if widget_id in ('api_key', 'api_secret', 'notification_email', 'max_risk'):
            self.state[widget_id] = value
            return {'status': 'updated'}
        
        if widget_id == 'save_settings_btn' and event_type == 'click':
            settings = {
                'api_key': self.state.get('api_key', ''),
                'notification_email': self.state.get('notification_email', ''),
                'max_risk': self.state.get('max_risk', 2.0),
                'updated_at': int(time.time())
            }
            return {
                'success': True,
                'settings': settings,
                'message': 'Configurações salvas com sucesso'
            }

        return {'status': 'unknown_widget'}"""
    
    # Primeiro, vamos encontrar e substituir o layout do dashboard
    dashboard_pattern = r"(        elif page_name == 'dashboard':\s+return \{\s+'page': 'dashboard',\s+'title': '🏠 Dashboard Principal',\s+'layout': \{\s+'sidebar': \{)\s+'navigation': True,\s+'user_info': True"
    
    dashboard_replacement = r"""\1
                    'navigation': True,
                    'user_info': True,
                    'symbol_selector': True"""
    
    if re.search(dashboard_pattern, content):
        content = re.sub(dashboard_pattern, dashboard_replacement, content)
        fixes_applied.append("✅ Adicionado symbol_selector ao sidebar do Dashboard")
    
    # Atualizar o main do dashboard
    dashboard_main_pattern = r"(                    'main': \{)\s+'overview_cards': True,\s+'recent_trades': True,\s+'performance_chart': True"
    dashboard_main_replacement = r"""\1
                        'metrics_row': True,
                        'market_data_card': True,
                        'positions_table': True"""
    
    if re.search(dashboard_main_pattern, content):
        content = re.sub(dashboard_main_pattern, dashboard_main_replacement, content)
        fixes_applied.append("✅ Atualizado conteúdo main do Dashboard")
    
    # Fix 2: Adicionar métodos de widget interaction para estratégias e configurações
    print("🔧 Aplicando Fix 2: Adicionar handlers para estratégias e configurações")
    
    # Procurar onde termina o método handle_widget_interaction atual
    widget_method_pattern = r"(        return \{\s+'success': True,\s+'order': order,\s+'trade_result': trade_result,\s+'message': 'Ordem executada com sucesso'\s+\})\s+return \{'status': 'unknown_widget'\}"
    
    widget_method_replacement = r"""\1
        
        # Criação de estratégia
        if widget_id in ('strategy_name', 'strategy_type', 'strategy_risk'):
            self.state[widget_id] = value
            return {'status': 'updated'}
        
        if widget_id == 'create_strategy_btn' and event_type == 'click':
            strategy = {
                'name': self.state.get('strategy_name', 'New Strategy'),
                'type': self.state.get('strategy_type', 'ppp_vishva'),
                'risk': self.state.get('strategy_risk', 1.0),
                'created_at': int(time.time())
            }
            return {
                'success': True,
                'strategy': strategy,
                'message': 'Estratégia criada com sucesso'
            }
        
        # Configurações
        if widget_id in ('api_key', 'api_secret', 'notification_email', 'max_risk'):
            self.state[widget_id] = value
            return {'status': 'updated'}
        
        if widget_id == 'save_settings_btn' and event_type == 'click':
            settings = {
                'api_key': self.state.get('api_key', ''),
                'notification_email': self.state.get('notification_email', ''),
                'max_risk': self.state.get('max_risk', 2.0),
                'updated_at': int(time.time())
            }
            return {
                'success': True,
                'settings': settings,
                'message': 'Configurações salvas com sucesso'
            }

        return {'status': 'unknown_widget'}"""
    
    if re.search(widget_method_pattern, content):
        content = re.sub(widget_method_pattern, widget_method_replacement, content)
        fixes_applied.append("✅ Adicionados handlers para criação de estratégias")
        fixes_applied.append("✅ Adicionados handlers para salvar configurações")
    
    # Fix 3: Corrigir chamadas ao banco de dados para incluir strategy_id
    print("🔧 Aplicando Fix 3: Adicionar strategy_id padrão nas chamadas ao banco")
    
    # Encontrar o método execute_trade do TradingSystem e adicionar strategy_id
    execute_trade_pattern = r"(async def execute_trade\(self, user_id: str, symbol: str, side: str, quantity: float\):.*?position = await self\.database\.create_position\()\s+user_id=user_id,"
    
    execute_trade_replacement = r"\1\n                user_id=user_id,\n                strategy_id=1,  # ID padrão para testes"
    
    if re.search(execute_trade_pattern, content, re.DOTALL):
        content = re.sub(execute_trade_pattern, execute_trade_replacement, content, flags=re.DOTALL)
        fixes_applied.append("✅ Adicionado strategy_id padrão nas chamadas ao banco")
    
    # Verificar se houve mudanças
    if content == original_content:
        print("\n⚠️  AVISO: Nenhuma correção adicional foi aplicada!")
        print("Isso pode significar que:")
        print("  1. As correções já foram aplicadas anteriormente")
        print("  2. O arquivo tem uma estrutura diferente do esperado")
        print("  3. As correções da Parte 1 ainda não foram aplicadas")
        return False
    
    # Salvar arquivo corrigido
    print(f"\n💾 Salvando arquivo corrigido: {file_path}")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Mostrar resumo
    print("\n" + "="*60)
    print("✅ CORREÇÕES ADICIONAIS APLICADAS COM SUCESSO!")
    print("="*60)
    for fix in fixes_applied:
        print(f"  {fix}")
    print("\n🚀 Execute os testes novamente:")
    print("   pytest tests/e2e/test_streamlit_interface.py -v")
    print("="*60)
    
    return True


def main():
    # Determinar caminho do arquivo
    if len(sys.argv) > 1:
        file_path = Path(sys.argv[1])
    else:
        file_path = Path("tests/e2e/test_streamlit_interface.py")
    
    if not file_path.exists():
        print(f"❌ ERRO: Arquivo não encontrado: {file_path}")
        print("\nUso:")
        print("  python fix_streamlit_tests_part2.py [caminho/para/test_streamlit_interface.py]")
        print("\nSe executado sem argumentos, procura em: tests/e2e/test_streamlit_interface.py")
        sys.exit(1)
    
    print("="*60)
    print("🔧 SCRIPT DE CORREÇÃO ADICIONAL (PARTE 2)")
    print("   test_streamlit_interface.py")
    print("="*60)
    print()
    
    success = apply_additional_fixes(file_path)
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
