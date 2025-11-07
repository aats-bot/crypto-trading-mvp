#!/bin/bash
################################################################################
# Script de Geração de Relatórios - Quality Report
#
# Descrição: Gera relatório consolidado de qualidade do projeto
# Autor: Manus AI
# Data: 07/11/2025
# Uso: ./generate-report.sh [output_dir]
################################################################################

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BLUE='\033[0;34m'
NC='\033[0m'

# Variáveis
OUTPUT_DIR=${1:-reports}
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
REPORT_FILE="$OUTPUT_DIR/quality_report_$TIMESTAMP.md"

echo ""
echo "════════════════════════════════════════════════════════════"
echo "  📊 GERAÇÃO DE RELATÓRIO DE QUALIDADE"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "  Output: $REPORT_FILE"
echo "  Time: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""
echo "════════════════════════════════════════════════════════════"
echo ""

# Criar diretório de saída
mkdir -p "$OUTPUT_DIR"

# Iniciar relatório
cat > "$REPORT_FILE" <<'EOF'
# 📊 Relatório de Qualidade do Código

**Projeto:** Crypto Trading MVP  
**Data:** $(date '+%Y-%m-%d %H:%M:%S')  
**Gerado por:** Quality Check Script

---

## 📋 Sumário Executivo

EOF

echo -e "${CYAN}▶️  Gerando relatório...${NC}"
echo ""

# ============================================================================
# 1. COBERTURA DE TESTES
# ============================================================================
echo -e "${CYAN}▶️  1. Analisando cobertura de testes...${NC}"

if command -v pytest &> /dev/null; then
    cat >> "$REPORT_FILE" <<'EOF'
## 🧪 Cobertura de Testes

EOF
    
    # Executar testes com cobertura
    python -m pytest --cov=. --cov-report=term-missing --cov-report=json -q &> /dev/null || true
    
    if [ -f ".coverage.json" ]; then
        COVERAGE=$(python -c "import json; data=json.load(open('.coverage.json')); print(f\"{data['totals']['percent_covered']:.1f}\")")
        
        cat >> "$REPORT_FILE" <<EOF
**Cobertura Total:** ${COVERAGE}%

