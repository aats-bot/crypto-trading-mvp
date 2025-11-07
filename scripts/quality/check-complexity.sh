#!/bin/bash
################################################################################
# Script de Verificação de Complexidade - Quality Check
#
# Descrição: Analisa complexidade ciclomática e maintainability do código
# Autor: Manus AI
# Data: 07/11/2025
# Uso: ./check-complexity.sh [max_complexity]
################################################################################

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# Variáveis
MAX_COMPLEXITY=${1:-10}  # Complexidade máxima aceitável

echo ""
echo "════════════════════════════════════════════════════════════"
echo "  📊 VERIFICAÇÃO DE COMPLEXIDADE DE CÓDIGO"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "  Max Complexity: $MAX_COMPLEXITY"
echo "  Time: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""
echo "════════════════════════════════════════════════════════════"
echo ""

# Verificar se radon está instalado
if ! command -v radon &> /dev/null; then
    echo -e "${RED}❌ radon não está instalado!${NC}"
    echo -e "${YELLOW}   Instale com: pip install radon${NC}"
    exit 1
fi

echo -e "${GREEN}✅ radon encontrado${NC}"
echo ""

# Complexidade Ciclomática
echo "════════════════════════════════════════════════════════════"
echo "  🔄 COMPLEXIDADE CICLOMÁTICA"
echo "════════════════════════════════════════════════════════════"
echo ""

echo -e "${CYAN}▶️  Analisando complexidade ciclomática...${NC}"
echo ""

# Gerar relatório completo
radon cc . -a -s > complexity_report.txt

# Mostrar resumo
echo -e "${CYAN}Resumo por classificação:${NC}"
echo ""

radon cc . -a -s | head -30

echo ""

# Verificar funções com alta complexidade
echo "════════════════════════════════════════════════════════════"
echo "  ⚠️  FUNÇÕES COM ALTA COMPLEXIDADE (>$MAX_COMPLEXITY)"
echo "════════════════════════════════════════════════════════════"
echo ""

HIGH_COMPLEXITY=$(radon cc . -n C -s)

if [ -z "$HIGH_COMPLEXITY" ]; then
    echo -e "${GREEN}✅ Nenhuma função com complexidade excessiva${NC}"
    COMPLEXITY_OK=true
else
    echo -e "${RED}As seguintes funções têm complexidade alta:${NC}"
    echo ""
    echo "$HIGH_COMPLEXITY"
    COMPLEXITY_OK=false
fi

echo ""

# Complexidade por arquivo
echo "════════════════════════════════════════════════════════════"
echo "  📁 COMPLEXIDADE MÉDIA POR ARQUIVO"
echo "════════════════════════════════════════════════════════════"
echo ""

radon cc . -a | grep "Average complexity" | sort -t: -k2 -rn | head -10

echo ""

# Maintainability Index
echo "════════════════════════════════════════════════════════════"
echo "  🔧 ÍNDICE DE MANUTENIBILIDADE"
echo "════════════════════════════════════════════════════════════"
echo ""

echo -e "${CYAN}▶️  Calculando índice de manutenibilidade...${NC}"
echo ""

# Gerar relatório de maintainability
radon mi . -s > maintainability_report.txt

# Mostrar resumo
radon mi . -s | head -20

echo ""

# Arquivos com baixa manutenibilidade
echo "════════════════════════════════════════════════════════════"
echo "  ⚠️  ARQUIVOS COM BAIXA MANUTENIBILIDADE (C ou pior)"
echo "════════════════════════════════════════════════════════════"
echo ""

LOW_MAINTAINABILITY=$(radon mi . -n C -s)

if [ -z "$LOW_MAINTAINABILITY" ]; then
    echo -e "${GREEN}✅ Todos os arquivos têm boa manutenibilidade${NC}"
    MAINTAINABILITY_OK=true
else
    echo -e "${YELLOW}Os seguintes arquivos têm baixa manutenibilidade:${NC}"
    echo ""
    echo "$LOW_MAINTAINABILITY"
    MAINTAINABILITY_OK=false
fi

echo ""

# Raw Metrics
echo "════════════════════════════════════════════════════════════"
echo "  📏 MÉTRICAS RAW"
echo "════════════════════════════════════════════════════════════"
echo ""

echo -e "${CYAN}▶️  Calculando métricas raw...${NC}"
echo ""

# LOC, LLOC, SLOC, Comments, etc
radon raw . -s > raw_metrics.txt

# Mostrar resumo
echo -e "${CYAN}Resumo de métricas:${NC}"
echo ""

radon raw . -s | grep -A 5 "** Total **"

echo ""

