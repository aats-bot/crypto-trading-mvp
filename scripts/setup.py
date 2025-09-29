#!/usr/bin/env python3
"""
Script de Setup - Crypto Trading MVP
Configura ambiente completo do projeto unificado
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_banner():
    """Exibe banner do projeto"""
    print("=" * 60)
    print("🚀 CRYPTO TRADING MVP - SETUP")
    print("📊 Bot de Trading Automatizado com Infraestrutura de Testes")
    print("=" * 60)
    print()

def check_python_version():
    """Verifica versão do Python"""
    print("🔍 Verificando versão do Python...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Erro: Python 3.8+ é necessário")
        print(f"   Versão atual: {version.major}.{version.minor}.{version.micro}")
        sys.exit(1)
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
    print()

def create_virtual_environment():
    """Cria ambiente virtual"""
    print("🔧 Configurando ambiente virtual...")
    
    venv_path = Path("venv")
    if venv_path.exists():
        print("ℹ️  Ambiente virtual já existe")
    else:
        try:
            subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
            print("✅ Ambiente virtual criado")
        except subprocess.CalledProcessError:
            print("❌ Erro ao criar ambiente virtual")
            sys.exit(1)
    
    # Instruções de ativação
    system = platform.system().lower()
    if system == "windows":
        activate_cmd = "venv\\Scripts\\activate"
    else:
        activate_cmd = "source venv/bin/activate"
    
    print(f"💡 Para ativar: {activate_cmd}")
    print()

def install_dependencies():
    """Instala dependências"""
    print("📦 Instalando dependências...")
    
    # Detectar se está em ambiente virtual
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    
    if not in_venv:
        print("⚠️  Recomendado: Ative o ambiente virtual primeiro")
        response = input("Continuar mesmo assim? (y/N): ")
        if response.lower() != 'y':
            print("Setup cancelado")
            return
    
    try:
        # Instalar dependências principais
        print("📋 Instalando dependências principais...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        
        # Instalar dependências de teste
        print("🧪 Instalando dependências de teste...")
        test_req = "requirements-test-windows.txt" if platform.system() == "Windows" else "requirements-test.txt"
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", test_req], check=True)
        
        print("✅ Dependências instaladas com sucesso")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao instalar dependências: {e}")
        sys.exit(1)
    
    print()

def setup_configuration():
    """Configura arquivos de configuração"""
    print("⚙️  Configurando arquivos...")
    
    # Criar arquivo .env se não existir
    env_file = Path(".env")
    if not env_file.exists():
        env_content = """# Crypto Trading MVP - Configurações
# Copie este arquivo para .env e configure suas chaves

# API Keys (Configure com suas chaves reais)
BYBIT_API_KEY=your_api_key_here
BYBIT_SECRET_KEY=your_secret_key_here

# Database
DATABASE_URL=sqlite:///data/trading.db

# Security
JWT_SECRET_KEY=your_jwt_secret_key_here
ENCRYPTION_KEY=your_encryption_key_here

# Trading Configuration
DEFAULT_RISK_PER_TRADE=0.02
MAX_POSITIONS=3
ENABLE_LIVE_TRADING=false

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/trading.log

# Dashboard
STREAMLIT_PORT=8501
API_PORT=8000
"""
        env_file.write_text(env_content)
        print("✅ Arquivo .env.example criado")
    
    # Criar diretórios necessários
    directories = ["data", "logs", "backups"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    print("✅ Diretórios criados")
    print()

def run_tests():
    """Executa testes para validar instalação"""
    print("🧪 Executando testes de validação...")
    
    try:
        # Teste rápido
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/unit/test_ppp_vishva_strategy.py", 
            "-v", "--tb=short"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Testes de validação passaram")
            print(f"📊 {result.stdout.count('PASSED')} testes executados com sucesso")
        else:
            print("⚠️  Alguns testes falharam (normal em setup inicial)")
            print("💡 Execute 'pytest tests/' para diagnóstico completo")
        
    except FileNotFoundError:
        print("ℹ️  Pytest não encontrado - instale dependências primeiro")
    
    print()

def show_next_steps():
    """Mostra próximos passos"""
    print("🎯 SETUP CONCLUÍDO!")
    print()
    print("📋 Próximos passos:")
    print("1. Ative o ambiente virtual:")
    
    system = platform.system().lower()
    if system == "windows":
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    
    print()
    print("2. Configure suas API keys no arquivo .env")
    print()
    print("3. Execute os testes:")
    print("   pytest tests/ -v")
    print()
    print("4. Inicie a aplicação:")
    print("   python app/main.py              # API")
    print("   streamlit run app/dashboard.py  # Dashboard")
    print()
    print("📚 Documentação completa: README.md")
    print("🎉 Projeto pronto para desenvolvimento!")

def main():
    """Função principal"""
    print_banner()
    
    try:
        check_python_version()
        create_virtual_environment()
        install_dependencies()
        setup_configuration()
        run_tests()
        show_next_steps()
        
    except KeyboardInterrupt:
        print("\n❌ Setup cancelado pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

