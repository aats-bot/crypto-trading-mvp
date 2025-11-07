#!/bin/bash
################################################################################
# Script de Rollback - Reverter Deployment
#
# Descrição: Reverte para a versão anterior em caso de falha
# Autor: Manus AI
# Data: 07/11/2025
# Uso: ./rollback.sh <environment>
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
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo ""
echo "════════════════════════════════════════════════════════════"
echo "  ⏮️  ROLLBACK - CRYPTO TRADING MVP"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "  Environment: $ENVIRONMENT"
echo "  Time: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""
echo "════════════════════════════════════════════════════════════"
echo ""

# Validar ambiente
if [[ ! "$ENVIRONMENT" =~ ^(dev|staging|production)$ ]]; then
    echo -e "${RED}❌ Ambiente inválido: $ENVIRONMENT${NC}"
    exit 1
fi

# Confirmar rollback em produção
if [ "$ENVIRONMENT" == "production" ]; then
    echo -e "${YELLOW}⚠️  ATENÇÃO: Você está fazendo rollback em PRODUÇÃO!${NC}"
    echo ""
    read -p "Tem certeza que deseja continuar? (yes/no): " CONFIRM
    
    if [ "$CONFIRM" != "yes" ]; then
        echo -e "${RED}❌ Rollback cancelado${NC}"
        exit 0
    fi
fi

# Verificar se existe backup
BACKUP_FILE="$PROJECT_ROOT/.deploy_backup_$ENVIRONMENT"

if [ ! -f "$BACKUP_FILE" ]; then
    echo -e "${RED}❌ Nenhum backup encontrado para $ENVIRONMENT${NC}"
    echo -e "${YELLOW}   Não é possível fazer rollback${NC}"
    exit 1
fi

echo -e "${CYAN}▶️  Carregando informações do backup...${NC}"
source "$BACKUP_FILE"
echo -e "${GREEN}✅ Backup encontrado${NC}"
echo -e "${CYAN}   Data do backup: $BACKUP_DATE${NC}"
echo ""

# Parar serviços atuais
echo "════════════════════════════════════════════════════════════"
echo "  🛑 PARANDO SERVIÇOS ATUAIS"
echo "════════════════════════════════════════════════════════════"
echo ""

echo -e "${CYAN}▶️  Parando containers...${NC}"
docker-compose down
echo -e "${GREEN}✅ Serviços parados${NC}"
echo ""

# Restaurar versão anterior
echo "════════════════════════════════════════════════════════════"
echo "  ⏮️  RESTAURANDO VERSÃO ANTERIOR"
echo "════════════════════════════════════════════════════════════"
echo ""

echo -e "${CYAN}▶️  Restaurando containers...${NC}"

# Carregar configurações do ambiente
ENV_FILE="$PROJECT_ROOT/config/environments/$ENVIRONMENT.env"
source "$ENV_FILE"

# Definir variáveis de ambiente
export ENVIRONMENT=$ENVIRONMENT
export VERSION=previous

# Iniciar versão anterior
if docker-compose up -d; then
    echo -e "${GREEN}✅ Versão anterior restaurada${NC}"
else
    echo -e "${RED}❌ Falha ao restaurar versão anterior!${NC}"
    exit 1
fi

echo ""

# Aguardar serviços
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
    echo -e "${RED}❌ Health check falhou após rollback!${NC}"
    echo -e "${YELLOW}   Intervenção manual necessária!${NC}"
    exit 1
fi

echo ""

# Notificação
"$SCRIPT_DIR/notify.sh" "$ENVIRONMENT" "rollback" "warning"

echo ""

# Resumo
echo "════════════════════════════════════════════════════════════"
echo "  ✅ ROLLBACK CONCLUÍDO COM SUCESSO!"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "  Environment: $ENVIRONMENT"
echo "  Backup Date: $BACKUP_DATE"
echo "  Rollback Time: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""
echo "════════════════════════════════════════════════════════════"
echo ""

# Salvar informações do rollback
ROLLBACK_INFO="$PROJECT_ROOT/.rollback_info_$ENVIRONMENT"
cat > "$ROLLBACK_INFO" <<EOF
ENVIRONMENT=$ENVIRONMENT
ROLLBACK_DATE=$(date '+%Y-%m-%d %H:%M:%S')
ROLLBACK_USER=$(whoami)
ROLLBACK_HOST=$(hostname)
BACKUP_DATE=$BACKUP_DATE
EOF

echo -e "${GREEN}💡 Para verificar logs: docker-compose logs -f${NC}"
echo -e "${YELLOW}💡 Investigue a causa da falha antes de tentar novo deployment${NC}"
echo ""
