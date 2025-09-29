#!/bin/bash
# Script de Diagnóstico Completo do Sistema Enterprise

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
WHITE='\033[1;37m'
NC='\033[0m'

log() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')] INFO:${NC} $1"
}

success() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')] SUCCESS:${NC} $1"
}

error() {
    echo -e "${RED}[$(date +'%H:%M:%S')] ERROR:${NC} $1"
}

warning() {
    echo -e "${YELLOW}[$(date +'%H:%M:%S')] WARNING:${NC} $1"
}

diagnostic() {
    echo -e "${CYAN}[$(date +'%H:%M:%S')] DIAGNOSTIC:${NC} $1"
}

section() {
    echo ""
    echo -e "${WHITE}=================================================================="
    echo -e "📊 $1"
    echo -e "==================================================================${NC}"
    echo ""
}

echo "=================================================================="
echo "🔍 DIAGNÓSTICO COMPLETO DO SISTEMA ENTERPRISE"
echo "🎯 Mapeando TODOS os problemas para resolução definitiva"
echo "=================================================================="
echo ""

diagnostic "Iniciando diagnóstico completo em $(date)"

# ================================================================
# 1. STATUS DOS CONTAINERS
# ================================================================
section "1. STATUS DOS CONTAINERS"

log "Verificando status de todos os containers..."
if docker-compose -f docker-compose.production.yml ps; then
    success "✅ Docker Compose funcionando"
else
    error "❌ Problema com Docker Compose"
fi

echo ""
log "Status detalhado dos containers:"
docker ps -a --filter "name=crypto-trading" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" || true

echo ""
log "Verificando health checks:"
for container in crypto-trading-api crypto-trading-dashboard crypto-trading-postgres crypto-trading-redis crypto-trading-grafana crypto-trading-nginx crypto-trading-worker; do
    if docker ps --filter "name=$container" --format "{{.Names}}: {{.Status}}" 2>/dev/null | grep -q "$container"; then
        STATUS=$(docker ps --filter "name=$container" --format "{{.Status}}" 2>/dev/null || echo "Not found")
        if [[ "$STATUS" == *"healthy"* ]]; then
            success "✅ $container: Healthy"
        elif [[ "$STATUS" == *"unhealthy"* ]]; then
            error "❌ $container: Unhealthy"
        elif [[ "$STATUS" == *"starting"* ]]; then
            warning "⏳ $container: Starting"
        else
            warning "⚠️ $container: $STATUS"
        fi
    else
        error "❌ $container: Not found"
    fi
done

# ================================================================
# 2. LOGS DOS CONTAINERS
# ================================================================
section "2. LOGS DOS CONTAINERS (ÚLTIMAS 10 LINHAS)"

for container in api dashboard worker postgres redis grafana nginx; do
    log "Logs do $container:"
    if docker-compose -f docker-compose.production.yml logs --tail=10 $container 2>/dev/null; then
        echo ""
    else
        error "❌ Não foi possível obter logs do $container"
        echo ""
    fi
done

# ================================================================
# 3. CONECTIVIDADE DE REDE
# ================================================================
section "3. CONECTIVIDADE DE REDE"

log "Verificando rede Docker..."
if docker network ls | grep -q "crypto-trading-network"; then
    success "✅ Rede crypto-trading-network existe"
else
    error "❌ Rede crypto-trading-network não encontrada"
fi

echo ""
log "Testando conectividade entre containers..."

# Teste de conectividade interna
if docker-compose -f docker-compose.production.yml exec -T api ping -c 1 postgres >/dev/null 2>&1; then
    success "✅ API → PostgreSQL: Conectividade OK"
else
    error "❌ API → PostgreSQL: Falha na conectividade"
fi

if docker-compose -f docker-compose.production.yml exec -T api ping -c 1 redis >/dev/null 2>&1; then
    success "✅ API → Redis: Conectividade OK"
else
    error "❌ API → Redis: Falha na conectividade"
fi

# ================================================================
# 4. TESTES DE ENDPOINTS
# ================================================================
section "4. TESTES DE ENDPOINTS"

log "Testando endpoints externos..."

