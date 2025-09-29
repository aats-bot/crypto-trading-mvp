"""
Crypto Trading MVP - API Health Check
Script de verificação de saúde para container da API
"""

import sys
import os
import time
import json
import urllib.request
import urllib.error
from datetime import datetime

def log(message, level="INFO"):
    """Log com timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] HEALTHCHECK {level}: {message}")

def check_api_endpoint():
    """Verifica se o endpoint da API está respondendo"""
    try:
        host = os.getenv('UVICORN_HOST', '0.0.0.0')
        port = os.getenv('UVICORN_PORT', '8000')
        
        # Se host for 0.0.0.0, usar localhost para health check
        if host == '0.0.0.0':
            host = '127.0.0.1'
        
        url = f"http://{host}:{port}/health"
        
        # Configurar timeout curto para health check
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'HealthCheck/1.0')
        
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                data = response.read().decode('utf-8')
                try:
                    health_data = json.loads(data)
                    if health_data.get('status') == 'healthy':
                        log(f"API endpoint healthy: {health_data}")
                        return True
                    else:
                        log(f"API endpoint unhealthy: {health_data}", "ERROR")
                        return False
                except json.JSONDecodeError:
                    log(f"API responded but invalid JSON: {data}", "WARNING")
                    return True  # API está respondendo, mesmo que formato seja inesperado
            else:
                log(f"API endpoint returned status {response.status}", "ERROR")
                return False
                
    except urllib.error.URLError as e:
        log(f"Failed to connect to API endpoint: {e}", "ERROR")
        return False
    except Exception as e:
        log(f"Unexpected error checking API endpoint: {e}", "ERROR")
        return False

def check_database_connection():
    """Verifica conectividade com banco de dados"""
    try:
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            log("DATABASE_URL not configured, skipping DB check", "WARNING")
            return True
        
        # Importar apenas se necessário
        import urllib.parse
        
        # Parse da URL do banco
        parsed = urllib.parse.urlparse(database_url)
        
        if parsed.scheme.startswith('postgresql'):
            return check_postgresql_connection(parsed)
        elif parsed.scheme.startswith('sqlite'):
            return check_sqlite_connection(database_url)
        else:
            log(f"Unsupported database scheme: {parsed.scheme}", "WARNING")
            return True
            
    except Exception as e:
        log(f"Error checking database connection: {e}", "ERROR")
        return False

def check_postgresql_connection(parsed_url):
    """Verifica conexão PostgreSQL"""
    try:
        import socket
        
        host = parsed_url.hostname or 'localhost'
        port = parsed_url.port or 5432
        
        # Teste básico de conectividade TCP
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((host, port))
        sock.close()
        
