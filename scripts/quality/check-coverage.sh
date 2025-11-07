#!/bin/bash
################################################################################
# Script de Verificação de Cobertura - Quality Check
#
# Descrição: Verifica cobertura de testes e gera relatórios detalhados
# Autor: Manus AI
# Data: 07/11/2025
# Uso: ./check-coverage.sh [threshold]
################################################################################

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# Variáveis
THRESHOLD=${1:-90}  # Threshold padrão: 90%

echo ""
echo "════════════════════════════════════════════════════════════"
echo "  📊 VERIFICAÇÃO DE COBERTURA DE TESTES"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "  Threshold: ${THRESHOLD}%"
echo "  Time: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""
echo "════════════════════════════════════════════════════════════"
echo ""

# Verificar se pytest está instalado
if ! python -m pytest --version &> /dev/null; then
    echo -e "${RED}❌ pytest não está instalado!${NC}"
    echo -e "${YELLOW}   Instale com: pip install pytest pytest-cov${NC}"
    exit 1
fi

echo -e "${GREEN}✅ pytest encontrado${NC}"
echo ""

# Executar testes com cobertura
echo "════════════════════════════════════════════════════════════"
echo "  🧪 EXECUTANDO TESTES"
echo "════════════════════════════════════════════════════════════"
echo ""

echo -e "${CYAN}▶️  Executando testes com cobertura...${NC}"
echo ""

# Executar pytest com cobertura
if python -m pytest \
    --cov=. \
    --cov-report=term-missing \
    --cov-report=html \
    --cov-report=xml \
    --cov-report=json \
    -v; then
    echo ""
    echo -e "${GREEN}✅ Testes executados com sucesso${NC}"
else
    echo ""
    echo -e "${RED}❌ Alguns testes falharam!${NC}"
    exit 1
fi

echo ""

# Gerar relatório de cobertura
echo "════════════════════════════════════════════════════════════"
echo "  📈 RELATÓRIO DE COBERTURA"
echo "════════════════════════════════════════════════════════════"
echo ""

# Obter cobertura total
COVERAGE=$(python -m coverage report | grep TOTAL | awk '{print $4}' | sed 's/%//')

echo -e "${CYAN}Cobertura Total: ${COVERAGE}%${NC}"
echo ""

# Verificar threshold
if [ "${COVERAGE%.*}" -ge "$THRESHOLD" ]; then
    echo -e "${GREEN}✅ Cobertura atende o threshold (≥${THRESHOLD}%)${NC}"
    THRESHOLD_MET=true
else
    echo -e "${RED}❌ Cobertura abaixo do threshold (<${THRESHOLD}%)${NC}"
    THRESHOLD_MET=false
fi

echo ""

# Relatório detalhado por arquivo
echo "════════════════════════════════════════════════════════════"
echo "  📋 COBERTURA POR ARQUIVO"
echo "════════════════════════════════════════════════════════════"
echo ""

python -m coverage report --sort=cover

echo ""

# Identificar arquivos com baixa cobertura
echo "════════════════════════════════════════════════════════════"
echo "  ⚠️  ARQUIVOS COM BAIXA COBERTURA (<80%)"
echo "════════════════════════════════════════════════════════════"
echo ""

LOW_COVERAGE_FILES=$(python -m coverage report | awk '$4 < 80 && NR > 2 {print $1, $4}' | grep -v TOTAL || true)

if [ -z "$LOW_COVERAGE_FILES" ]; then
    echo -e "${GREEN}✅ Nenhum arquivo com cobertura baixa${NC}"
else
    echo -e "${YELLOW}Os seguintes arquivos têm cobertura abaixo de 80%:${NC}"
    echo ""
    echo "$LOW_COVERAGE_FILES" | while read file coverage; do
        echo -e "${YELLOW}  - $file: $coverage${NC}"
    done
fi

echo ""

# Linhas não cobertas
echo "════════════════════════════════════════════════════════════"
echo "  🔍 LINHAS NÃO COBERTAS"
echo "════════════════════════════════════════════════════════════"
echo ""

echo -e "${CYAN}Arquivos com linhas não cobertas:${NC}"
echo ""

python -m coverage report --show-missing | grep -v "100%" | grep -v "TOTAL" | head -10

echo ""