# API
if curl -f -s --max-time 5 http://localhost:8000/health >/dev/null 2>&1; then
    success "✅ API Health: http://localhost:8000/health"
    API_RESPONSE=$(curl -s http://localhost:8000/ 2>/dev/null || echo "ERRO")
    echo "   Resposta: $API_RESPONSE"
else
    error "❌ API Health: http://localhost:8000/health"
fi

# Dashboard
if curl -f -s --max-time 5 http://localhost:8501 >/dev/null 2>&1; then
    success "✅ Dashboard: http://localhost:8501"
else
    error "❌ Dashboard: http://localhost:8501"
fi

# Grafana
if curl -f -s --max-time 5 http://localhost:3000/api/health >/dev/null 2>&1; then
    success "✅ Grafana: http://localhost:3000"
else
    error "❌ Grafana: http://localhost:3000"
fi

# Nginx
if curl -f -s --max-time 5 http://localhost:80 >/dev/null 2>&1; then
    success "✅ Nginx: http://localhost:80"
else
    error "❌ Nginx: http://localhost:80"
fi

# ================================================================
# 5. ESTRUTURA DE ARQUIVOS
# ================================================================
section "5. ESTRUTURA DE ARQUIVOS"

log "Verificando estrutura de arquivos no container da API..."

if docker-compose -f docker-compose.production.yml exec -T api ls -la /app/src/api/main.py >/dev/null 2>&1; then
    success "✅ /app/src/api/main.py existe"
else
    error "❌ /app/src/api/main.py não encontrado"
fi

if docker-compose -f docker-compose.production.yml exec -T api ls -la /app/config/settings.py >/dev/null 2>&1; then
    success "✅ /app/config/settings.py existe"
    
    # Verificar conteúdo do settings.py
    log "Verificando conteúdo do config/settings.py..."
    SETTINGS_CONTENT=$(docker-compose -f docker-compose.production.yml exec -T api head -5 /app/config/settings.py 2>/dev/null || echo "ERRO")
    if [[ "$SETTINGS_CONTENT" == *"extra = \"allow\""* ]] || [[ "$SETTINGS_CONTENT" == *"Enterprise"* ]]; then
        success "✅ Config/settings.py parece ser a versão enterprise"
    else
        warning "⚠️ Config/settings.py pode ser versão antiga"
        echo "   Primeiras linhas: $SETTINGS_CONTENT"
    fi
else
    error "❌ /app/config/settings.py não encontrado"
fi

# ================================================================
# 6. TESTES DE IMPORTS PYTHON
# ================================================================
section "6. TESTES DE IMPORTS PYTHON"

log "Testando imports Python no container da API..."

# Teste de import básico
IMPORT_TEST=$(docker-compose -f docker-compose.production.yml exec -T api python -c "import sys; print('Python OK')" 2>&1 || echo "ERRO")
if [[ "$IMPORT_TEST" == *"Python OK"* ]]; then
    success "✅ Python funcionando"
else
    error "❌ Python com problema: $IMPORT_TEST"
fi

# Teste de import FastAPI
FASTAPI_TEST=$(docker-compose -f docker-compose.production.yml exec -T api python -c "import fastapi; print('FastAPI OK')" 2>&1 || echo "ERRO")
if [[ "$FASTAPI_TEST" == *"FastAPI OK"* ]]; then
    success "✅ FastAPI importando"
else
    error "❌ FastAPI com problema: $FASTAPI_TEST"
fi

# Teste de import AsyncPG
ASYNCPG_TEST=$(docker-compose -f docker-compose.production.yml exec -T api python -c "import asyncpg; print('AsyncPG OK')" 2>&1 || echo "ERRO")
if [[ "$ASYNCPG_TEST" == *"AsyncPG OK"* ]]; then
    success "✅ AsyncPG instalado"
else
    error "❌ AsyncPG com problema: $ASYNCPG_TEST"
fi

# Teste de import das configurações
CONFIG_TEST=$(docker-compose -f docker-compose.production.yml exec -T api python -c "from config.settings import settings; print('Config OK')" 2>&1 || echo "ERRO")
if [[ "$CONFIG_TEST" == *"Config OK"* ]]; then
    success "✅ Config/settings importando"
else
    error "❌ Config/settings com problema:"
    echo "   Erro: $CONFIG_TEST"
fi

# Teste de import da API principal
API_IMPORT_TEST=$(docker-compose -f docker-compose.production.yml exec -T api python -c "import src.api.main; print('API Main OK')" 2>&1 || echo "ERRO")
if [[ "$API_IMPORT_TEST" == *"API Main OK"* ]]; then
    success "✅ src.api.main importando"
else
    error "❌ src.api.main com problema:"
    echo "   Erro: $API_IMPORT_TEST"
fi

# ================================================================
# 7. VARIÁVEIS DE AMBIENTE
# ================================================================
section "7. VARIÁVEIS DE AMBIENTE"

log "Verificando variáveis de ambiente no container da API..."

ENV_VARS=$(docker-compose -f docker-compose.production.yml exec -T api env | grep -E "(POSTGRES|REDIS|JWT|API)" | head -10 2>/dev/null || echo "ERRO")
if [[ "$ENV_VARS" != "ERRO" ]]; then
    success "✅ Variáveis de ambiente carregadas:"
    echo "$ENV_VARS"
else
    error "❌ Problema ao acessar variáveis de ambiente"
fi

# ================================================================
# 8. BANCO DE DADOS
# ================================================================
section "8. BANCO DE DADOS"

log "Testando conectividade com PostgreSQL..."

# Teste de conexão com PostgreSQL
PG_TEST=$(docker-compose -f docker-compose.production.yml exec -T postgres pg_isready -U trading_user -d crypto_trading 2>&1 || echo "ERRO")
if [[ "$PG_TEST" == *"accepting connections"* ]]; then
    success "✅ PostgreSQL aceitando conexões"
else
    error "❌ PostgreSQL com problema: $PG_TEST"
fi

# Teste de conexão com Redis
REDIS_TEST=$(docker-compose -f docker-compose.production.yml exec -T redis redis-cli ping 2>&1 || echo "ERRO")
if [[ "$REDIS_TEST" == *"PONG"* ]]; then
    success "✅ Redis respondendo"
else
    error "❌ Redis com problema: $REDIS_TEST"
fi

# ================================================================
# 9. RECURSOS DO SISTEMA
# ================================================================
section "9. RECURSOS DO SISTEMA"

log "Verificando uso de recursos..."

# Uso de CPU e memória dos containers
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" $(docker ps --filter "name=crypto-trading" -q) 2>/dev/null || echo "Erro ao obter estatísticas"

# ================================================================
# 10. RESUMO E RECOMENDAÇÕES
# ================================================================
section "10. RESUMO E RECOMENDAÇÕES"

log "Analisando resultados do diagnóstico..."

echo ""
diagnostic "📊 RESUMO DOS PROBLEMAS ENCONTRADOS:"

# Contar problemas
PROBLEMS=0

# Verificar se API está funcionando
if ! curl -f -s --max-time 5 http://localhost:8000/health >/dev/null 2>&1; then
    error "🚨 PROBLEMA CRÍTICO: API não está respondendo"
    PROBLEMS=$((PROBLEMS + 1))
fi

# Verificar se config está funcionando
CONFIG_CHECK=$(docker-compose -f docker-compose.production.yml exec -T api python -c "from config.settings import settings; print('OK')" 2>&1 || echo "ERRO")
if [[ "$CONFIG_CHECK" == *"ERRO"* ]]; then
    error "🚨 PROBLEMA CRÍTICO: Config/settings.py com erro"
    PROBLEMS=$((PROBLEMS + 1))
fi

# Verificar se Dashboard está funcionando
if ! curl -f -s --max-time 5 http://localhost:8501 >/dev/null 2>&1; then
    warning "⚠️ PROBLEMA: Dashboard não está respondendo"
    PROBLEMS=$((PROBLEMS + 1))
fi

echo ""
if [ $PROBLEMS -eq 0 ]; then
    success "🎉 SISTEMA FUNCIONANDO PERFEITAMENTE!"
    success "🏆 Nenhum problema crítico encontrado!"
else
    diagnostic "📋 TOTAL DE PROBLEMAS ENCONTRADOS: $PROBLEMS"
    echo ""
    diagnostic "🔧 RECOMENDAÇÕES:"
    
    if [[ "$CONFIG_CHECK" == *"ERRO"* ]]; then
        echo "   1. 🎯 PRIORIDADE ALTA: Corrigir config/settings.py"
        echo "      Comando: ./aplicar_config_definitiva.sh"
    fi
    
    if ! curl -f -s --max-time 5 http://localhost:8000/health >/dev/null 2>&1; then
        echo "   2. 🎯 PRIORIDADE ALTA: Reiniciar API"
        echo "      Comando: docker-compose -f docker-compose.production.yml restart api"
    fi
    
    if ! curl -f -s --max-time 5 http://localhost:8501 >/dev/null 2>&1; then
        echo "   3. 🎯 PRIORIDADE MÉDIA: Verificar Dashboard"
        echo "      Comando: docker-compose -f docker-compose.production.yml logs dashboard"
    fi
fi

echo ""
echo "=================================================================="
echo "🔍 DIAGNÓSTICO COMPLETO FINALIZADO"
echo "📊 Relatório gerado em $(date)"
echo "=================================================================="

