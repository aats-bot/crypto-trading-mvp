#!/bin/bash
################################################################################
# Script de Deployment - Deploy Automatizado
#
# Descrição: Script principal para deployment em diferentes ambientes
# Autor: Manus AI
# Data: 07/11/2025
# Uso: ./deploy.sh <environment> [version]
################################################################################

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Variáveis
ENVIRONMENT=${1:-staging}
VERSION=${2:-latest}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo ""
echo "════════════════════════════════════════════════════════════"
echo "  🚀 DEPLOYMENT - CRYPTO TRADING MVP"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "  Environment: $ENVIRONMENT"
echo "  Version: $VERSION"
echo "  Time: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""
echo "════════════════════════════════════════════════════════════"
echo ""

# Validar ambiente
if [[ ! "$ENVIRONMENT" =~ ^(dev|staging|production)$ ]]; then
    echo -e "${RED}❌ Ambiente inválido: $ENVIRONMENT${NC}"
    echo -e "${YELLOW}   Ambientes válidos: dev, staging, production${NC}"
    exit 1
fi

# Confirmar deployment em produção
if [ "$ENVIRONMENT" == "production" ]; then
    echo -e "${YELLOW}⚠️  ATENÇÃO: Você está fazendo deployment para PRODUÇÃO!${NC}"
    echo -e "${YELLOW}   Version: $VERSION${NC}"
    echo ""
    read -p "Tem certeza que deseja continuar? (yes/no): " CONFIRM
    
    if [ "$CONFIRM" != "yes" ]; then
        echo -e "${RED}❌ Deployment cancelado${NC}"
        exit 0
    fi
fi

# Carregar configurações do ambiente
ENV_FILE="$PROJECT_ROOT/config/environments/$ENVIRONMENT.env"

if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}❌ Arquivo de configuração não encontrado: $ENV_FILE${NC}"
    exit 1
fi

echo -e "${CYAN}▶️  Carregando configurações do ambiente...${NC}"
source "$ENV_FILE"
echo -e "${GREEN}✅ Configurações carregadas${NC}"
echo ""

# Verificar Docker
echo -e "${CYAN}▶️  Verificando Docker...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker não encontrado!${NC}"
    exit 1
fi

if ! docker info &> /dev/null; then
    echo -e "${RED}❌ Docker não está rodando!${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker disponível${NC}"
echo ""

# Pull das imagens
echo "════════════════════════════════════════════════════════════"
echo "  📦 PULL DE IMAGENS"
echo "════════════════════════════════════════════════════════════"
echo ""

IMAGES=(
    "crypto-trading-api:$VERSION"
    "crypto-trading-dashboard:$VERSION"
    "crypto-trading-worker:$VERSION"
)

for image in "${IMAGES[@]}"; do
    echo -e "${CYAN}▶️  Pulling $image...${NC}"
    
    # Se for latest ou imagem local, usar imagem local
    if [ "$VERSION" == "latest" ] || ! docker pull "$image" 2>/dev/null; then
        echo -e "${YELLOW}   Usando imagem local${NC}"
    else
        echo -e "${GREEN}✅ Pull concluído${NC}"
    fi
done

echo ""

# Backup da versão atual (se existir)
echo "════════════════════════════════════════════════════════════"
echo "  💾 BACKUP DA VERSÃO ATUAL"
echo "════════════════════════════════════════════════════════════"
echo ""

BACKUP_FILE="$PROJECT_ROOT/.deploy_backup_$ENVIRONMENT"

if docker-compose ps -q &> /dev/null; then
    echo -e "${CYAN}▶️  Salvando informações da versão atual...${NC}"
    
    # Salvar versão atual
    echo "PREVIOUS_VERSION=$(docker-compose images -q | head -1)" > "$BACKUP_FILE"
    echo "BACKUP_DATE=$(date '+%Y-%m-%d %H:%M:%S')" >> "$BACKUP_FILE"
    
    echo -e "${GREEN}✅ Backup criado${NC}"
