#!/usr/bin/env python3
"""
Script to start all services for the Crypto Trading MVP
"""
import subprocess
import time
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from config.settings import settings

def start_api():
    """Start the FastAPI server"""
    print("🚀 Starting FastAPI server...")
    api_process = subprocess.Popen([
        sys.executable, "src/api/main.py"
    ], cwd=project_root)
    
    # Wait for API to start
    time.sleep(3)
    return api_process

def start_dashboard():
    """Start the Streamlit dashboard"""
    print("🎨 Starting Streamlit dashboard...")
    dashboard_process = subprocess.Popen([
        "streamlit", "run", "src/dashboard/main.py",
        "--server.port", str(settings.streamlit_port),
        "--server.address", settings.streamlit_server_address,
        "--browser.gatherUsageStats", "false"
    ], cwd=project_root)
    
    return dashboard_process

def start_bot_worker():
    """Start the bot worker"""
    print("🤖 Starting bot worker...")
    worker_process = subprocess.Popen([
        sys.executable, "src/bot/worker.py"
    ], cwd=project_root)
    
    return worker_process

def main():
    """Main function to start all services"""
    print("=" * 50)
    print("🚀 Crypto Trading Bot MVP - Starting Services")
    print("=" * 50)
    
    processes = []
    
    try:
        # Start API
        api_process = start_api()
        processes.append(("API", api_process))
        
        # Start Dashboard
        dashboard_process = start_dashboard()
        processes.append(("Dashboard", dashboard_process))
        
        # Start Bot Worker
        worker_process = start_bot_worker()
        processes.append(("Bot Worker", worker_process))
        
        print("\n✅ All services started successfully!")
        print(f"📊 Dashboard: http://localhost:{settings.streamlit_port}")
        print(f"🔗 API Docs: http://localhost:{settings.api_port}/docs")
        print("\n⏹️  Press Ctrl+C to stop all services")
        
        # Wait for processes
        while True:
            time.sleep(1)
            
            # Check if any process died
            for name, process in processes:
                if process.poll() is not None:
                    print(f"❌ {name} process died with code {process.returncode}")
                    return
    
    except KeyboardInterrupt:
        print("\n🛑 Stopping all services...")
        
        for name, process in processes:
            print(f"⏹️  Stopping {name}...")
            process.terminate()
            
            # Wait for graceful shutdown
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print(f"🔪 Force killing {name}...")
                process.kill()
        
        print("✅ All services stopped")

if __name__ == "__main__":
    main()

