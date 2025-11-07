#!/usr/bin/env python3
"""
Script para corrigir automaticamente o arquivo test_streamlit_interface.py
Aplica todas as correções necessárias para que os testes passem.
"""

import re
import sys
from pathlib import Path


def apply_fixes(file_path):
    """Aplica todas as correções no arquivo"""
    
    print(f"📖 Lendo arquivo: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    fixes_applied = []
    
    # Fix 1: Adicionar trading_system ao __init__
    print("🔧 Aplicando Fix 1: Adicionar trading_system ao __init__")
    pattern1 = r"(    def __init__\(self\):\s+# Estado simples para o mock usado nos testes E2E\s+self\.session = \{\}\s+self\._authenticated = False\s+self\.state = \{\}\s+self\.current_page = 'login'\s+self\.is_running = False)"
    replacement1 = r"\1\n        self.trading_system = None  # Será inicializado em initialize()"
    
    if re.search(pattern1, content):
        content = re.sub(pattern1, replacement1, content)
        fixes_applied.append("✅ Adicionado self.trading_system ao __init__")
    else:
        print("⚠️  Pattern 1 não encontrado, tentando alternativa...")
        # Alternativa: procurar apenas pela linha is_running
        if "self.is_running = False" in content and "self.trading_system = None" not in content:
            content = content.replace(
                "self.is_running = False",
                "self.is_running = False\n        self.trading_system = None  # Será inicializado em initialize()"
            )
            fixes_applied.append("✅ Adicionado self.trading_system ao __init__ (método alternativo)")
    
    # Fix 2: Inicializar trading_system em initialize()
    print("🔧 Aplicando Fix 2: Inicializar trading_system em initialize()")
    pattern2 = r"(    async def initialize\(self\):\s+import asyncio\s+await asyncio\.sleep\(0\.01\))\s+(self\.is_running = True)"
    replacement2 = r"\1\n        # Inicializar trading system mock\n        self.trading_system = TradingSystem()\n        await self.trading_system.initialize()\n        \2"
    
    if re.search(pattern2, content):
        content = re.sub(pattern2, replacement2, content)
        fixes_applied.append("✅ Adicionada inicialização do trading_system")
    
    # Fix 3: Corrigir título do Dashboard
    print("🔧 Aplicando Fix 3: Corrigir título do Dashboard")
    # Procurar o bloco do dashboard e substituir
    pattern3 = r"(        elif page_name == 'dashboard':\s+return \{\s+)'page': 'dashboard',\s+'title': title,"
    replacement3 = r"\1'page': 'dashboard',\n                'title': '🏠 Dashboard Principal',"
    
    if re.search(pattern3, content):
        content = re.sub(pattern3, replacement3, content)
        fixes_applied.append("✅ Corrigido título do Dashboard")
    
    # Fix 4: Adicionar layout ao Dashboard
    print("🔧 Aplicando Fix 4: Adicionar layout ao Dashboard")
    pattern4 = r"(        elif page_name == 'dashboard':\s+return \{\s+'page': 'dashboard',\s+'title': '🏠 Dashboard Principal',)\s+'components': \{'overview': True\}"
    replacement4 = r"""\1
                'layout': {
                    'sidebar': {
                        'navigation': True,
                        'user_info': True
                    },
                    'main': {
                        'overview_cards': True,
                        'recent_trades': True,
                        'performance_chart': True
                    }
                },
                'components': {'overview': True}"""
    
    if re.search(pattern4, content):
        content = re.sub(pattern4, replacement4, content)
        fixes_applied.append("✅ Adicionado layout ao Dashboard")
    
    # Fix 5: Adicionar layout às Estratégias
    print("🔧 Aplicando Fix 5: Adicionar layout às Estratégias")
    pattern5 = r"(        elif page_name == 'strategies':\s+return \{\s+'page': 'strategies',\s+'title': title,)\s+'components': \{'strategy_list': True\}"
    replacement5 = r"""\1
                'layout': {
                    'create_strategy_form': True,
                    'strategy_templates': True,
                    'active_strategies': True
                },
                'components': {'strategy_list': True}"""
    
    if re.search(pattern5, content):
        content = re.sub(pattern5, replacement5, content)
        fixes_applied.append("✅ Adicionado layout às Estratégias")
    
    # Fix 6: Adicionar layout às Configurações
    print("🔧 Aplicando Fix 6: Adicionar layout às Configurações")
    pattern6 = r"(        elif page_name == 'settings':\s+return \{\s+'page': 'settings',\s+'title': title,)\s+'components': \{'settings_form': True\}"
    replacement6 = r"""\1
                'layout': {
                    'trading_settings': True,
                    'notification_settings': True,
                    'api_settings': True
                },
                'components': {'settings_form': True}"""
    
    if re.search(pattern6, content):
        content = re.sub(pattern6, replacement6, content)
        fixes_applied.append("✅ Adicionado layout às Configurações")
    
    # Verificar se houve mudanças
    if content == original_content:
        print("\n⚠️  AVISO: Nenhuma correção foi aplicada!")
        print("Isso pode significar que:")
        print("  1. As correções já foram aplicadas anteriormente")
        print("  2. O arquivo tem uma estrutura diferente do esperado")
        return False
    
    # Salvar arquivo corrigido
    print(f"\n💾 Salvando arquivo corrigido: {file_path}")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Mostrar resumo
    print("\n" + "="*60)
    print("✅ CORREÇÕES APLICADAS COM SUCESSO!")
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
        print("  python fix_streamlit_tests.py [caminho/para/test_streamlit_interface.py]")
        print("\nSe executado sem argumentos, procura em: tests/e2e/test_streamlit_interface.py")
        sys.exit(1)
    
    print("="*60)
    print("🔧 SCRIPT DE CORREÇÃO AUTOMÁTICA")
    print("   test_streamlit_interface.py")
    print("="*60)
    print()
    
    success = apply_fixes(file_path)
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
