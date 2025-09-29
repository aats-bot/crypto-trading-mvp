#!/bin/bash
# Script de Testes - Bot de Trading MVP
# Este script automatiza a execução de todos os tipos de testes

set -e  # Parar em caso de erro

# Configurações
PROJECT_NAME="trading-bot-mvp"
TEST_DB_NAME="trading_bot_test"
COVERAGE_THRESHOLD=70

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Função para log
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] ✅ $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ❌ $1${NC}"
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] ⚠️  $1${NC}"
}

info() {
    echo -e "${CYAN}[$(date +'%Y-%m-%d %H:%M:%S')] ℹ️  $1${NC}"
}

# Função para verificar dependências
check_dependencies() {
    log "Verificando dependências para testes..."
    
    # Verificar Python
    if ! command -v python3 &> /dev/null; then
        error "Python 3 não encontrado!"
        exit 1
    fi
    
    # Verificar se estamos em um ambiente virtual
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        warning "Não está em um ambiente virtual"
        if [ -d "venv" ]; then
            log "Ativando ambiente virtual..."
            source venv/bin/activate
        else
            warning "Ambiente virtual não encontrado - criando..."
            python3 -m venv venv
            source venv/bin/activate
        fi
    fi
    
    # Verificar pytest
    if ! python -c "import pytest" 2>/dev/null; then
        log "Instalando pytest..."
        pip install pytest pytest-cov pytest-asyncio pytest-mock pytest-xdist
    fi
    
    success "Dependências verificadas"
}

# Função para configurar ambiente de teste
setup_test_environment() {
    log "Configurando ambiente de teste..."
    
    # Carregar variáveis de ambiente de teste
    if [ -f ".env.test" ]; then
        export $(cat .env.test | grep -v '^#' | xargs)
        info "Variáveis de .env.test carregadas"
    elif [ -f ".env" ]; then
        export $(cat .env | grep -v '^#' | xargs)
        info "Variáveis de .env carregadas"
    fi
    
    # Configurar variáveis específicas para teste
    export ENVIRONMENT=test
    export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/${TEST_DB_NAME}"
    export REDIS_URL="redis://localhost:6379/1"
    export BYBIT_TESTNET=true
    export LOG_LEVEL=WARNING
    
    # Verificar se PostgreSQL está rodando
    if command -v pg_isready &> /dev/null; then
        if pg_isready -h localhost -p 5432 &> /dev/null; then
            success "PostgreSQL está rodando"
        else
            warning "PostgreSQL não está rodando - alguns testes podem falhar"
        fi
    fi
    
    # Verificar se Redis está rodando
    if command -v redis-cli &> /dev/null; then
        if redis-cli ping &> /dev/null; then
            success "Redis está rodando"
        else
            warning "Redis não está rodando - alguns testes podem falhar"
        fi
    fi
    
    success "Ambiente de teste configurado"
}

# Função para preparar banco de dados de teste
setup_test_database() {
    log "Preparando banco de dados de teste..."
    
    # Verificar se psql está disponível
    if command -v psql &> /dev/null; then
        # Criar banco de teste se não existir
        psql -h localhost -U postgres -tc "SELECT 1 FROM pg_database WHERE datname = '${TEST_DB_NAME}'" | grep -q 1 || \
        psql -h localhost -U postgres -c "CREATE DATABASE ${TEST_DB_NAME};"
        
        # Executar migrations se existir alembic
        if [ -f "alembic.ini" ]; then
            log "Executando migrations de teste..."
            alembic upgrade head
        fi
        
        success "Banco de dados de teste preparado"
    else
        warning "psql não encontrado - pulando configuração do banco"
    fi
}

# Função para executar testes unitários
run_unit_tests() {
    log "Executando testes unitários..."
    
    if [ -d "tests/unit" ]; then
        pytest tests/unit/ \
            -v \
            --tb=short \
            --cov=. \
            --cov-report=term-missing \
            --cov-report=html:htmlcov/unit \
            --cov-report=xml:coverage-unit.xml \
            --junit-xml=test-results-unit.xml \
            --cov-fail-under=${COVERAGE_THRESHOLD} \
            -x
        
        success "Testes unitários concluídos"
    else
        warning "Diretório tests/unit/ não encontrado"
    fi
}

# Função para executar testes de integração
run_integration_tests() {
    log "Executando testes de integração..."
    
    if [ -d "tests/integration" ]; then
        pytest tests/integration/ \
            -v \
            --tb=short \
            --junit-xml=test-results-integration.xml \
            -x
        
        success "Testes de integração concluídos"
    else
        warning "Diretório tests/integration/ não encontrado"
    fi
}