\`\`\`
$(python -m coverage report)
\`\`\`

EOF
        
        echo -e "${GREEN}   ✅ Cobertura: ${COVERAGE}%${NC}"
    else
        echo "⚠️ Dados de cobertura não disponíveis" >> "$REPORT_FILE"
        echo ""  >> "$REPORT_FILE"
        echo -e "${YELLOW}   ⚠️  Dados de cobertura não disponíveis${NC}"
    fi
else
    echo "⚠️ pytest não instalado - cobertura não verificada" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    echo -e "${YELLOW}   ⚠️  pytest não instalado${NC}"
fi

echo ""

# ============================================================================
# 2. COMPLEXIDADE CICLOMÁTICA
# ============================================================================
echo -e "${CYAN}▶️  2. Analisando complexidade ciclomática...${NC}"

if command -v radon &> /dev/null; then
    cat >> "$REPORT_FILE" <<'EOF'
## 🔄 Complexidade Ciclomática

EOF
    
    # Análise de complexidade
    radon cc . -a -s > /tmp/complexity.txt 2>/dev/null || true
    
    # Contar por classificação
    A_COUNT=$(radon cc . -s 2>/dev/null | grep -c " A " || echo "0")
    B_COUNT=$(radon cc . -s 2>/dev/null | grep -c " B " || echo "0")
    C_COUNT=$(radon cc . -s 2>/dev/null | grep -c " C " || echo "0")
    D_COUNT=$(radon cc . -s 2>/dev/null | grep -c " D " || echo "0")
    F_COUNT=$(radon cc . -s 2>/dev/null | grep -c " F " || echo "0")
    
    cat >> "$REPORT_FILE" <<EOF
**Distribuição:**
- 🟢 A (1-5): $A_COUNT funções
- 🟢 B (6-10): $B_COUNT funções
- 🟡 C (11-20): $C_COUNT funções
- 🟡 D (21-30): $D_COUNT funções
- 🔴 F (31+): $F_COUNT funções

EOF
    
    # Funções com alta complexidade
    HIGH_COMPLEXITY=$(radon cc . -n C -s 2>/dev/null | head -10)
    
    if [ -n "$HIGH_COMPLEXITY" ]; then
        cat >> "$REPORT_FILE" <<EOF
**Funções com Alta Complexidade:**

\`\`\`
$HIGH_COMPLEXITY
\`\`\`

EOF
    fi
    
    echo -e "${GREEN}   ✅ Complexidade analisada${NC}"
else
    echo "⚠️ radon não instalado - complexidade não verificada" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    echo -e "${YELLOW}   ⚠️  radon não instalado${NC}"
fi

echo ""

# ============================================================================
# 3. ÍNDICE DE MANUTENIBILIDADE
# ============================================================================
echo -e "${CYAN}▶️  3. Analisando manutenibilidade...${NC}"

if command -v radon &> /dev/null; then
    cat >> "$REPORT_FILE" <<'EOF'
## 🔧 Índice de Manutenibilidade

EOF
    
    # Análise de manutenibilidade
    MA_COUNT=$(radon mi . -s 2>/dev/null | grep -c " A " || echo "0")
    MB_COUNT=$(radon mi . -s 2>/dev/null | grep -c " B " || echo "0")
    MC_COUNT=$(radon mi . -s 2>/dev/null | grep -c " C " || echo "0")
    
    cat >> "$REPORT_FILE" <<EOF
**Distribuição:**
- 🟢 A (100-20): $MA_COUNT arquivos
- 🟡 B (20-10): $MB_COUNT arquivos
- 🔴 C (10-0): $MC_COUNT arquivos

EOF
    
    # Arquivos com baixa manutenibilidade
    LOW_MAINT=$(radon mi . -n C -s 2>/dev/null | head -10)
    
    if [ -n "$LOW_MAINT" ]; then
        cat >> "$REPORT_FILE" <<EOF
**Arquivos com Baixa Manutenibilidade:**

\`\`\`
$LOW_MAINT
\`\`\`

EOF
    fi
    
    echo -e "${GREEN}   ✅ Manutenibilidade analisada${NC}"
else
    echo -e "${YELLOW}   ⚠️  radon não instalado${NC}"
fi

echo ""

# ============================================================================
# 4. LINTING
# ============================================================================
echo -e "${CYAN}▶️  4. Executando linting...${NC}"

if command -v flake8 &> /dev/null; then
    cat >> "$REPORT_FILE" <<'EOF'
## 🔍 Linting (Flake8)

EOF
    
    # Executar flake8
    flake8 . --count --statistics > /tmp/flake8.txt 2>&1 || true
    
    ERROR_COUNT=$(grep -o "^[0-9]*" /tmp/flake8.txt | head -1 || echo "0")
    
    cat >> "$REPORT_FILE" <<EOF
**Total de Issues:** $ERROR_COUNT

EOF
    
    if [ "$ERROR_COUNT" -gt 0 ]; then
        cat >> "$REPORT_FILE" <<EOF
\`\`\`
$(head -20 /tmp/flake8.txt)
\`\`\`

EOF
    else
        echo "✅ Nenhum issue encontrado" >> "$REPORT_FILE"
        echo "" >> "$REPORT_FILE"
    fi
    
    echo -e "${GREEN}   ✅ Linting executado${NC}"
else
    echo "⚠️ flake8 não instalado" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    echo -e "${YELLOW}   ⚠️  flake8 não instalado${NC}"
fi

echo ""

# ============================================================================
# 5. SEGURANÇA
# ============================================================================
echo -e "${CYAN}▶️  5. Verificando segurança...${NC}"

if command -v bandit &> /dev/null; then
    cat >> "$REPORT_FILE" <<'EOF'
## 🛡️ Segurança (Bandit)

EOF
    
    # Executar bandit
    bandit -r . -f json -o /tmp/bandit.json 2>/dev/null || true
    
    if [ -f "/tmp/bandit.json" ]; then
        HIGH=$(cat /tmp/bandit.json | grep -o '"issue_severity": "HIGH"' | wc -l)
        MEDIUM=$(cat /tmp/bandit.json | grep -o '"issue_severity": "MEDIUM"' | wc -l)
        LOW=$(cat /tmp/bandit.json | grep -o '"issue_severity": "LOW"' | wc -l)
        
        cat >> "$REPORT_FILE" <<EOF
**Issues Encontrados:**
- 🔴 High: $HIGH
- 🟡 Medium: $MEDIUM
- 🟢 Low: $LOW

EOF
        
        echo -e "${GREEN}   ✅ Segurança verificada${NC}"
    fi
else
    echo "⚠️ bandit não instalado" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    echo -e "${YELLOW}   ⚠️  bandit não instalado${NC}"
fi

echo ""

# ============================================================================
# 6. MÉTRICAS DE CÓDIGO
# ============================================================================
echo -e "${CYAN}▶️  6. Coletando métricas de código...${NC}"

cat >> "$REPORT_FILE" <<'EOF'
## 📏 Métricas de Código

EOF

# Contar linhas de código
if command -v radon &> /dev/null; then
    radon raw . -s > /tmp/raw_metrics.txt 2>/dev/null || true
    
    if [ -f "/tmp/raw_metrics.txt" ]; then
        cat >> "$REPORT_FILE" <<EOF
\`\`\`
$(grep -A 10 "** Total **" /tmp/raw_metrics.txt)
\`\`\`

EOF
    fi
else
    # Contagem simples
    TOTAL_LINES=$(find . -name "*.py" -exec wc -l {} + | tail -1 | awk '{print $1}')
    TOTAL_FILES=$(find . -name "*.py" | wc -l)
    
    cat >> "$REPORT_FILE" <<EOF
- **Total de arquivos Python:** $TOTAL_FILES
- **Total de linhas:** $TOTAL_LINES

EOF
fi

echo -e "${GREEN}   ✅ Métricas coletadas${NC}"
echo ""

# ============================================================================
# 7. RECOMENDAÇÕES
# ============================================================================
echo -e "${CYAN}▶️  7. Gerando recomendações...${NC}"

cat >> "$REPORT_FILE" <<'EOF'
## 💡 Recomendações

### Prioridade Alta
EOF

# Adicionar recomendações baseadas nas métricas
if [ -n "$COVERAGE" ] && [ "${COVERAGE%.*}" -lt 90 ]; then
    echo "- 🔴 Aumentar cobertura de testes para ≥90% (atual: ${COVERAGE}%)" >> "$REPORT_FILE"
fi

if [ "$F_COUNT" -gt 0 ]; then
    echo "- 🔴 Refatorar $F_COUNT funções com complexidade muito alta (F)" >> "$REPORT_FILE"
fi

if [ "$HIGH" -gt 0 ]; then
    echo "- 🔴 Corrigir $HIGH issues de segurança de alta severidade" >> "$REPORT_FILE"
fi

cat >> "$REPORT_FILE" <<'EOF'

### Prioridade Média
EOF

if [ "$D_COUNT" -gt 0 ]; then
    echo "- 🟡 Simplificar $D_COUNT funções com alta complexidade (D)" >> "$REPORT_FILE"
fi

if [ "$MC_COUNT" -gt 0 ]; then
    echo "- 🟡 Melhorar manutenibilidade de $MC_COUNT arquivos" >> "$REPORT_FILE"
fi

cat >> "$REPORT_FILE" <<'EOF'

### Boas Práticas
- ✅ Manter cobertura de testes acima de 90%
- ✅ Manter complexidade ciclomática abaixo de 10
- ✅ Executar linting regularmente
- ✅ Revisar issues de segurança periodicamente

EOF

echo -e "${GREEN}   ✅ Recomendações geradas${NC}"
echo ""

# ============================================================================
# FINALIZAÇÃO
# ============================================================================

cat >> "$REPORT_FILE" <<EOF

---

**Relatório gerado em:** $(date '+%Y-%m-%d %H:%M:%S')  
**Script:** generate-report.sh

EOF

echo "════════════════════════════════════════════════════════════"
echo "  ✅ RELATÓRIO GERADO COM SUCESSO!"
echo "════════════════════════════════════════════════════════════"
echo ""
echo -e "${GREEN}Relatório salvo em: $REPORT_FILE${NC}"
echo ""
echo -e "${CYAN}💡 Para visualizar:${NC}"
echo -e "${CYAN}   cat $REPORT_FILE${NC}"
echo -e "${CYAN}   ou abra em um visualizador de Markdown${NC}"
echo ""

# Copiar relatório mais recente
cp "$REPORT_FILE" "$OUTPUT_DIR/quality_report_latest.md"

echo -e "${GREEN}✅ Cópia criada: $OUTPUT_DIR/quality_report_latest.md${NC}"
echo ""