else
    echo -e "${YELLOW}⚠️  Nenhuma versão anterior encontrada${NC}"
fi

echo ""

# Parar serviços atuais
echo "════════════════════════════════════════════════════════════"
echo "  🛑 PARANDO SERVIÇOS ATUAIS"
echo "════════════════════════════════════════════════════════════"
echo ""

if docker-compose ps -q &> /dev/null; then
    echo -e "${CYAN}▶️  Parando containers...${NC}"
    docker-compose down
    echo -e "${GREEN}✅ Serviços parados${NC}"
else
    echo -e "${YELLOW}⚠️  Nenhum serviço rodando${NC}"
fi

echo ""

# Deploy dos novos serviços
echo "════════════════════════════════════════════════════════════"
echo "  🚀 INICIANDO NOVOS SERVIÇOS"
echo "════════════════════════════════════════════════════════════"
echo ""

echo -e "${CYAN}▶️  Iniciando containers...${NC}"

# Definir variáveis de ambiente para docker-compose
export ENVIRONMENT=$ENVIRONMENT
export VERSION=$VERSION

# Iniciar serviços
if docker-compose up -d; then
    echo -e "${GREEN}✅ Serviços iniciados${NC}"
else
    echo -e "${RED}❌ Falha ao iniciar serviços!${NC}"
    echo -e "${YELLOW}   Executando rollback...${NC}"
    
    # Tentar rollback
    "$SCRIPT_DIR/rollback.sh" "$ENVIRONMENT"
    exit 1
fi

echo ""

# Aguardar serviços ficarem prontos
echo "════════════════════════════════════════════════════════════"
echo "  ⏳ AGUARDANDO SERVIÇOS"
echo "════════════════════════════════════════════════════════════"
echo ""

echo -e "${CYAN}▶️  Aguardando serviços ficarem prontos...${NC}"
sleep 10

echo ""

# Health check
echo "════════════════════════════════════════════════════════════"
echo "  🏥 HEALTH CHECK"
echo "════════════════════════════════════════════════════════════"
echo ""

if "$SCRIPT_DIR/health-check.sh" "$ENVIRONMENT"; then
    echo -e "${GREEN}✅ Health check passou!${NC}"
else
    echo -e "${RED}❌ Health check falhou!${NC}"
    echo -e "${YELLOW}   Executando rollback...${NC}"
    
    # Rollback
    "$SCRIPT_DIR/rollback.sh" "$ENVIRONMENT"
    exit 1
fi

echo ""

# Notificação
echo "════════════════════════════════════════════════════════════"
echo "  📢 NOTIFICAÇÃO"
echo "════════════════════════════════════════════════════════════"
echo ""

"$SCRIPT_DIR/notify.sh" "$ENVIRONMENT" "$VERSION" "success"

echo ""

# Resumo
echo "════════════════════════════════════════════════════════════"
echo "  ✅ DEPLOYMENT CONCLUÍDO COM SUCESSO!"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "  Environment: $ENVIRONMENT"
echo "  Version: $VERSION"
echo "  Time: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""
echo "  🌐 Serviços disponíveis:"
echo "     - API: http://localhost:8000"
echo "     - Dashboard: http://localhost:3000"
echo ""
echo "════════════════════════════════════════════════════════════"
echo ""

# Salvar informações do deployment
DEPLOY_INFO="$PROJECT_ROOT/.deploy_info_$ENVIRONMENT"
cat > "$DEPLOY_INFO" <<EOF
ENVIRONMENT=$ENVIRONMENT
VERSION=$VERSION
DEPLOY_DATE=$(date '+%Y-%m-%d %H:%M:%S')
DEPLOY_USER=$(whoami)
DEPLOY_HOST=$(hostname)
EOF

echo -e "${GREEN}💡 Para verificar logs: docker-compose logs -f${NC}"
echo -e "${GREEN}💡 Para rollback: ./scripts/deploy/rollback.sh $ENVIRONMENT${NC}"
echo ""
