#!/bin/bash
# Crypto Trading MVP - Dashboard Entrypoint
set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] DASHBOARD:${NC} $1"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] SUCCESS:${NC} $1"
}

# Banner
echo "=================================="
echo "🎨 Crypto Trading MVP - Dashboard"
echo "📊 Interface Streamlit"
echo "=================================="
echo ""

# Verificar variáveis obrigatórias
log "Verificando configuração..."
required_vars=("API_URL")

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        error "Variável obrigatória não definida: $var"
        exit 1
    fi
done

success "Configuração validada"

# Aguardar API estar disponível
log "Aguardando API estar disponível..."
API_HOST=$(echo $API_URL | sed -n 's|http://\([^:]*\):.*|\1|p')
API_PORT=$(echo $API_URL | sed -n 's|.*:\([0-9]*\).*|\1|p')

if [ -n "$API_HOST" ] && [ -n "$API_PORT" ]; then
    max_attempts=30
    attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if timeout 5 bash -c "</dev/tcp/$API_HOST/$API_PORT" 2>/dev/null; then
            success "API disponível"
            break
        else
            log "Aguardando API... (tentativa $attempt/$max_attempts)"
            sleep 2
            attempt=$((attempt + 1))
        fi
    done
fi

# Criar diretórios
log "Criando estrutura de diretórios..."
mkdir -p /app/logs /app/data /app/static
success "Diretórios criados"

# Configurar Streamlit
export STREAMLIT_SERVER_PORT=${STREAMLIT_SERVER_PORT:-8501}
export STREAMLIT_SERVER_ADDRESS=${STREAMLIT_SERVER_ADDRESS:-0.0.0.0}

log "Configuração Streamlit:"
log "  Port: $STREAMLIT_SERVER_PORT"
log "  Address: $STREAMLIT_SERVER_ADDRESS"

success "Iniciando Dashboard Streamlit..."
exec "$@"

