#!/bin/bash
################################################################################
# Script de Verificação de Progresso - Semana 5 da Onda 2
#
# Descrição: Verifica o progresso da implementação do pipeline CI/CD da
#            Semana 5, identificando o que já foi implementado e o que
#            ainda precisa ser feito.
#
# Autor: Manus AI
# Data: 07 de Novembro de 2025
# Versão: 1.0
# Compatibilidade: Bash 4.0+, Linux, macOS, WSL
################################################################################

set -uo pipefail

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Símbolos
CHECK="✅"
CROSS="❌"
INFO="ℹ️ "
WARN="⚠️ "

# Contadores
total_checks=0
passed_checks=0
failed_checks=0

# Funções de output
write_success() {
    echo -e "${GREEN}${CHECK} $1${NC}"
}

write_failure() {
    echo -e "${RED}${CROSS} $1${NC}"
}

write_info() {
    echo -e "${CYAN}${INFO} $1${NC}"
}

write_warning() {
    echo -e "${YELLOW}${WARN} $1${NC}"
}

write_title() {
    echo ""
    echo -e "${MAGENTA}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${MAGENTA}  $1${NC}"
    echo -e "${MAGENTA}═══════════════════════════════════════════════════════════${NC}"
    echo ""
}

# Banner
clear
echo ""
echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                                                            ║${NC}"
echo -e "${CYAN}║     📊 VERIFICAÇÃO DE PROGRESSO - SEMANA 5 DA ONDA 2      ║${NC}"
echo -e "${CYAN}║        Pipeline CI/CD Automatizado                         ║${NC}"
echo -e "${CYAN}║                                                            ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
write_info "Data: $(date '+%d/%m/%Y %H:%M:%S')"
write_info "Diretório: $(pwd)"
echo ""

# Função para verificar arquivo
test_file_exists() {
    local path="$1"
    local description="$2"
    
    ((total_checks++))
    
    if [[ -f "$path" ]]; then
        write_success "$description"
        ((passed_checks++))
        return 0
    else
        write_failure "$description"
        ((failed_checks++))
        return 1
    fi
}

# Função para verificar diretório
test_directory_exists() {
    local path="$1"
    local description="$2"
    
    ((total_checks++))
    
    if [[ -d "$path" ]]; then
        write_success "$description"
        ((passed_checks++))
        return 0
    else
        write_failure "$description"
        ((failed_checks++))
        return 1
    fi
}

# Função para verificar conteúdo de arquivo
test_file_content() {
    local path="$1"
    local pattern="$2"
    local description="$3"
    
    ((total_checks++))
    
    if [[ -f "$path" ]] && grep -q "$pattern" "$path" 2>/dev/null; then
        write_success "$description"
        ((passed_checks++))
        return 0
    else
        write_failure "$description"
        ((failed_checks++))
        return 1
    fi
}

# ═══════════════════════════════════════════════════════════
# FASE 1: ESTRUTURA DE DIRETÓRIOS
# ═══════════════════════════════════════════════════════════
write_title "📁 FASE 1: ESTRUTURA DE DIRETÓRIOS"

echo -e "${YELLOW}Verificando estrutura de workflows...${NC}"
test_directory_exists ".github" "Diretório .github/"
test_directory_exists ".github/workflows" "Diretório .github/workflows/"

echo -e "\n${YELLOW}Verificando estrutura de scripts...${NC}"
test_directory_exists "scripts" "Diretório scripts/"
test_directory_exists "scripts/ci" "Diretório scripts/ci/"
test_directory_exists "scripts/deploy" "Diretório scripts/deploy/"
test_directory_exists "scripts/quality" "Diretório scripts/quality/"

echo -e "\n${YELLOW}Verificando estrutura de configurações...${NC}"
test_directory_exists "config" "Diretório config/"
test_directory_exists "config/environments" "Diretório config/environments/"
test_directory_exists "config/quality" "Diretório config/quality/"