# Função para executar testes de API
run_api_tests() {
    log "Executando testes de API..."
    
    if [ -d "tests/api" ]; then
        # Verificar se a API está rodando
        if curl -f http://localhost:8000/health &> /dev/null; then
            pytest tests/api/ \
                -v \
                --tb=short \
                --junit-xml=test-results-api.xml
            
            success "Testes de API concluídos"
        else
            warning "API não está rodando - pulando testes de API"
            info "Para executar testes de API, inicie a aplicação primeiro"
        fi
    else
        warning "Diretório tests/api/ não encontrado"
    fi
}

# Função para executar testes de performance
run_performance_tests() {
    log "Executando testes de performance..."
    
    if [ -d "tests/performance" ]; then
        pytest tests/performance/ \
            -v \
            --tb=short \
            --benchmark-only \
            --benchmark-json=benchmark-results.json \
            --junit-xml=test-results-performance.xml
        
        success "Testes de performance concluídos"
    else
        warning "Diretório tests/performance/ não encontrado"
    fi
}

# Função para executar testes de segurança
run_security_tests() {
    log "Executando testes de segurança..."
    
    # Bandit - análise de segurança do código
    if command -v bandit &> /dev/null; then
        log "Executando Bandit (análise de segurança)..."
        bandit -r . -f json -o security-report.json || warning "Problemas de segurança encontrados"
    fi
    
    # Safety - verificação de vulnerabilidades em dependências
    if command -v safety &> /dev/null; then
        log "Executando Safety (vulnerabilidades em dependências)..."
        safety check --json --output safety-report.json || warning "Vulnerabilidades encontradas"
    fi
    
    # Semgrep - análise estática de código
    if command -v semgrep &> /dev/null; then
        log "Executando Semgrep (análise estática)..."
        semgrep --config=auto --json --output=semgrep-report.json . || warning "Problemas encontrados pelo Semgrep"
    fi
    
    success "Testes de segurança concluídos"
}

# Função para executar testes de carga básicos
run_load_tests() {
    log "Executando testes de carga básicos..."
    
    # Verificar se a API está rodando
    if curl -f http://localhost:8000/health &> /dev/null; then
        log "Executando teste de carga simples..."
        
        # Teste básico com curl
        for i in {1..50}; do
            curl -s http://localhost:8000/api/v1/status > /dev/null &
        done
        wait
        
        # Se locust estiver disponível, executar teste mais completo
        if command -v locust &> /dev/null && [ -f "tests/load/locustfile.py" ]; then
            log "Executando teste com Locust..."
            locust -f tests/load/locustfile.py --headless -u 10 -r 2 -t 30s --host=http://localhost:8000
        fi
        
        success "Testes de carga concluídos"
    else
        warning "API não está rodando - pulando testes de carga"
    fi
}

# Função para gerar relatórios
generate_reports() {
    log "Gerando relatórios de teste..."
    
    # Criar diretório de relatórios
    mkdir -p reports/
    
    # Mover arquivos de relatório
    mv test-results-*.xml reports/ 2>/dev/null || true
    mv coverage*.xml reports/ 2>/dev/null || true
    mv *-report.json reports/ 2>/dev/null || true
    mv benchmark-results.json reports/ 2>/dev/null || true
    
    # Gerar relatório consolidado
    cat > reports/test-summary.md << EOF
# 📊 Relatório de Testes - $(date)

## 📈 Cobertura de Código
$(coverage report --skip-covered 2>/dev/null || echo "Relatório de cobertura não disponível")

## 🧪 Resumo dos Testes
- **Testes Unitários**: $(grep -c "testcase" reports/test-results-unit.xml 2>/dev/null || echo "N/A") testes
- **Testes de Integração**: $(grep -c "testcase" reports/test-results-integration.xml 2>/dev/null || echo "N/A") testes
- **Testes de API**: $(grep -c "testcase" reports/test-results-api.xml 2>/dev/null || echo "N/A") testes
- **Testes de Performance**: $(grep -c "testcase" reports/test-results-performance.xml 2>/dev/null || echo "N/A") testes

## 🔒 Segurança
- **Bandit**: $([ -f reports/security-report.json ] && echo "Executado" || echo "Não executado")
- **Safety**: $([ -f reports/safety-report.json ] && echo "Executado" || echo "Não executado")
- **Semgrep**: $([ -f reports/semgrep-report.json ] && echo "Executado" || echo "Não executado")

## 📁 Arquivos Gerados
- Cobertura HTML: htmlcov/index.html
- Relatórios XML: reports/
- Relatórios de Segurança: reports/
EOF
    
    success "Relatórios gerados em reports/"
}