# Relatórios gerados
echo "════════════════════════════════════════════════════════════"
echo "  📄 RELATÓRIOS GERADOS"
echo "════════════════════════════════════════════════════════════"
echo ""

if [ -f "coverage.xml" ]; then
    echo -e "${GREEN}✅ coverage.xml${NC} - Relatório XML (para CI/CD)"
fi

if [ -f ".coverage.json" ]; then
    echo -e "${GREEN}✅ .coverage.json${NC} - Relatório JSON"
fi

if [ -d "htmlcov" ]; then
    echo -e "${GREEN}✅ htmlcov/${NC} - Relatório HTML interativo"
    echo -e "${CYAN}   Abra: htmlcov/index.html${NC}"
fi

echo ""

# Estatísticas adicionais
echo "════════════════════════════════════════════════════════════"
echo "  📊 ESTATÍSTICAS"
echo "════════════════════════════════════════════════════════════"
echo ""

# Total de linhas
TOTAL_LINES=$(python -m coverage report | grep TOTAL | awk '{print $2}')
COVERED_LINES=$(python -m coverage report | grep TOTAL | awk '{print $3}')
MISSING_LINES=$(python -m coverage report | grep TOTAL | awk '{print $4}')

echo -e "${CYAN}Total de linhas:${NC} $TOTAL_LINES"
echo -e "${GREEN}Linhas cobertas:${NC} $COVERED_LINES"
echo -e "${YELLOW}Linhas não cobertas:${NC} $MISSING_LINES"
echo ""

# Número de arquivos
TOTAL_FILES=$(python -m coverage report | grep -v "TOTAL" | grep -v "^-" | wc -l)
FILES_100=$(python -m coverage report | grep "100%" | wc -l)

echo -e "${CYAN}Total de arquivos:${NC} $TOTAL_FILES"
echo -e "${GREEN}Arquivos com 100%:${NC} $FILES_100"
echo ""

# Tendência (se houver histórico)
if [ -f ".coverage_history" ]; then
    PREVIOUS_COVERAGE=$(tail -1 .coverage_history | awk '{print $2}')
    DIFF=$(echo "$COVERAGE - $PREVIOUS_COVERAGE" | bc)
    
    echo -e "${CYAN}Cobertura anterior:${NC} ${PREVIOUS_COVERAGE}%"
    
    if (( $(echo "$DIFF > 0" | bc -l) )); then
        echo -e "${GREEN}Tendência:${NC} ↑ +${DIFF}%"
    elif (( $(echo "$DIFF < 0" | bc -l) )); then
        echo -e "${RED}Tendência:${NC} ↓ ${DIFF}%"
    else
        echo -e "${CYAN}Tendência:${NC} → sem mudança"
    fi
    echo ""
fi

# Salvar histórico
echo "$(date '+%Y-%m-%d') $COVERAGE" >> .coverage_history

# Resumo final
echo "════════════════════════════════════════════════════════════"
echo "  📊 RESUMO FINAL"
echo "════════════════════════════════════════════════════════════"
echo ""

if [ "$THRESHOLD_MET" = true ]; then
    echo -e "${GREEN}✅ VERIFICAÇÃO DE COBERTURA PASSOU${NC}"
    echo ""
    echo -e "${GREEN}Cobertura: ${COVERAGE}% (threshold: ${THRESHOLD}%)${NC}"
    echo ""
    echo -e "${CYAN}💡 Relatório HTML disponível em: htmlcov/index.html${NC}"
    echo ""
    exit 0
else
    echo -e "${RED}❌ VERIFICAÇÃO DE COBERTURA FALHOU${NC}"
    echo ""
    echo -e "${RED}Cobertura: ${COVERAGE}% (threshold: ${THRESHOLD}%)${NC}"
    echo -e "${YELLOW}Diferença: -$((THRESHOLD - ${COVERAGE%.*}))%${NC}"
    echo ""
    echo -e "${YELLOW}💡 Ações recomendadas:${NC}"
    echo -e "${YELLOW}   1. Adicione testes para arquivos com baixa cobertura${NC}"
    echo -e "${YELLOW}   2. Revise o relatório HTML: htmlcov/index.html${NC}"
    echo -e "${YELLOW}   3. Foque em arquivos críticos primeiro${NC}"
    echo ""
    exit 1
fi