echo -e "\n${YELLOW}Verificando estrutura de documentação...${NC}"
test_directory_exists "docs" "Diretório docs/"
test_directory_exists "docs/ci-cd" "Diretório docs/ci-cd/"
test_directory_exists "docs/runbooks" "Diretório docs/runbooks/"

# ═══════════════════════════════════════════════════════════
# FASE 2: WORKFLOWS DO GITHUB ACTIONS (DIAS 29-30)
# ═══════════════════════════════════════════════════════════
write_title "🔄 FASE 2: WORKFLOWS DO GITHUB ACTIONS"

echo -e "${YELLOW}Verificando workflow principal de CI...${NC}"
test_file_exists ".github/workflows/ci.yml" "Workflow principal de CI (ci.yml)"
if [[ -f ".github/workflows/ci.yml" ]]; then
    test_file_content ".github/workflows/ci.yml" "lint" "  ├─ Job de linting configurado"
    test_file_content ".github/workflows/ci.yml" "test" "  ├─ Job de testes configurado"
    test_file_content ".github/workflows/ci.yml" "build" "  └─ Job de build configurado"
fi

echo -e "\n${YELLOW}Verificando workflow de validação de PR...${NC}"
test_file_exists ".github/workflows/pr-validation.yml" "Workflow de validação de PR"

echo -e "\n${YELLOW}Verificando configurações de linting...${NC}"
test_file_exists ".flake8" "Configuração do flake8 (.flake8)"
test_file_exists "pyproject.toml" "Configuração do black/isort (pyproject.toml)"
if [[ -f "pyproject.toml" ]]; then
    test_file_content "pyproject.toml" "\[tool\.black\]" "  ├─ Configuração do black"
    test_file_content "pyproject.toml" "\[tool\.isort\]" "  └─ Configuração do isort"
fi

# ═══════════════════════════════════════════════════════════
# FASE 3: DEPLOYMENT AUTOMATIZADO (DIAS 31-32)
# ═══════════════════════════════════════════════════════════
write_title "🚀 FASE 3: DEPLOYMENT AUTOMATIZADO"

echo -e "${YELLOW}Verificando workflows de deployment...${NC}"
test_file_exists ".github/workflows/deploy-staging.yml" "Workflow de deploy para staging"
test_file_exists ".github/workflows/deploy-production.yml" "Workflow de deploy para produção"

echo -e "\n${YELLOW}Verificando scripts de deployment...${NC}"
test_file_exists "scripts/deploy/deploy.sh" "Script principal de deployment"
test_file_exists "scripts/deploy/rollback.sh" "Script de rollback"
test_file_exists "scripts/deploy/health-check.sh" "Script de health check"
test_file_exists "scripts/deploy/notify.sh" "Script de notificações"

echo -e "\n${YELLOW}Verificando configurações de ambientes...${NC}"
test_file_exists "config/environments/dev.env" "Configuração de desenvolvimento"
test_file_exists "config/environments/staging.env" "Configuração de staging"
test_file_exists "config/environments/production.env" "Configuração de produção"

# ═══════════════════════════════════════════════════════════
# FASE 4: QUALITY GATES E SECURITY (DIAS 33-34)
# ═══════════════════════════════════════════════════════════
write_title "🛡️ FASE 4: QUALITY GATES E SECURITY SCANNING"

echo -e "${YELLOW}Verificando workflows de qualidade...${NC}"
test_file_exists ".github/workflows/quality-gates.yml" "Workflow de quality gates"
test_file_exists ".github/workflows/security-scan.yml" "Workflow de security scanning"

echo -e "\n${YELLOW}Verificando configuração de Dependabot...${NC}"
test_file_exists ".github/dependabot.yml" "Configuração do Dependabot"

echo -e "\n${YELLOW}Verificando scripts de qualidade...${NC}"
test_file_exists "scripts/quality/check-coverage.sh" "Script de verificação de cobertura"
test_file_exists "scripts/quality/check-complexity.sh" "Script de verificação de complexidade"
test_file_exists "scripts/quality/generate-report.sh" "Script de geração de relatórios"

