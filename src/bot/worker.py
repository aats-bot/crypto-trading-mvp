#!/usr/bin/env python3
"""
Crypto Trading MVP - Bot Worker
Worker para processamento assíncrono de trading
"""

import asyncio
import logging
import os
import signal
import sys
from datetime import datetime
from typing import Optional

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/app/logs/worker.log', mode='a') if os.path.exists('/app/logs') else logging.NullHandler()
    ]
)

logger = logging.getLogger(__name__)

class TradingWorker:
    """Worker principal para processamento de trading"""
    
    def __init__(self):
        self.running = False
        self.tasks = []
        
    async def start(self):
        """Inicia o worker"""
        logger.info("🚀 Iniciando Trading Worker...")
        self.running = True
        
        # Verificar variáveis de ambiente
        self._check_environment()
        
        # Configurar signal handlers
        self._setup_signal_handlers()
        
        # Iniciar tasks principais
        await self._start_main_tasks()
        
    def _check_environment(self):
        """Verifica variáveis de ambiente necessárias"""
        required_vars = [
            'DATABASE_URL',
            'REDIS_URL'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            logger.warning(f"⚠️  Variáveis de ambiente não configuradas: {missing_vars}")
        else:
            logger.info("✅ Variáveis de ambiente verificadas")
    
    def _setup_signal_handlers(self):
        """Configura handlers para shutdown graceful"""
        def signal_handler(signum, frame):
            logger.info(f"📡 Recebido sinal {signum}, iniciando shutdown...")
            self.running = False
        
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
    
    async def _start_main_tasks(self):
        """Inicia as tasks principais do worker"""
        logger.info("🔄 Iniciando tasks principais...")
        
        # Task 1: Market Data Processing
        self.tasks.append(
            asyncio.create_task(self._market_data_processor())
        )
        
        # Task 2: Strategy Execution
        self.tasks.append(
            asyncio.create_task(self._strategy_executor())
        )
        
        # Task 3: Health Monitor
        self.tasks.append(
            asyncio.create_task(self._health_monitor())
        )
        
        logger.info(f"✅ {len(self.tasks)} tasks iniciadas")
        
        # Aguardar todas as tasks
        try:
            await asyncio.gather(*self.tasks)
        except asyncio.CancelledError:
            logger.info("📋 Tasks canceladas durante shutdown")
        except Exception as e:
            logger.error(f"❌ Erro nas tasks: {e}")
    
    async def _market_data_processor(self):
        """Processa dados de mercado"""
        logger.info("📊 Market Data Processor iniciado")
        
        while self.running:
            try:
                # Simular processamento de dados de mercado
                logger.debug("📈 Processando dados de mercado...")
                
                # Aqui seria a lógica real de processamento
                # Por enquanto, apenas aguarda
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"❌ Erro no processamento de dados: {e}")
                await asyncio.sleep(5)
    
    async def _strategy_executor(self):
        """Executa estratégias de trading"""
        logger.info("🎯 Strategy Executor iniciado")
        
        while self.running:
            try:
                # Simular execução de estratégias
                logger.debug("🔄 Executando estratégias...")
                
                # Aqui seria a lógica real de execução
                # Por enquanto, apenas aguarda
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"❌ Erro na execução de estratégias: {e}")
                await asyncio.sleep(10)
    
    async def _health_monitor(self):
        """Monitor de saúde do worker"""
        logger.info("💚 Health Monitor iniciado")
        
        while self.running:
            try:
                # Log de status a cada 5 minutos
                logger.info(f"💚 Worker funcionando - {datetime.now().strftime('%H:%M:%S')}")
                await asyncio.sleep(300)  # 5 minutos
                
            except Exception as e:
                logger.error(f"❌ Erro no health monitor: {e}")
                await asyncio.sleep(30)
    
    async def stop(self):
        """Para o worker gracefully"""
        logger.info("🛑 Parando Trading Worker...")
        self.running = False
        
        # Cancelar todas as tasks
        for task in self.tasks:
            if not task.done():
                task.cancel()
        
        # Aguardar tasks terminarem
        if self.tasks:
            await asyncio.gather(*self.tasks, return_exceptions=True)
        
        logger.info("✅ Trading Worker parado")

async def main():
    """Função principal"""
    logger.info("=" * 50)
    logger.info("🤖 CRYPTO TRADING MVP - BOT WORKER")
    logger.info("🔄 Processamento Assíncrono de Trading")
    logger.info("=" * 50)
    
    worker = TradingWorker()
    
    try:
        await worker.start()
    except KeyboardInterrupt:
        logger.info("⌨️  Interrupção do usuário detectada")
    except Exception as e:
        logger.error(f"❌ Erro fatal no worker: {e}")
        sys.exit(1)
    finally:
        await worker.stop()

if __name__ == "__main__":
    # Verificar se está rodando em container
    if os.path.exists('/.dockerenv'):
        logger.info("🐳 Executando em container Docker")
    
    # Criar diretório de logs se não existir
    os.makedirs('/app/logs', exist_ok=True)
    
    # Executar worker
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"❌ Falha ao iniciar worker: {e}")
        sys.exit(1)

