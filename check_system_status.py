#!/usr/bin/env python3
"""
Script de diagnóstico completo do Crypto Trading Bot MVP
Verifica todos os componentes e status do sistema
"""
import subprocess
import requests
import psycopg2
import os
import sys
import time
from datetime import datetime

def print_header(title):
    """Imprimir cabeçalho formatado"""
    print("\n" + "=" * 70)
    print(f"🔍 {title}")
    print("=" * 70)

def print_status(component, status, details=""):
    """Imprimir status formatado"""
    status_icon = "✅" if status else "❌"
    print(f"{status_icon} {component:<30} {'OK' if status else 'ERRO'}")
    if details:
        print(f"   └─ {details}")

def check_processes():
    """Verificar processos rodando"""
    print_header("PROCESSOS DO SISTEMA")
    
    try:
        # Verificar processos Python
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                              capture_output=True, text=True, shell=True)
        python_processes = result.stdout.count('python.exe')
        
        print_status("Processos Python", python_processes > 0, f"{python_processes} processos encontrados")
        
        # Verificar Streamlit
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq streamlit.exe'], 
                              capture_output=True, text=True, shell=True)
        streamlit_running = 'streamlit.exe' in result.stdout
        
        print_status("Streamlit", streamlit_running)
        
        return python_processes > 0
        
    except Exception as e:
        print_status("Verificação de Processos", False, str(e))
        return False

def check_ports():
    """Verificar portas em uso"""
    print_header("PORTAS DO SISTEMA")
    
    ports_to_check = {
        8000: "API FastAPI",
        8501: "Dashboard Streamlit", 
        8502: "Dashboard Alternativo",
        5432: "PostgreSQL"
    }
    
    active_ports = {}
    
    for port, service in ports_to_check.items():
        try:
            result = subprocess.run(['netstat', '-an'], capture_output=True, text=True, shell=True)
            port_active = f":{port}" in result.stdout
            print_status(f"Porta {port} ({service})", port_active)
            active_ports[port] = port_active
        except Exception as e:
            print_status(f"Porta {port}", False, str(e))
            active_ports[port] = False
    
    return active_ports

def check_database():
    """Verificar conexão com banco de dados"""
    print_header("BANCO DE DADOS")
    
    try:
        # Tentar conectar ao PostgreSQL
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            database='crypto_trading_mvp',
            user='postgres',
            password='aats.dados'
        )
        
        cursor = conn.cursor()
        
        # Verificar tabelas
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = cursor.fetchall()
        
        print_status("Conexão PostgreSQL", True, f"{len(tables)} tabelas encontradas")
        
        # Verificar usuários
        cursor.execute("SELECT COUNT(*) FROM clients")
        user_count = cursor.fetchone()[0]
        
        print_status("Tabela Clients", True, f"{user_count} usuários cadastrados")
        
        # Verificar usuário admin
        cursor.execute("SELECT email FROM clients WHERE email = 'admin@trading.com'")
        admin_exists = cursor.fetchone() is not None
        
        print_status("Usuário Admin", admin_exists, "admin@trading.com")
        
        conn.close()
        return True
        
    except Exception as e:
        print_status("Banco de Dados", False, str(e))
        return False

def check_api():
    """Verificar API endpoints"""
    print_header("API ENDPOINTS")
    
    base_url = "http://localhost:8000"
    
    endpoints_to_check = [
        ("/", "Root"),
        ("/health", "Health Check"),
        ("/docs", "Documentação"),
        ("/api/auth/login", "Login"),
        ("/api/auth/register", "Registro")
    ]
    
    api_working = False
    
    for endpoint, name in endpoints_to_check:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            status = response.status_code < 500
            print_status(f"{name} ({endpoint})", status, f"Status: {response.status_code}")
            if endpoint == "/" and status:
                api_working = True
        except requests.exceptions.ConnectionError:
            print_status(f"{name} ({endpoint})", False, "Conexão recusada")
        except Exception as e:
            print_status(f"{name} ({endpoint})", False, str(e))
    
    return api_working