echo -e "\n${YELLOW}Verificando scripts de CI...${NC}"
test_file_exists "scripts/ci/lint.sh" "Script de linting"
test_file_exists "scripts/ci/test.sh" "Script de testes"
test_file_exists "scripts/ci/build.sh" "Script de build"
test_file_exists "scripts/ci/security-scan.sh" "Script de security scan"

echo -e "\n${YELLOW}Verificando configurações de qualidade...${NC}"
test_file_exists "config/quality/sonar-project.properties" "Configuração do SonarCloud"
test_file_exists "config/quality/.trivyignore" "Configuração do Trivy"
test_file_exists "config/quality/.bandit" "Configuração do Bandit"

echo -e "\n${YELLOW}Verificando arquivo CODEOWNERS...${NC}"
test_file_exists ".github/CODEOWNERS" "Arquivo CODEOWNERS"

# ═══════════════════════════════════════════════════════════
# FASE 5: DOCUMENTAÇÃO (DIA 35)
# ═══════════════════════════════════════════════════════════
write_title "📚 FASE 5: DOCUMENTAÇÃO E RUNBOOKS"

echo -e "${YELLOW}Verificando documentação de CI/CD...${NC}"
test_file_exists "docs/ci-cd/pipeline-overview.md" "Visão geral do pipeline"
test_file_exists "docs/ci-cd/deployment-guide.md" "Guia de deployment"
test_file_exists "docs/ci-cd/rollback-procedures.md" "Procedimentos de rollback"
test_file_exists "docs/ci-cd/troubleshooting.md" "Guia de troubleshooting"

echo -e "\n${YELLOW}Verificando runbooks operacionais...${NC}"
test_file_exists "docs/runbooks/deployment-checklist.md" "Checklist de deployment"
test_file_exists "docs/runbooks/incident-response.md" "Resposta a incidentes"
test_file_exists "docs/runbooks/emergency-procedures.md" "Procedimentos de emergência"

# ═══════════════════════════════════════════════════════════
# VERIFICAÇÕES ADICIONAIS
# ═══════════════════════════════════════════════════════════
write_title "🔍 VERIFICAÇÕES ADICIONAIS"

echo -e "${YELLOW}Verificando integração com Git...${NC}"
if [[ -d ".git" ]]; then
    write_success "Repositório Git inicializado"
    ((total_checks++))
    ((passed_checks++))
    
    # Verificar se há commits
    if git log --oneline &>/dev/null; then
        write_success "  └─ Commits encontrados no repositório"
        ((total_checks++))
        ((passed_checks++))
    else
        write_warning "  └─ Nenhum commit encontrado"
        ((total_checks++))
        ((failed_checks++))
    fi
else
    write_failure "Repositório Git não inicializado"
    ((total_checks++))
    ((failed_checks++))
fi

echo -e "\n${YELLOW}Verificando Docker...${NC}"
if command -v docker &>/dev/null; then
    docker_version=$(docker --version)
    write_success "Docker instalado: $docker_version"
    ((total_checks++))
    ((passed_checks++))
else
    write_warning "Docker não encontrado ou não está no PATH"
    ((total_checks++))
    ((failed_checks++))
fi

echo -e "\n${YELLOW}Verificando Python...${NC}"
if command -v python3 &>/dev/null; then
    python_version=$(python3 --version)
    write_success "Python instalado: $python_version"
    ((total_checks++))
    ((passed_checks++))
elif command -v python &>/dev/null; then
    python_version=$(python --version)
    write_success "Python instalado: $python_version"
    ((total_checks++))
    ((passed_checks++))
else
    write_warning "Python não encontrado ou não está no PATH"
    ((total_checks++))
    ((failed_checks++))
fi

# ═══════════════════════════════════════════════════════════
# ANÁLISE DE PROGRESSO POR DIA
# ═══════════════════════════════════════════════════════════
write_title "📅 ANÁLISE DE PROGRESSO POR DIA"

