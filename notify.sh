#!/bin/bash
################################################################################
# Script de Notificações - Enviar Notificações de Deployment
#
# Descrição: Envia notificações sobre deployment para diferentes canais
# Autor: Manus AI
# Data: 07/11/2025
# Uso: ./notify.sh <environment> <version> <status>
################################################################################

set -e

# Variáveis
ENVIRONMENT=${1:-staging}
VERSION=${2:-unknown}
STATUS=${3:-success}  # success, warning, error

# Cores para console
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# Emojis baseados no status
case $STATUS in
    success)
        EMOJI="✅"
        COLOR="$GREEN"
        STATUS_TEXT="SUCCESS"
        ;;
    warning)
        EMOJI="⚠️"
        COLOR="$YELLOW"
        STATUS_TEXT="WARNING"
        ;;
    error)
        EMOJI="❌"
        COLOR="$RED"
        STATUS_TEXT="ERROR"
        ;;
    *)
        EMOJI="ℹ️"
        COLOR="$CYAN"
        STATUS_TEXT="INFO"
        ;;
esac

# Informações do deployment
DEPLOY_USER=$(whoami)
DEPLOY_HOST=$(hostname)
DEPLOY_TIME=$(date '+%Y-%m-%d %H:%M:%S')

# Mensagem
MESSAGE="$EMOJI Deployment $STATUS_TEXT

Environment: $ENVIRONMENT
Version: $VERSION
Status: $STATUS_TEXT
User: $DEPLOY_USER
Host: $DEPLOY_HOST
Time: $DEPLOY_TIME"

echo -e "${CYAN}▶️  Enviando notificações...${NC}"
echo ""

# ============================================================================
# NOTIFICAÇÃO NO CONSOLE
# ============================================================================
echo -e "${COLOR}════════════════════════════════════════════════════════════${NC}"
echo -e "${COLOR}  $EMOJI NOTIFICAÇÃO DE DEPLOYMENT${NC}"
echo -e "${COLOR}════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${COLOR}Environment:${NC} $ENVIRONMENT"
echo -e "${COLOR}Version:${NC} $VERSION"
echo -e "${COLOR}Status:${NC} $STATUS_TEXT"
echo -e "${COLOR}User:${NC} $DEPLOY_USER"
echo -e "${COLOR}Host:${NC} $DEPLOY_HOST"
echo -e "${COLOR}Time:${NC} $DEPLOY_TIME"
echo ""
echo -e "${COLOR}════════════════════════════════════════════════════════════${NC}"
echo ""

# ============================================================================
# NOTIFICAÇÃO SLACK (se configurado)
# ============================================================================
if [ -n "$SLACK_WEBHOOK_URL" ]; then
    echo -e "${CYAN}   Enviando para Slack...${NC}"
    
    # Cor do Slack baseada no status
    case $STATUS in
        success) SLACK_COLOR="good" ;;
        warning) SLACK_COLOR="warning" ;;
        error) SLACK_COLOR="danger" ;;
        *) SLACK_COLOR="#36a64f" ;;
    esac
    
    # Payload JSON para Slack
    SLACK_PAYLOAD=$(cat <<EOF
{
    "attachments": [
        {
            "color": "$SLACK_COLOR",
            "title": "$EMOJI Deployment $STATUS_TEXT",
            "fields": [
                {
                    "title": "Environment",
                    "value": "$ENVIRONMENT",
                    "short": true
                },
                {
                    "title": "Version",
                    "value": "$VERSION",
                    "short": true
                },
                {
                    "title": "Status",
                    "value": "$STATUS_TEXT",
                    "short": true
                },
                {
                    "title": "User",
                    "value": "$DEPLOY_USER",
                    "short": true
                }
            ],
            "footer": "Crypto Trading MVP",
            "ts": $(date +%s)
        }
    ]
}
EOF
)
    
    if curl -X POST -H 'Content-type: application/json' \
        --data "$SLACK_PAYLOAD" \
        "$SLACK_WEBHOOK_URL" &> /dev/null; then
        echo -e "${GREEN}   ✅ Notificação enviada para Slack${NC}"
    else
        echo -e "${YELLOW}   ⚠️  Falha ao enviar para Slack${NC}"
    fi
