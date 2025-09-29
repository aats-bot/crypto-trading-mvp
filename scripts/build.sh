#!/bin/bash
# Script de Build - Bot de Trading MVP
# Este script automatiza o processo de build da aplicação

set -e  # Parar em caso de erro

# Configurações
PROJECT_NAME="trading-bot-mvp"
PYTHON_VERSION="3.11"
NODE_VERSION="18"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

# Função para verificar dependências
check_dependencies() {
    log "Verificando dependências do sistema..."
    
    # Verificar Python
    if command -v python3 &> /dev/null; then
        PYTHON_VER=$(python3 --version | cut -d' ' -f2)
        success "Python encontrado: $PYTHON_VER"
    else
        error "Python 3 não encontrado!"
        exit 1
    fi
    
    # Verificar pip
    if command -v pip3 &> /dev/null; then
        success "pip3 encontrado"
    else
        error "pip3 não encontrado!"
        exit 1
    fi
    
    # Verificar Docker (opcional)
    if command -v docker &> /dev/null; then
        success "Docker encontrado"
        DOCKER_AVAILABLE=true
    else
        warning "Docker não encontrado - build de containers será pulado"
        DOCKER_AVAILABLE=false
    fi
    
    # Verificar Node.js (se houver frontend)
    if [ -f "package.json" ]; then
        if command -v node &> /dev/null; then
            NODE_VER=$(node --version)
            success "Node.js encontrado: $NODE_VER"
        else
            error "Node.js necessário mas não encontrado!"
            exit 1
        fi
    fi
}

# Função para limpar build anterior
clean_build() {
    log "Limpando build anterior..."
    
    # Remover cache Python
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    
    # Remover diretórios de build
    rm -rf build/ dist/ *.egg-info/ .coverage htmlcov/ .pytest_cache/
    
    # Remover node_modules se existir
    if [ -d "node_modules" ]; then
        rm -rf node_modules/
    fi
    
    success "Limpeza concluída"
}

# Função para instalar dependências Python
install_python_deps() {
    log "Instalando dependências Python..."
    
    # Criar ambiente virtual se não existir
    if [ ! -d "venv" ]; then
        log "Criando ambiente virtual..."
        python3 -m venv venv
    fi
    
    # Ativar ambiente virtual
    source venv/bin/activate
    
    # Atualizar pip
    pip install --upgrade pip
    
    # Instalar dependências de produção
    if [ -f "requirements.txt" ]; then
        log "Instalando requirements.txt..."
        pip install -r requirements.txt
    fi
    
    # Instalar dependências de desenvolvimento
    if [ -f "requirements-dev.txt" ]; then
        log "Instalando requirements-dev.txt..."
        pip install -r requirements-dev.txt
    fi
    
    # Instalar dependências de teste
    if [ -f "requirements-test.txt" ]; then
        log "Instalando requirements-test.txt..."
        pip install -r requirements-test.txt
    fi
    
    success "Dependências Python instaladas"
}

# Função para instalar dependências Node.js
install_node_deps() {
    if [ -f "package.json" ]; then
        log "Instalando dependências Node.js..."
        
        if command -v npm &> /dev/null; then
            npm ci
        elif command -v yarn &> /dev/null; then
            yarn install --frozen-lockfile
        else
            error "npm ou yarn necessário para instalar dependências Node.js"
            exit 1
        fi
        
        success "Dependências Node.js instaladas"
    fi
}

# Função para executar linting
run_linting() {
    log "Executando verificações de código..."
    
    source venv/bin/activate
    
    # Black (formatação)
    if command -v black &> /dev/null; then
        log "Executando Black..."
        black --check . || {
            warning "Código não está formatado corretamente"
            log "Execute: black . para corrigir"
        }
    fi
    
    # isort (imports)
    if command -v isort &> /dev/null; then
        log "Executando isort..."
        isort --check-only . || {
            warning "Imports não estão organizados"
            log "Execute: isort . para corrigir"
        }
    fi
    
    # Flake8 (linting)
    if command -v flake8 &> /dev/null; then
        log "Executando Flake8..."
        flake8 . --count --statistics
    fi
    
    # MyPy (type checking)
    if command -v mypy &> /dev/null; then
        log "Executando MyPy..."
        mypy . --ignore-missing-imports || warning "Problemas de tipagem encontrados"
    fi
    
    success "Verificações de código concluídas"
}