# Função auxiliar para calcular progresso
calc_progress() {
    local count=0
    local total=$#
    
    for item in "$@"; do
        if [[ "$item" == "true" ]]; then
            ((count++))
        fi
    done
    
    if [[ $total -gt 0 ]]; then
        echo $(( count * 100 / total ))
    else
        echo 0
    fi
}

# Dia 29
echo -e "${YELLOW}DIA 29: Configuração Inicial do GitHub Actions${NC}"
dia29_items=(
    "$([[ -d ".github/workflows" ]] && echo "true" || echo "false")"
    "$([[ -f ".github/workflows/ci.yml" ]] && echo "true" || echo "false")"
    "$([[ -f ".flake8" ]] && echo "true" || echo "false")"
    "$([[ -f "pyproject.toml" ]] && echo "true" || echo "false")"
)
dia29_progress=$(calc_progress "${dia29_items[@]}")
if [[ $dia29_progress -eq 100 ]]; then
    echo -e "  Progresso: ${GREEN}${dia29_progress}%${NC}"
elif [[ $dia29_progress -ge 50 ]]; then
    echo -e "  Progresso: ${YELLOW}${dia29_progress}%${NC}"
else
    echo -e "  Progresso: ${RED}${dia29_progress}%${NC}"
fi

# Dia 30
echo -e "\n${YELLOW}DIA 30: Integração de Testes e Building${NC}"
dia30_items=(
    "$([[ -f ".github/workflows/ci.yml" ]] && grep -q "test" ".github/workflows/ci.yml" && echo "true" || echo "false")"
    "$([[ -f ".github/workflows/ci.yml" ]] && grep -q "build" ".github/workflows/ci.yml" && echo "true" || echo "false")"
    "$([[ -f ".github/workflows/ci.yml" ]] && grep -q "coverage" ".github/workflows/ci.yml" && echo "true" || echo "false")"
)
dia30_progress=$(calc_progress "${dia30_items[@]}")
if [[ $dia30_progress -eq 100 ]]; then
    echo -e "  Progresso: ${GREEN}${dia30_progress}%${NC}"
elif [[ $dia30_progress -ge 50 ]]; then
    echo -e "  Progresso: ${YELLOW}${dia30_progress}%${NC}"
else
    echo -e "  Progresso: ${RED}${dia30_progress}%${NC}"
fi

# Dia 31
echo -e "\n${YELLOW}DIA 31: Configuração de Ambientes e Deploy Staging${NC}"
dia31_items=(
    "$([[ -d "config/environments" ]] && echo "true" || echo "false")"
    "$([[ -f ".github/workflows/deploy-staging.yml" ]] && echo "true" || echo "false")"
    "$([[ -f "scripts/deploy/deploy.sh" ]] && echo "true" || echo "false")"
)
dia31_progress=$(calc_progress "${dia31_items[@]}")
if [[ $dia31_progress -eq 100 ]]; then
    echo -e "  Progresso: ${GREEN}${dia31_progress}%${NC}"
elif [[ $dia31_progress -ge 50 ]]; then
    echo -e "  Progresso: ${YELLOW}${dia31_progress}%${NC}"
else
    echo -e "  Progresso: ${RED}${dia31_progress}%${NC}"
fi

# Dia 32
echo -e "\n${YELLOW}DIA 32: Deploy Produção e Estratégias Avançadas${NC}"
dia32_items=(
    "$([[ -f ".github/workflows/deploy-production.yml" ]] && echo "true" || echo "false")"
    "$([[ -f "scripts/deploy/rollback.sh" ]] && echo "true" || echo "false")"
    "$([[ -f "scripts/deploy/health-check.sh" ]] && echo "true" || echo "false")"
)
dia32_progress=$(calc_progress "${dia32_items[@]}")
if [[ $dia32_progress -eq 100 ]]; then
    echo -e "  Progresso: ${GREEN}${dia32_progress}%${NC}"