else
    echo -e "${YELLOW}   ⚠️  Slack webhook não configurado (SLACK_WEBHOOK_URL)${NC}"
fi

echo ""

# ============================================================================
# NOTIFICAÇÃO DISCORD (se configurado)
# ============================================================================
if [ -n "$DISCORD_WEBHOOK_URL" ]; then
    echo -e "${CYAN}   Enviando para Discord...${NC}"
    
    # Cor do Discord baseada no status (decimal)
    case $STATUS in
        success) DISCORD_COLOR=3066993 ;;  # Verde
        warning) DISCORD_COLOR=16776960 ;; # Amarelo
        error) DISCORD_COLOR=15158332 ;;   # Vermelho
        *) DISCORD_COLOR=3447003 ;;        # Azul
    esac
    
    # Payload JSON para Discord
    DISCORD_PAYLOAD=$(cat <<EOF
{
    "embeds": [
        {
            "title": "$EMOJI Deployment $STATUS_TEXT",
            "color": $DISCORD_COLOR,
            "fields": [
                {
                    "name": "Environment",
                    "value": "$ENVIRONMENT",
                    "inline": true
                },
                {
                    "name": "Version",
                    "value": "$VERSION",
                    "inline": true
                },
                {
                    "name": "Status",
                    "value": "$STATUS_TEXT",
                    "inline": true
                },
                {
                    "name": "User",
                    "value": "$DEPLOY_USER",
                    "inline": true
                }
            ],
            "footer": {
                "text": "Crypto Trading MVP"
            },
            "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
        }
    ]
}
EOF
)
    
    if curl -X POST -H 'Content-type: application/json' \
        --data "$DISCORD_PAYLOAD" \
        "$DISCORD_WEBHOOK_URL" &> /dev/null; then
        echo -e "${GREEN}   ✅ Notificação enviada para Discord${NC}"
    else
        echo -e "${YELLOW}   ⚠️  Falha ao enviar para Discord${NC}"
    fi
else
    echo -e "${YELLOW}   ⚠️  Discord webhook não configurado (DISCORD_WEBHOOK_URL)${NC}"
fi

echo ""

# ============================================================================
# NOTIFICAÇÃO EMAIL (se configurado)
# ============================================================================
if [ -n "$NOTIFICATION_EMAIL" ] && command -v mail &> /dev/null; then
    echo -e "${CYAN}   Enviando email...${NC}"
    
    EMAIL_SUBJECT="[$STATUS_TEXT] Deployment - $ENVIRONMENT - $VERSION"
    
    echo "$MESSAGE" | mail -s "$EMAIL_SUBJECT" "$NOTIFICATION_EMAIL"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}   ✅ Email enviado para $NOTIFICATION_EMAIL${NC}"
    else
        echo -e "${YELLOW}   ⚠️  Falha ao enviar email${NC}"
    fi
else
    echo -e "${YELLOW}   ⚠️  Email não configurado (NOTIFICATION_EMAIL) ou comando 'mail' não disponível${NC}"
fi

echo ""

# ============================================================================
# LOG DE NOTIFICAÇÕES
# ============================================================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
LOG_FILE="$PROJECT_ROOT/logs/notifications.log"

# Criar diretório de logs se não existir
mkdir -p "$PROJECT_ROOT/logs"

# Adicionar ao log
echo "[$DEPLOY_TIME] $STATUS_TEXT - $ENVIRONMENT - $VERSION - $DEPLOY_USER@$DEPLOY_HOST" >> "$LOG_FILE"

echo -e "${GREEN}✅ Notificações processadas${NC}"
echo ""

# ============================================================================
# CONFIGURAÇÃO DE WEBHOOKS
# ============================================================================
echo -e "${CYAN}💡 Para configurar notificações, adicione ao arquivo .env:${NC}"
echo ""
echo -e "${YELLOW}   # Slack${NC}"
echo -e "${YELLOW}   SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL${NC}"
echo ""
echo -e "${YELLOW}   # Discord${NC}"
echo -e "${YELLOW}   DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR/WEBHOOK/URL${NC}"
echo ""
echo -e "${YELLOW}   # Email${NC}"
echo -e "${YELLOW}   NOTIFICATION_EMAIL=your-email@example.com${NC}"
echo ""
