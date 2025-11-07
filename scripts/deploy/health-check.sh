#!/bin/bash
################################################################################
# Script de Health Check - Verificação de Saúde dos Serviços
#
# Descrição: Verifica se todos os serviços estão funcionando corretamente
# Autor: Manus AI
# Data: 07/11/2025
# Uso: ./health-check.sh <environment>
################################################################################

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# Variáveis
ENVIRONMENT=${1:-staging}
MAX_RETRIES=30
RETRY_INTERVAL=2

echo -e "${CYAN}▶️  Executando health check para $ENVIRONMENT...${NC}"
echo ""

# Função para verificar endpoint
check_endpoint() {
    local service=$1
    local url=$2
    local expected_status=${3:-200}
    
    echo -e "${CYAN}   Verificando $service...${NC}"
    
    for i in $(seq 1 $MAX_RETRIES); do
        if curl -f -s -o /dev/null -w "%{http_code}" "$url" | grep -q "$expected_status"; then
            echo -e "${GREEN}   ✅ $service está saudável${NC}"
            return 0
        fi
        
        if [ $i -lt $MAX_RETRIES ]; then
            echo -e "${YELLOW}   ⏳ Tentativa $i/$MAX_RETRIES - Aguardando...${NC}"
            sleep $RETRY_INTERVAL
        fi
    done
    
    echo -e "${RED}   ❌ $service não respondeu após $MAX_RETRIES tentativas${NC}"
    return 1
}

# Função para verificar container
check_container() {
    local container=$1
    
    echo -e "${CYAN}   Verificando container $container...${NC}"
    
    if docker ps --filter "name=$container" --filter "status=running" | grep -q "$container"; then
        echo -e "${GREEN}   ✅ Container $container está rodando${NC}"
        return 0
    else
        echo -e "${RED}   ❌ Container $container não está rodando${NC}"
        return 1
    fi
}

# Verificar containers
echo "════════════════════════════════════════════════════════════"
echo "  🐳 VERIFICANDO CONTAINERS"
echo "════════════════════════════════════════════════════════════"
echo ""

CONTAINERS=(
    "crypto-trading-api"
    "crypto-trading-dashboard"
    "crypto-trading-worker"
    "postgres"
    "redis"
)

CONTAINER_CHECK_FAILED=false

for container in "${CONTAINERS[@]}"; do
    if ! check_container "$container"; then
        CONTAINER_CHECK_FAILED=true
    fi
done

echo ""

# Verificar endpoints HTTP
echo "════════════════════════════════════════════════════════════"
echo "  🌐 VERIFICANDO ENDPOINTS"
echo "════════════════════════════════════════════════════════════"
echo ""

ENDPOINT_CHECK_FAILED=false

# API Health endpoint
if ! check_endpoint "API Health" "http://localhost:8000/health" "200"; then
    ENDPOINT_CHECK_FAILED=true
fi

# API Docs (opcional)
if curl -f -s -o /dev/null "http://localhost:8000/docs"; then
    echo -e "${GREEN}   ✅ API Docs disponível${NC}"
else
    echo -e "${YELLOW}   ⚠️  API Docs não disponível (opcional)${NC}"
fi

# Dashboard (opcional - pode não ter health endpoint)
if curl -f -s -o /dev/null "http://localhost:3000"; then
    echo -e "${GREEN}   ✅ Dashboard acessível${NC}"
else
    echo -e "${YELLOW}   ⚠️  Dashboard não acessível${NC}"
fi

echo ""

# Verificar logs de erros
echo "════════════════════════════════════════════════════════════"
echo "  📋 VERIFICANDO LOGS"
echo "════════════════════════════════════════════════════════════"
echo ""

echo -e "${CYAN}   Verificando logs recentes...${NC}"

# Verificar logs de erro nos últimos 30 segundos
ERROR_COUNT=$(docker-compose logs --tail=100 --since=30s 2>&1 | grep -i "error\|exception\|fatal" | wc -l)

if [ "$ERROR_COUNT" -gt 0 ]; then
    echo -e "${YELLOW}   ⚠️  $ERROR_COUNT erros encontrados nos logs recentes${NC}"
    echo -e "${YELLOW}   💡 Execute 'docker-compose logs' para mais detalhes${NC}"
else
    echo -e "${GREEN}   ✅ Nenhum erro crítico nos logs recentes${NC}"
fi

echo ""

# Verificar recursos do sistema
echo "════════════════════════════════════════════════════════════"
echo "  💻 VERIFICANDO RECURSOS DO SISTEMA"
echo "════════════════════════════════════════════════════════════"
echo ""

# CPU e Memória dos containers
echo -e "${CYAN}   Uso de recursos:${NC}"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" | head -6

echo ""

# Verificar espaço em disco
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 90 ]; then
    echo -e "${RED}   ⚠️  Espaço em disco crítico: ${DISK_USAGE}%${NC}"
else
    echo -e "${GREEN}   ✅ Espaço em disco: ${DISK_USAGE}%${NC}"
fi

echo ""

# Resumo final
echo "════════════════════════════════════════════════════════════"
echo "  📊 RESUMO DO HEALTH CHECK"
echo "════════════════════════════════════════════════════════════"
echo ""

if [ "$CONTAINER_CHECK_FAILED" = true ] || [ "$ENDPOINT_CHECK_FAILED" = true ]; then
    echo -e "${RED}❌ HEALTH CHECK FALHOU${NC}"
    echo ""
    echo -e "${YELLOW}Problemas encontrados:${NC}"
    
    if [ "$CONTAINER_CHECK_FAILED" = true ]; then
        echo -e "${RED}  - Alguns containers não estão rodando${NC}"
    fi
    
    if [ "$ENDPOINT_CHECK_FAILED" = true ]; then
        echo -e "${RED}  - Alguns endpoints não estão respondendo${NC}"
    fi
    
    echo ""
    echo -e "${YELLOW}💡 Comandos úteis para debug:${NC}"
    echo -e "${CYAN}   docker-compose ps${NC}"
    echo -e "${CYAN}   docker-compose logs -f${NC}"
    echo -e "${CYAN}   docker-compose logs <service>${NC}"
    echo ""
    
    exit 1
else
    echo -e "${GREEN}✅ HEALTH CHECK PASSOU${NC}"
    echo ""
    echo -e "${GREEN}Todos os serviços estão funcionando corretamente!${NC}"
    echo ""
    echo -e "${CYAN}Serviços disponíveis:${NC}"
    echo -e "${GREEN}  🌐 API: http://localhost:8000${NC}"
    echo -e "${GREEN}  🌐 API Docs: http://localhost:8000/docs${NC}"
    echo -e "${GREEN}  🌐 Dashboard: http://localhost:3000${NC}"
    echo ""
    
    exit 0
fi