# Função para executar testes
run_tests() {
    log "Executando testes..."
    
    source venv/bin/activate
    
    if command -v pytest &> /dev/null; then
        # Executar testes com cobertura
        pytest tests/ -v --cov=. --cov-report=html --cov-report=term-missing
        
        # Verificar cobertura mínima
        coverage report --fail-under=70 || {
            warning "Cobertura de testes abaixo de 70%"
        }
    else
        warning "pytest não encontrado - pulando testes"
    fi
    
    success "Testes concluídos"
}

# Função para build da aplicação
build_application() {
    log "Fazendo build da aplicação..."
    
    source venv/bin/activate
    
    # Build do frontend se existir
    if [ -f "package.json" ]; then
        log "Fazendo build do frontend..."
        if command -v npm &> /dev/null; then
            npm run build
        elif command -v yarn &> /dev/null; then
            yarn build
        fi
    fi
    
    # Criar distribuição Python se houver setup.py
    if [ -f "setup.py" ]; then
        log "Criando distribuição Python..."
        python setup.py sdist bdist_wheel
    fi
    
    # Gerar requirements.txt atualizado
    log "Gerando requirements.txt atualizado..."
    pip freeze > requirements-frozen.txt
    
    success "Build da aplicação concluído"
}

# Função para build Docker
build_docker() {
    if [ "$DOCKER_AVAILABLE" = true ]; then
        log "Fazendo build da imagem Docker..."
        
        # Build da imagem principal
        docker build -t ${PROJECT_NAME}:latest .
        
        # Build da imagem de desenvolvimento se houver Dockerfile.dev
        if [ -f "Dockerfile.dev" ]; then
            docker build -f Dockerfile.dev -t ${PROJECT_NAME}:dev .
        fi
        
        # Verificar tamanho da imagem
        IMAGE_SIZE=$(docker images ${PROJECT_NAME}:latest --format "table {{.Size}}" | tail -n 1)
        log "Tamanho da imagem: $IMAGE_SIZE"
        
        success "Build Docker concluído"
    fi
}

# Função para gerar artefatos
generate_artifacts() {
    log "Gerando artefatos de build..."
    
    # Criar diretório de artefatos
    mkdir -p artifacts/
    
    # Copiar arquivos importantes
    cp requirements*.txt artifacts/ 2>/dev/null || true
    cp *.yml *.yaml artifacts/ 2>/dev/null || true
    
    # Gerar informações de build
    cat > artifacts/build-info.json << EOF
{
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "git_commit": "$(git rev-parse HEAD 2>/dev/null || echo 'unknown')",
    "git_branch": "$(git branch --show-current 2>/dev/null || echo 'unknown')",
    "python_version": "$(python3 --version)",
    "build_number": "${BUILD_NUMBER:-local}",
    "environment": "${ENVIRONMENT:-development}"
}
EOF
    
    # Gerar checksums
    if command -v sha256sum &> /dev/null; then
        find artifacts/ -type f -exec sha256sum {} \; > artifacts/checksums.txt
    fi
    
    success "Artefatos gerados em artifacts/"
}

# Função para verificar qualidade
quality_checks() {
    log "Executando verificações de qualidade..."
    
    source venv/bin/activate
    
    # Verificar segurança com bandit
    if command -v bandit &> /dev/null; then
        log "Executando verificação de segurança..."
        bandit -r . -f json -o artifacts/security-report.json || warning "Problemas de segurança encontrados"
    fi
    
    # Verificar vulnerabilidades em dependências
    if command -v safety &> /dev/null; then
        log "Verificando vulnerabilidades em dependências..."
        safety check --json --output artifacts/safety-report.json || warning "Vulnerabilidades encontradas"
    fi
    
    success "Verificações de qualidade concluídas"
}

# Função principal
main() {
    log "Iniciando build do $PROJECT_NAME..."
    
    # Verificar se estamos no diretório correto
    if [ ! -f "requirements.txt" ] && [ ! -f "pyproject.toml" ] && [ ! -f "setup.py" ]; then
        error "Não parece ser um projeto Python válido"
        exit 1
    fi
    
    # Executar etapas do build
    check_dependencies
    clean_build
    install_python_deps
    install_node_deps
    run_linting
    run_tests
    build_application
    build_docker
    generate_artifacts
    quality_checks
    
    success "Build concluído com sucesso! 🎉"
    
    # Mostrar resumo
    echo ""
    log "📊 Resumo do Build:"
    echo "  - Artefatos: artifacts/"
    echo "  - Logs de teste: htmlcov/"
    if [ "$DOCKER_AVAILABLE" = true ]; then
        echo "  - Imagem Docker: ${PROJECT_NAME}:latest"
    fi
    echo ""
}

# Executar função principal
main "$@"
