#!/usr/bin/env python3
"""
Script de diagnóstico do sistema Crypto Trading MVP
Identifica problemas comuns e sugere soluções
"""
import os
import sys
import subprocess
import socket
from pathlib import Path

def check_python_version():
    """Verifica a versão do Python"""
    print("🐍 Verificando Python...")
    version = sys.version_info
    print(f"   Versão: {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 8:
        print("   ✅ Versão do Python adequada")
        return True
    else:
        print("   ❌ Python 3.8+ necessário")
        return False

def check_dependencies():
    """Verifica dependências Python essenciais"""
    print("\n📦 Verificando dependências...")
    
    required_packages = [
        'psycopg2',
        'fastapi', 
        'uvicorn',
        'streamlit',
        'pydantic',
        'bcrypt',
        'asyncpg'
    ]
    
    missing = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} - FALTANDO")
            missing.append(package)
    
    if missing:
        print(f"\n💡 Para instalar dependências faltantes:")
        print(f"   pip install {' '.join(missing)}")
        return False
    
    return True

def check_postgresql():
    """Verifica se PostgreSQL está acessível"""
    print("\n🐘 Verificando PostgreSQL...")
    
    try:
        import psycopg2
        
        # Tentar conectar
        conn = psycopg2.connect(
            host="localhost",
            port="5432", 
            database="postgres",  # Conectar ao banco padrão primeiro
            user="postgres",
            password="aats.dados",
            connect_timeout=5
        )
        conn.close()
        print("   ✅ PostgreSQL acessível")
        
        # Verificar se o banco crypto_trading_mvp existe
        try:
            conn = psycopg2.connect(
                host="localhost",
                port="5432",
                database="crypto_trading_mvp",
                user="postgres", 
                password="aats.dados",
                connect_timeout=5
            )
            conn.close()
            print("   ✅ Banco crypto_trading_mvp existe")
            return True
        except psycopg2.OperationalError:
            print("   ⚠️  Banco crypto_trading_mvp não existe")
            print("   💡 Execute: createdb -U postgres crypto_trading_mvp")
            return False
            
    except ImportError:
        print("   ❌ psycopg2 não instalado")
        print("   💡 Execute: pip install psycopg2-binary")
        return False
    except psycopg2.OperationalError as e:
        print(f"   ❌ Erro de conexão: {e}")
        print("   💡 Verifique se PostgreSQL está rodando")
        print("   💡 Verifique usuário/senha: postgres/aats.dados")
        return False
    except Exception as e:
        print(f"   ❌ Erro inesperado: {e}")
        return False

def check_ports():
    """Verifica se as portas necessárias estão livres"""
    print("\n🔌 Verificando portas...")
    
    ports_to_check = [
        (8000, "API FastAPI"),
        (8501, "Dashboard Streamlit"),
        (5432, "PostgreSQL")
    ]
    
    all_good = True
    
    for port, service in ports_to_check:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        
        try:
            result = sock.connect_ex(('localhost', port))
            if result == 0:
                print(f"   ⚠️  Porta {port} ({service}) está em uso")
                if port != 5432:  # PostgreSQL deve estar em uso
                    all_good = False
            else:
                if port == 5432:
                    print(f"   ❌ Porta {port} ({service}) não está em uso")
                    all_good = False
                else:
                    print(f"   ✅ Porta {port} ({service}) disponível")
        except Exception as e:
            print(f"   ❌ Erro ao verificar porta {port}: {e}")
            all_good = False
        finally:
            sock.close()
    
    return all_good

def check_project_structure():
    """Verifica a estrutura do projeto"""
    print("\n📁 Verificando estrutura do projeto...")
    
    required_files = [
        'src/api/main.py',
        'src/dashboard/main.py', 
        'src/bot/worker.py',
        'config/settings.py',
        '.env',
        'start_services.py'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} - FALTANDO")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n💡 Arquivos faltando: {len(missing_files)}")
        return False
    
    return True

def check_environment_variables():
    """Verifica variáveis de ambiente"""
    print("\n🌍 Verificando variáveis de ambiente...")
    
    if Path('.env').exists():
        print("   ✅ Arquivo .env existe")
        
        # Ler algumas variáveis importantes
        try:
            with open('.env', 'r') as f:
                content = f.read()
                
            if 'DATABASE_URL' in content:
                print("   ✅ DATABASE_URL configurada")
            else:
                print("   ❌ DATABASE_URL não encontrada")
                
            if 'API_PORT' in content:
                print("   ✅ API_PORT configurada")
            else:
                print("   ❌ API_PORT não encontrada")
                
            return True
        except Exception as e:
            print(f"   ❌ Erro ao ler .env: {e}")
            return False
    else:
        print("   ❌ Arquivo .env não encontrado")
        return False

