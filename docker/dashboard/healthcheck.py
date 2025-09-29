#!/usr/bin/env python3
"""
Crypto Trading MVP - Dashboard Health Check
"""

import sys
import os
import urllib.request
import urllib.error
from datetime import datetime

def log(message, level="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] DASHBOARD-HEALTHCHECK {level}: {message}")

def check_streamlit_endpoint():
    """Verifica se o Streamlit está respondendo"""
    try:
        port = os.getenv('STREAMLIT_SERVER_PORT', '8501')
        url = f"http://127.0.0.1:{port}/_stcore/health"
        
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'HealthCheck/1.0')
        
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                log("Streamlit endpoint healthy")
                return True
            else:
                log(f"Streamlit endpoint returned status {response.status}", "ERROR")
                return False
                
    except Exception as e:
        log(f"Failed to check Streamlit endpoint: {e}", "ERROR")
        return False

def check_api_connectivity():
    """Verifica conectividade com API"""
    try:
        api_url = os.getenv('API_URL', 'http://localhost:8000')
        health_url = f"{api_url}/health"
        
        req = urllib.request.Request(health_url)
        req.add_header('User-Agent', 'Dashboard-HealthCheck/1.0')
        
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                log("API connectivity OK")
                return True
            else:
                log(f"API returned status {response.status}", "WARNING")
                return True  # Não crítico para dashboard
                
    except Exception as e:
        log(f"API connectivity check failed: {e}", "WARNING")
        return True  # Não crítico

def main():
    log("Starting dashboard health check...")
    
    checks = [
        ("Streamlit Endpoint", check_streamlit_endpoint),
        ("API Connectivity", check_api_connectivity),
    ]
    
    failed_checks = []
    
    for check_name, check_func in checks:
        try:
            if not check_func():
                failed_checks.append(check_name)
        except Exception as e:
            log(f"Exception in {check_name} check: {e}", "ERROR")
            failed_checks.append(check_name)
    
    if failed_checks:
        log(f"Health check FAILED. Failed checks: {', '.join(failed_checks)}", "ERROR")
        sys.exit(1)
    else:
        log("Health check PASSED. Dashboard operational.")
        sys.exit(0)

if __name__ == "__main__":
    main()