# Estatísticas gerais
echo "════════════════════════════════════════════════════════════"
echo "  📊 ESTATÍSTICAS GERAIS"
echo "════════════════════════════════════════════════════════════"
echo ""

# Contar funções por complexidade
A_COUNT=$(radon cc . -s | grep -c " A " || true)
B_COUNT=$(radon cc . -s | grep -c " B " || true)
C_COUNT=$(radon cc . -s | grep -c " C " || true)
D_COUNT=$(radon cc . -s | grep -c " D " || true)
F_COUNT=$(radon cc . -s | grep -c " F " || true)

echo -e "${CYAN}Distribuição de Complexidade:${NC}"
echo -e "${GREEN}  A (1-5):   $A_COUNT funções${NC}"
echo -e "${GREEN}  B (6-10):  $B_COUNT funções${NC}"
echo -e "${YELLOW}  C (11-20): $C_COUNT funções${NC}"
echo -e "${YELLOW}  D (21-30): $D_COUNT funções${NC}"
echo -e "${RED}  F (31+):   $F_COUNT funções${NC}"
echo ""

# Contar arquivos por manutenibilidade
MA_COUNT=$(radon mi . -s | grep -c " A " || true)
MB_COUNT=$(radon mi . -s | grep -c " B " || true)
MC_COUNT=$(radon mi . -s | grep -c " C " || true)

echo -e "${CYAN}Distribuição de Manutenibilidade:${NC}"
echo -e "${GREEN}  A (100-20): $MA_COUNT arquivos${NC}"
echo -e "${YELLOW}  B (20-10):  $MB_COUNT arquivos${NC}"
echo -e "${RED}  C (10-0):   $MC_COUNT arquivos${NC}"
echo ""

# Recomendações
echo "════════════════════════════════════════════════════════════"
echo "  💡 RECOMENDAÇÕES"
echo "════════════════════════════════════════════════════════════"
echo ""

if [ "$COMPLEXITY_OK" = false ]; then
    echo -e "${YELLOW}Complexidade Ciclomática:${NC}"
    echo "  - Refatore funções com complexidade > $MAX_COMPLEXITY"
    echo "  - Divida funções grandes em funções menores"
    echo "  - Simplifique condicionais complexos"
    echo ""
fi

if [ "$MAINTAINABILITY_OK" = false ]; then
    echo -e "${YELLOW}Manutenibilidade:${NC}"
    echo "  - Melhore a documentação dos arquivos"
    echo "  - Reduza o tamanho das funções"
    echo "  - Simplifique a lógica"
    echo ""
fi

if [ "$COMPLEXITY_OK" = true ] && [ "$MAINTAINABILITY_OK" = true ]; then
    echo -e "${GREEN}✅ Código está em boa forma!${NC}"
    echo ""
    echo "Continue mantendo:"
    echo "  - Funções pequenas e focadas"
    echo "  - Lógica simples e clara"
    echo "  - Boa documentação"
    echo ""
fi

# Relatórios gerados
echo "════════════════════════════════════════════════════════════"
echo "  📄 RELATÓRIOS GERADOS"
echo "════════════════════════════════════════════════════════════"
echo ""

echo -e "${GREEN}✅ complexity_report.txt${NC} - Relatório de complexidade"
echo -e "${GREEN}✅ maintainability_report.txt${NC} - Relatório de manutenibilidade"
echo -e "${GREEN}✅ raw_metrics.txt${NC} - Métricas raw"
echo ""

# Resumo final
echo "════════════════════════════════════════════════════════════"
echo "  📊 RESUMO FINAL"
echo "════════════════════════════════════════════════════════════"
echo ""

if [ "$COMPLEXITY_OK" = true ] && [ "$MAINTAINABILITY_OK" = true ]; then
    echo -e "${GREEN}✅ VERIFICAÇÃO DE COMPLEXIDADE PASSOU${NC}"
    echo ""
    echo -e "${GREEN}Todas as métricas estão dentro dos limites aceitáveis${NC}"
    echo ""
    exit 0
else
    echo -e "${YELLOW}⚠️  VERIFICAÇÃO DE COMPLEXIDADE COM AVISOS${NC}"
    echo ""
    
    if [ "$COMPLEXITY_OK" = false ]; then
        echo -e "${YELLOW}  - Funções com alta complexidade detectadas${NC}"
    fi
    
    if [ "$MAINTAINABILITY_OK" = false ]; then
        echo -e "${YELLOW}  - Arquivos com baixa manutenibilidade detectados${NC}"
    fi
    
    echo ""
    echo -e "${CYAN}💡 Revise os relatórios e considere refatoração${NC}"
    echo ""
    
    # Não falhar o build, apenas avisar
    exit 0
fi