# Função para limpeza pós-teste
cleanup() {
    log "Executando limpeza pós-teste..."
    
    # Limpar cache de teste
    find . -name "*.pyc" -delete 2>/dev/null || true
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    rm -rf .pytest_cache/ 2>/dev/null || true
    
    # Limpar banco de teste se especificado
    if [ "$CLEANUP_DB" = "true" ] && command -v psql &> /dev/null; then
        psql -h localhost -U postgres -c "DROP DATABASE IF EXISTS ${TEST_DB_NAME};" 2>/dev/null || true
    fi
    
    success "Limpeza concluída"
}

# Função para mostrar ajuda
show_help() {
    echo "Uso: $0 [opções]"
    echo ""
    echo "Opções:"
    echo "  -u, --unit           Executar apenas testes unitários"
    echo "  -i, --integration    Executar apenas testes de integração"
    echo "  -a, --api           Executar apenas testes de API"
    echo "  -p, --performance   Executar apenas testes de performance"
    echo "  -s, --security      Executar apenas testes de segurança"
    echo "  -l, --load          Executar apenas testes de carga"
    echo "  -f, --fast          Executar testes rápidos (unitários + integração)"
    echo "  -A, --all           Executar todos os tipos de teste (padrão)"
    echo "  -c, --coverage      Gerar apenas relatório de cobertura"
    echo "  -C, --cleanup-db    Limpar banco de dados após testes"
    echo "  -v, --verbose       Modo verboso"
    echo "  -h, --help          Mostrar esta ajuda"
    echo ""
    echo "Exemplos:"
    echo "  $0                  # Executar todos os testes"
    echo "  $0 -u               # Apenas testes unitários"
    echo "  $0 -f               # Testes rápidos"
    echo "  $0 -s -C            # Testes de segurança e limpar DB"
}

# Função principal
main() {
    local run_unit=false
    local run_integration=false
    local run_api=false
    local run_performance=false
    local run_security=false
    local run_load=false
    local run_all=true
    local coverage_only=false
    local verbose=false
    
    # Processar argumentos
    while [[ $# -gt 0 ]]; do
        case $1 in
            -u|--unit)
                run_unit=true
                run_all=false
                shift
                ;;
            -i|--integration)
                run_integration=true
                run_all=false
                shift
                ;;
            -a|--api)
                run_api=true
                run_all=false
                shift
                ;;
            -p|--performance)
                run_performance=true
                run_all=false
                shift
                ;;
            -s|--security)
                run_security=true
                run_all=false
                shift
                ;;
            -l|--load)
                run_load=true
                run_all=false
                shift
                ;;
            -f|--fast)
                run_unit=true
                run_integration=true
                run_all=false
                shift
                ;;
            -A|--all)
                run_all=true
                shift
                ;;
            -c|--coverage)
                coverage_only=true
                shift
                ;;
            -C|--cleanup-db)
                export CLEANUP_DB=true
                shift
                ;;
            -v|--verbose)
                verbose=true
                export PYTEST_ARGS="-v -s"
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                error "Opção desconhecida: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    log "Iniciando execução de testes do $PROJECT_NAME..."
    
    # Verificar se estamos no diretório correto
    if [ ! -f "requirements.txt" ] && [ ! -f "pyproject.toml" ]; then
        error "Não parece ser um projeto Python válido"
        exit 1
    fi
    
    # Configurar ambiente
    check_dependencies
    setup_test_environment
    setup_test_database
    
    # Executar testes baseado nos argumentos
    if [ "$coverage_only" = true ]; then
        log "Gerando apenas relatório de cobertura..."
        coverage html
        coverage report
    elif [ "$run_all" = true ]; then
        log "Executando todos os tipos de teste..."
        run_unit_tests
        run_integration_tests
        run_api_tests
        run_performance_tests
        run_security_tests
        run_load_tests
    else
        [ "$run_unit" = true ] && run_unit_tests
        [ "$run_integration" = true ] && run_integration_tests
        [ "$run_api" = true ] && run_api_tests
        [ "$run_performance" = true ] && run_performance_tests
        [ "$run_security" = true ] && run_security_tests
        [ "$run_load" = true ] && run_load_tests
    fi
    
    # Gerar relatórios e limpar
    generate_reports
    cleanup
    
    success "Execução de testes concluída! 🎉"
    
    # Mostrar resumo
    echo ""
    log "📊 Resumo:"
    echo "  - Relatórios: reports/"
    echo "  - Cobertura HTML: htmlcov/index.html"
    echo "  - Logs de teste: pytest.log"
    echo ""
    
    # Verificar se todos os testes passaram
    if [ -f "reports/test-results-unit.xml" ]; then
        if grep -q 'failures="0"' reports/test-results-unit.xml; then
            success "Todos os testes passaram! ✅"
        else
            error "Alguns testes falharam! ❌"
            exit 1
        fi
    fi
}

# Executar função principal
main "$@"
