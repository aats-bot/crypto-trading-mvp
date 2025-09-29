#!/bin/bash
# Crypto Trading MVP - API Entrypoint
# Script de inicialização otimizado para container

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para logging
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] API:${NC} $1"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] SUCCESS:${NC} $1"
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

# Banner de inicialização
echo "=================================="
echo "🚀 Crypto Trading MVP - API"
echo "📊 Bot de Trading Automatizado"
echo "=================================="
echo ""

# Verificar variáveis de ambiente obrigatórias
log "Verificando configuração..."

required_vars=(
    "DATABASE_URL"
    "JWT_SECRET_KEY"
)

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        error "Variável de ambiente obrigatória não definida: $var"
        exit 1
    fi
done

success "Configuração validada"

# Verificar conectividade com banco de dados
log "Verificando conectividade com banco de dados..."

# Extrair host e porta do DATABASE_URL
DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^:]*\):.*/\1/p')
DB_PORT=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')

if [ -n "$DB_HOST" ] && [ -n "$DB_PORT" ]; then
    # Aguardar banco de dados estar disponível
    max_attempts=30
    attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if timeout 5 bash -c "</dev/tcp/$DB_HOST/$DB_PORT" 2>/dev/null; then
            success "Banco de dados disponível"
            break
        else
            warning "Aguardando banco de dados... (tentativa $attempt/$max_attempts)"
            sleep 2
            attempt=$((attempt + 1))
        fi
    done
    
    if [ $attempt -gt $max_attempts ]; then
        error "Timeout aguardando banco de dados"
        exit 1
    fi
else
    warning "Não foi possível extrair host/porta do DATABASE_URL, pulando verificação"
fi

# Executar migrações de banco de dados se necessário
if [ "$RUN_MIGRATIONS" = "true" ]; then
    log "Executando migrações de banco de dados..."
    python -m alembic upgrade head || {
        error "Falha ao executar migrações"
        exit 1
    }
    success "Migrações executadas com sucesso"
fi

# Criar diretórios necessários
log "Criando estrutura de diretórios..."
mkdir -p /app/logs /app/data /app/tmp
success "Diretórios criados"

# Verificar permissões
log "Verificando permissões..."
if [ ! -w "/app/logs" ]; then
    error "Sem permissão de escrita em /app/logs"
    exit 1
fi

if [ ! -w "/app/data" ]; then
    error "Sem permissão de escrita em /app/data"
    exit 1
fi

success "Permissões verificadas"

# Configurar logging
export LOG_LEVEL=${LOG_LEVEL:-INFO}
export LOG_FILE=${LOG_FILE:-/app/logs/api.log}

log "Configuração de logging: Level=$LOG_LEVEL, File=$LOG_FILE"

# Verificar saúde da aplicação antes de iniciar
log "Verificando integridade da aplicação..."
python -c "
import sys
sys.path.append('/app')
try:
    from app.main import app
    print('✅ Aplicação carregada com sucesso')
except Exception as e:
    print(f'❌ Erro ao carregar aplicação: {e}')
    sys.exit(1)
" || exit 1

success "Aplicação verificada"

# Configurar workers baseado em CPU disponível
if [ -z "$WORKERS" ]; then
    WORKERS=$(python -c "import os; print(min(4, max(1, os.cpu_count() or 1)))")
    log "Workers configurados automaticamente: $WORKERS"
fi

# Configurar outras opções do Uvicorn
export UVICORN_HOST=${UVICORN_HOST:-0.0.0.0}
export UVICORN_PORT=${UVICORN_PORT:-8000}
export UVICORN_LOG_LEVEL=${UVICORN_LOG_LEVEL:-info}

log "Configuração Uvicorn:"
log "  Host: $UVICORN_HOST"
log "  Port: $UVICORN_PORT"
log "  Workers: $WORKERS"
log "  Log Level: $UVICORN_LOG_LEVEL"

# Função para cleanup graceful
cleanup() {
    log "Recebido sinal de shutdown, finalizando graciosamente..."
    # Aqui você pode adicionar lógica de cleanup se necessário
    exit 0
}

# Capturar sinais para shutdown graceful
trap cleanup SIGTERM SIGINT

# Log de inicialização final
success "Iniciando API do Crypto Trading MVP..."
echo ""

# Executar comando passado como argumento
exec "$@"

