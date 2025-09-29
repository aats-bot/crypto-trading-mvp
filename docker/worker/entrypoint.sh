#!/bin/bash
# Crypto Trading MVP - Worker Entrypoint
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] WORKER:${NC} $1"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] SUCCESS:${NC} $1"
}

echo "=================================="
echo "⚙️  Crypto Trading MVP - Worker"
echo "🔄 Processamento Assíncrono"
echo "=================================="
echo ""

log "Verificando configuração..."

required_vars=("DATABASE_URL" "REDIS_URL")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        error "Variável obrigatória não definida: $var"
        exit 1
    fi
done

success "Configuração validada"

# Aguardar dependências
log "Aguardando dependências..."

# Redis
REDIS_HOST=$(echo $REDIS_URL | sed -n 's|redis://\([^:]*\):.*|\1|p')
REDIS_PORT=$(echo $REDIS_URL | sed -n 's|.*:\([0-9]*\)/.*|\1|p')

if [ -n "$REDIS_HOST" ] && [ -n "$REDIS_PORT" ]; then
    max_attempts=30
    attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if timeout 3 bash -c "</dev/tcp/$REDIS_HOST/$REDIS_PORT" 2>/dev/null; then
            success "Redis disponível"
            break
        else
            log "Aguardando Redis... (tentativa $attempt/$max_attempts)"
            sleep 2
            attempt=$((attempt + 1))
        fi
    done
fi

mkdir -p /app/logs /app/data /app/tmp
success "Diretórios criados"

export WORKER_CONCURRENCY=${WORKER_CONCURRENCY:-4}
export WORKER_LOG_LEVEL=${WORKER_LOG_LEVEL:-INFO}

log "Configuração Worker:"
log "  Concurrency: $WORKER_CONCURRENCY"
log "  Log Level: $WORKER_LOG_LEVEL"

success "Iniciando Worker..."
exec "$@"

