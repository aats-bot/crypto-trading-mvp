#!/bin/bash
################################################################################
# Script de Security Scanning - CI Pipeline
#
# Descrição: Executa verificações de segurança no código e dependências
# Autor: Manus AI
# Data: 07/11/2025
################################################################################

set -e

echo "🛡️  Executando security scanning..."
echo ""

# Verificar se está no ambiente virtual
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Aviso: Ambiente virtual não detectado"
    echo "   Recomenda-se ativar o ambiente virtual antes de executar"
fi

SCAN_FAILED=false

echo "═══════════════════════════════════════════════════════════"
echo "  1. Safety - Verificação de Dependências Python"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Instalar safety se necessário
pip install -q safety 2>/dev/null || true

echo "▶️  Verificando vulnerabilidades em dependências Python..."
if safety check --json > safety-report.json 2>/dev/null; then
    echo "✅ Nenhuma vulnerabilidade conhecida encontrada"
else
    echo "⚠️  Vulnerabilidades encontradas!"
    echo "   Relatório salvo em: safety-report.json"
    SCAN_FAILED=true
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  2. Bandit - Análise de Segurança do Código Python"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Instalar bandit se necessário
pip install -q bandit 2>/dev/null || true

echo "▶️  Analisando código Python com Bandit..."
if [ -f "config/quality/.bandit" ]; then
    CONFIG_FLAG="-c config/quality/.bandit"
else
    CONFIG_FLAG=""
fi

if bandit -r . $CONFIG_FLAG -f json -o bandit-report.json; then
    echo "✅ Nenhum problema de segurança encontrado"
else
    echo "⚠️  Problemas de segurança encontrados!"
    echo "   Relatório salvo em: bandit-report.json"
    SCAN_FAILED=true
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  3. Trivy - Scanning de Imagens Docker"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Verificar se Trivy está instalado
if command -v trivy &> /dev/null; then
    echo "▶️  Verificando imagens Docker com Trivy..."
    
    # Procurar imagens crypto-trading
    IMAGES=$(docker images --format "{{.Repository}}:{{.Tag}}" | grep "crypto-trading" || true)
    
    if [ -z "$IMAGES" ]; then
        echo "⚠️  Nenhuma imagem crypto-trading encontrada"
        echo "   Execute o build primeiro: ./scripts/ci/build.sh"
    else
        for image in $IMAGES; do
            echo ""
            echo "  📦 Scanning: $image"
            
            if trivy image \
                --severity HIGH,CRITICAL \
                --format json \
                --output "trivy-$(echo $image | tr ':/' '-').json" \
                "$image"; then
                echo "  ✅ $image - Nenhuma vulnerabilidade crítica"
            else
                echo "  ⚠️  $image - Vulnerabilidades encontradas!"
                SCAN_FAILED=true
            fi
        done
    fi
else
    echo "⚠️  Trivy não está instalado"
    echo ""
    echo "💡 Para instalar Trivy:"
    echo "   Windows: choco install trivy"
    echo "   Linux: https://aquasecurity.github.io/trivy/latest/getting-started/installation/"
    echo ""
    echo "   Pulando scanning de imagens Docker..."
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  4. Git Secrets - Verificação de Credenciais"
echo "═══════════════════════════════════════════════════════════"
echo ""

echo "▶️  Verificando por credenciais expostas..."

# Padrões comuns de secrets
PATTERNS=(
    "password\s*=\s*['\"][^'\"]+['\"]"
    "api[_-]?key\s*=\s*['\"][^'\"]+['\"]"
    "secret[_-]?key\s*=\s*['\"][^'\"]+['\"]"
    "token\s*=\s*['\"][^'\"]+['\"]"
    "aws[_-]?access[_-]?key"
    "private[_-]?key"
)

SECRETS_FOUND=false

for pattern in "${PATTERNS[@]}"; do
    if grep -rE "$pattern" . \
        --exclude-dir=.git \
        --exclude-dir=.venv \
        --exclude-dir=venv \
        --exclude-dir=node_modules \
        --exclude="*.json" \
        --exclude="*.log" \
        > /dev/null 2>&1; then
        echo "  ⚠️  Possível credencial encontrada: $pattern"
        SECRETS_FOUND=true
    fi
done

if [ "$SECRETS_FOUND" = false ]; then
    echo "✅ Nenhuma credencial exposta encontrada"
else
    echo ""
    echo "⚠️  Possíveis credenciais expostas detectadas!"
    echo "   Revise o código e use variáveis de ambiente"
    SCAN_FAILED=true
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  📊 Relatórios de Segurança Gerados"
echo "═══════════════════════════════════════════════════════════"
echo ""

if [ -f "safety-report.json" ]; then
    echo "  📄 safety-report.json - Vulnerabilidades de dependências"
fi

if [ -f "bandit-report.json" ]; then
    echo "  📄 bandit-report.json - Problemas de segurança no código"
fi

TRIVY_REPORTS=$(ls trivy-*.json 2>/dev/null || true)
if [ -n "$TRIVY_REPORTS" ]; then
    echo "  📄 trivy-*.json - Vulnerabilidades em imagens Docker"
fi

echo ""

if [ "$SCAN_FAILED" = true ]; then
    echo "═══════════════════════════════════════════════════════════"
    echo "  ⚠️  SECURITY SCANNING CONCLUÍDO COM AVISOS"
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    echo "💡 Revise os relatórios e corrija as vulnerabilidades encontradas"
    exit 1
else
    echo "═══════════════════════════════════════════════════════════"
    echo "  ✅ SECURITY SCANNING CONCLUÍDO - NENHUM PROBLEMA CRÍTICO"
    echo "═══════════════════════════════════════════════════════════"
    echo ""
fi