def suggest_solutions(issues):
    """Sugere soluções para problemas encontrados"""
    if not issues:
        return
    
    print("\n🔧 SOLUÇÕES SUGERIDAS:")
    print("=" * 50)
    
    if 'python' in issues:
        print("📌 PYTHON:")
        print("   - Instale Python 3.8 ou superior")
        print("   - https://www.python.org/downloads/")
        print()
    
    if 'dependencies' in issues:
        print("📌 DEPENDÊNCIAS:")
        print("   pip install psycopg2-binary fastapi uvicorn streamlit pydantic bcrypt asyncpg")
        print()
    
    if 'postgresql' in issues:
        print("📌 POSTGRESQL:")
        print("   Windows:")
        print("   - Baixe: https://www.postgresql.org/download/windows/")
        print("   - Instale com senha 'aats.dados' para usuário postgres")
        print("   - Crie banco: createdb -U postgres crypto_trading_mvp")
        print()
        print("   Linux/WSL:")
        print("   - sudo apt install postgresql postgresql-contrib")
        print("   - sudo -u postgres psql -c \"ALTER USER postgres PASSWORD 'aats.dados';\"")
        print("   - sudo -u postgres createdb crypto_trading_mvp")
        print()
    
    if 'ports' in issues:
        print("📌 PORTAS:")
        print("   - Feche aplicações usando portas 8000 e 8501")
        print("   - Windows: netstat -ano | findstr :8000")
        print("   - Linux: lsof -i :8000")
        print()
    
    if 'structure' in issues:
        print("📌 ESTRUTURA DO PROJETO:")
        print("   - Verifique se está no diretório correto")
        print("   - Re-extraia o projeto se necessário")
        print()

def run_quick_fix():
    """Executa correções rápidas automáticas"""
    print("\n🔧 Executando correções automáticas...")
    
    # Instalar dependências básicas
    try:
        print("   📦 Instalando dependências essenciais...")
        subprocess.run([
            sys.executable, '-m', 'pip', 'install', 
            'psycopg2-binary', 'fastapi', 'uvicorn', 'streamlit', 'bcrypt'
        ], check=True, capture_output=True)
        print("   ✅ Dependências instaladas")
    except subprocess.CalledProcessError:
        print("   ❌ Falha ao instalar dependências")
    
    # Criar diretórios se necessário
    dirs_to_create = ['logs', 'data', 'backups']
    for dir_name in dirs_to_create:
        Path(dir_name).mkdir(exist_ok=True)
    print("   ✅ Diretórios criados")

def main():
    """Função principal de diagnóstico"""
    print("=" * 60)
    print("🔍 DIAGNÓSTICO DO SISTEMA - CRYPTO TRADING MVP")
    print("=" * 60)
    
    issues = []
    
    # Executar verificações
    if not check_python_version():
        issues.append('python')
    
    if not check_dependencies():
        issues.append('dependencies')
    
    if not check_postgresql():
        issues.append('postgresql')
    
    if not check_ports():
        issues.append('ports')
    
    if not check_project_structure():
        issues.append('structure')
    
    if not check_environment_variables():
        issues.append('environment')
    
    print("\n" + "=" * 60)
    
    if not issues:
        print("🎉 SISTEMA OK - TODOS OS TESTES PASSARAM!")
        print("\n✅ Próximos passos:")
        print("   1. python init_database_windows.py")
        print("   2. python start_services.py")
        print("   3. Acesse http://localhost:8501")
    else:
        print(f"⚠️  PROBLEMAS ENCONTRADOS: {len(issues)}")
        suggest_solutions(issues)
        
        print("\n🔧 Executar correções automáticas? (s/n): ", end="")
        try:
            response = input().lower()
            if response in ['s', 'sim', 'y', 'yes']:
                run_quick_fix()
        except KeyboardInterrupt:
            print("\n\n👋 Diagnóstico cancelado")
    
    print("=" * 60)

if __name__ == "__main__":
    main()