elif [[ $dia32_progress -ge 50 ]]; then
    echo -e "  Progresso: ${YELLOW}${dia32_progress}%${NC}"
else
    echo -e "  Progresso: ${RED}${dia32_progress}%${NC}"
fi

# Dia 33
echo -e "\n${YELLOW}DIA 33: Implementação de Quality Gates${NC}"
dia33_items=(
    "$([[ -f ".github/workflows/quality-gates.yml" ]] && echo "true" || echo "false")"
    "$([[ -f ".github/workflows/pr-validation.yml" ]] && echo "true" || echo "false")"
    "$([[ -f "config/quality/sonar-project.properties" ]] && echo "true" || echo "false")"
    "$([[ -d "scripts/quality" ]] && echo "true" || echo "false")"
)
dia33_progress=$(calc_progress "${dia33_items[@]}")
if [[ $dia33_progress -eq 100 ]]; then
    echo -e "  Progresso: ${GREEN}${dia33_progress}%${NC}"
elif [[ $dia33_progress -ge 50 ]]; then
    echo -e "  Progresso: ${YELLOW}${dia33_progress}%${NC}"
else
    echo -e "  Progresso: ${RED}${dia33_progress}%${NC}"
fi

# Dia 34
echo -e "\n${YELLOW}DIA 34: Security Scanning Completo${NC}"
dia34_items=(
    "$([[ -f ".github/dependabot.yml" ]] && echo "true" || echo "false")"
    "$([[ -f ".github/workflows/security-scan.yml" ]] && echo "true" || echo "false")"
    "$([[ -f "config/quality/.trivyignore" ]] && echo "true" || echo "false")"
    "$([[ -f "scripts/ci/security-scan.sh" ]] && echo "true" || echo "false")"
)
dia34_progress=$(calc_progress "${dia34_items[@]}")
if [[ $dia34_progress -eq 100 ]]; then
    echo -e "  Progresso: ${GREEN}${dia34_progress}%${NC}"
elif [[ $dia34_progress -ge 50 ]]; then
    echo -e "  Progresso: ${YELLOW}${dia34_progress}%${NC}"
else
    echo -e "  Progresso: ${RED}${dia34_progress}%${NC}"
fi

# Dia 35
echo -e "\n${YELLOW}DIA 35: Validação e Documentação${NC}"
dia35_items=(
    "$([[ -d "docs/ci-cd" ]] && echo "true" || echo "false")"
    "$([[ -d "docs/runbooks" ]] && echo "true" || echo "false")"
    "$([[ -f "docs/ci-cd/pipeline-overview.md" ]] && echo "true" || echo "false")"
    "$([[ -f "docs/ci-cd/deployment-guide.md" ]] && echo "true" || echo "false")"
)
dia35_progress=$(calc_progress "${dia35_items[@]}")
if [[ $dia35_progress -eq 100 ]]; then
    echo -e "  Progresso: ${GREEN}${dia35_progress}%${NC}"
elif [[ $dia35_progress -ge 50 ]]; then
    echo -e "  Progresso: ${YELLOW}${dia35_progress}%${NC}"
else
    echo -e "  Progresso: ${RED}${dia35_progress}%${NC}"
fi

# ═══════════════════════════════════════════════════════════
# RESUMO FINAL
# ═══════════════════════════════════════════════════════════
write_title "📊 RESUMO FINAL"

if [[ $total_checks -gt 0 ]]; then
    progress_percentage=$(( passed_checks * 100 / total_checks ))
else
    progress_percentage=0
fi

echo -e "${WHITE}Total de Verificações: $total_checks${NC}"
echo -e "${GREEN}Verificações Aprovadas: $passed_checks${NC}"
echo -e "${RED}Verificações Falhadas: $failed_checks${NC}"
echo ""

# Determinar cor do progresso
if [[ $progress_percentage -eq 100 ]]; then
    progress_color=$GREEN