def check_dashboard():
    """Verificar dashboard"""
    print_header("DASHBOARD STREAMLIT")
    
    dashboard_urls = [
        "http://localhost:8501",
        "http://localhost:8502"
    ]
    
    dashboard_working = False
    
    for url in dashboard_urls:
        try:
            response = requests.get(url, timeout=5)
            status = response.status_code == 200
            port = url.split(':')[-1]
            print_status(f"Dashboard (porta {port})", status, f"Status: {response.status_code}")
            if status:
                dashboard_working = True
        except requests.exceptions.ConnectionError:
            port = url.split(':')[-1]
            print_status(f"Dashboard (porta {port})", False, "Conexão recusada")
        except Exception as e:
            port = url.split(':')[-1]
            print_status(f"Dashboard (porta {port})", False, str(e))
    
    return dashboard_working

def check_authentication():
    """Verificar autenticação"""
    print_header("SISTEMA DE AUTENTICAÇÃO")
    
    try:
        # Testar login via API
        login_data = {
            "email": "admin@trading.com",
            "password": "admin123"
        }
        
        response = requests.post(
            "http://localhost:8000/api/auth/login",
            json=login_data,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_status("Login API", True, f"Token gerado para {data.get('client', {}).get('email', 'N/A')}")
            return True
        else:
            print_status("Login API", False, f"Status: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print_status("Login API", False, str(e))
        return False

def check_configuration():
    """Verificar configurações"""
    print_header("CONFIGURAÇÕES")
    
    config_files = [
        ("config/settings.py", "Settings Principal"),
        (".env", "Variáveis de Ambiente"),
        ("requirements.txt", "Dependências"),
        ("start_services.py", "Script de Inicialização")
    ]
    
    for file_path, name in config_files:
        exists = os.path.exists(file_path)
        print_status(name, exists, file_path)
    
    # Verificar variáveis de ambiente importantes
    env_vars = [
        "DATABASE_URL",
        "STREAMLIT_PORT"
    ]
    
    for var in env_vars:
        value = os.environ.get(var)
        print_status(f"ENV: {var}", value is not None, value or "Não definida")

def test_login_credentials():
    """Testar credenciais de login"""
    print_header("TESTE DE CREDENCIAIS")
    
    credentials_to_test = [
        ("admin@trading.com", "admin123"),
        ("admin@admin.com", "123456")
    ]
    
    for email, password in credentials_to_test:
        try:
            response = requests.post(
                "http://localhost:8000/api/auth/login",
                json={"email": email, "password": password},
                timeout=5
            )
            
            status = response.status_code == 200
            print_status(f"Login: {email}", status, f"Senha: {password}")
            
        except Exception as e:
            print_status(f"Login: {email}", False, str(e))

def generate_summary(results):
    """Gerar resumo do diagnóstico"""
    print_header("RESUMO DO DIAGNÓSTICO")
    
    total_checks = len(results)
    passed_checks = sum(results.values())
    
    print(f"📊 Total de verificações: {total_checks}")
    print(f"✅ Verificações OK: {passed_checks}")
    print(f"❌ Verificações com erro: {total_checks - passed_checks}")
    print(f"📈 Taxa de sucesso: {(passed_checks/total_checks)*100:.1f}%")
    
    if passed_checks == total_checks:
        print("\n🎉 SISTEMA TOTALMENTE OPERACIONAL!")
        print("✅ Todos os componentes estão funcionando corretamente")
        print("\n🌐 ACESSO:")
        print("📊 Dashboard: http://localhost:8501")
        print("🔗 API Docs: http://localhost:8000/docs")
        print("\n🎯 CREDENCIAIS:")
        print("📧 Email: admin@trading.com")
        print("🔑 Senha: admin123")
    else:
        print("\n⚠️  SISTEMA COM PROBLEMAS")
        print("💡 Verifique os componentes com erro acima")
        print("🔧 Execute: python start_services.py")

def main():
    """Função principal"""
    print("=" * 70)
    print("🤖 CRYPTO TRADING BOT MVP - DIAGNÓSTICO COMPLETO")
    print("=" * 70)
    print(f"📅 Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Executar todas as verificações
    results = {}
    
    results['processes'] = check_processes()
    results['ports'] = any(check_ports().values())
    results['database'] = check_database()
    results['api'] = check_api()
    results['dashboard'] = check_dashboard()
    results['auth'] = check_authentication()
    
    check_configuration()
    test_login_credentials()
    
    # Gerar resumo
    generate_summary(results)
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()