elif [[ $progress_percentage -ge 75 ]]; then
    progress_color=$CYAN
elif [[ $progress_percentage -ge 50 ]]; then
    progress_color=$YELLOW
elif [[ $progress_percentage -ge 25 ]]; then
    progress_color=$YELLOW
else
    progress_color=$RED
fi

echo -e "${progress_color}PROGRESSO GERAL DA SEMANA 5: ${progress_percentage}%${NC}"

# Barra de progresso visual
bar_length=50
filled_length=$(( bar_length * progress_percentage / 100 ))
empty_length=$(( bar_length - filled_length ))
progress_bar=$(printf "█%.0s" $(seq 1 $filled_length))$(printf "░%.0s" $(seq 1 $empty_length))
echo -e "${CYAN}[$progress_bar]${NC}"

echo ""

# Status geral
if [[ $progress_percentage -eq 100 ]]; then
    write_success "🎉 SEMANA 5 COMPLETA! Todos os componentes foram implementados."
elif [[ $progress_percentage -ge 75 ]]; then
    write_info "🚀 Ótimo progresso! A maioria dos componentes está implementada."
elif [[ $progress_percentage -ge 50 ]]; then
    write_warning "⚠️  Progresso moderado. Continue implementando os componentes restantes."
elif [[ $progress_percentage -ge 25 ]]; then
    write_warning "⚠️  Progresso inicial. Muitos componentes ainda precisam ser implementados."
else
    write_failure "❌ Progresso mínimo. A implementação está no início."
fi

echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Próximos passos recomendados
if [[ $progress_percentage -lt 100 ]]; then
    write_title "🎯 PRÓXIMOS PASSOS RECOMENDADOS"
    
    [[ ! -f ".github/workflows/ci.yml" ]] && echo -e "${YELLOW}1. Criar workflow principal de CI (.github/workflows/ci.yml)${NC}"
    [[ ! -f ".flake8" ]] && echo -e "${YELLOW}2. Configurar linting (.flake8 e pyproject.toml)${NC}"
    [[ ! -f ".github/workflows/deploy-staging.yml" ]] && echo -e "${YELLOW}3. Implementar deployment para staging${NC}"
    [[ ! -f ".github/dependabot.yml" ]] && echo -e "${YELLOW}4. Configurar Dependabot para security scanning${NC}"
    [[ ! -f "docs/ci-cd/pipeline-overview.md" ]] && echo -e "${YELLOW}5. Criar documentação do pipeline CI/CD${NC}"
    
    echo ""
    write_info "Consulte o 'Plano de Ação Detalhado da Semana 5' para instruções completas."
    echo ""
fi

# Salvar relatório
report_path="relatorio_progresso_semana5_$(date '+%Y%m%d_%H%M%S').txt"
cat > "$report_path" << EOF
═══════════════════════════════════════════════════════════
RELATÓRIO DE PROGRESSO - SEMANA 5 DA ONDA 2
Pipeline CI/CD Automatizado
═══════════════════════════════════════════════════════════

Data: $(date '+%d/%m/%Y %H:%M:%S')
Diretório: $(pwd)

RESUMO:
- Total de Verificações: $total_checks
- Verificações Aprovadas: $passed_checks
- Verificações Falhadas: $failed_checks
- Progresso Geral: ${progress_percentage}%

PROGRESSO POR DIA:
- Dia 29: ${dia29_progress}%
- Dia 30: ${dia30_progress}%
- Dia 31: ${dia31_progress}%
- Dia 32: ${dia32_progress}%
- Dia 33: ${dia33_progress}%
- Dia 34: ${dia34_progress}%
- Dia 35: ${dia35_progress}%

═══════════════════════════════════════════════════════════
EOF

write_info "Relatório salvo em: $report_path"
echo ""

# Retornar código de saída baseado no progresso
if [[ $progress_percentage -eq 100 ]]; then
    exit 0
else
    exit 1
fi
