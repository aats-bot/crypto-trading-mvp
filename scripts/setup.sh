#!/bin/bash
# 🛠️ Script de Setup Inicial - MVP Bot de Trading
# Localização: /scripts/setup.sh

set -e  # Parar em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configurações
PROJECT_NAME="crypto-trading-mvp"
PYTHON_VERSION="3.11"
NODE_VERSION="20"

# Função para logging
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] ✅${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] ⚠️${NC} $1"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ❌${NC} $1"
}

# Detectar sistema operacional
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [ -f /etc/debian_version ]; then
            OS="debian"
        elif [ -f /etc/redhat-release ]; then
            OS="redhat"
        else
            OS="linux"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    else
        OS="unknown"
    fi
    
    log "Sistema operacional detectado: $OS"
}

# Instalar Docker
install_docker() {
    log "🐳 Instalando Docker..."
    
    if command -v docker &> /dev/null; then
        log_success "Docker já está instalado"
        return
    fi
    
    case $OS in
        debian)
            # Ubuntu/Debian
            sudo apt-get update
            sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release
            curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
            echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
            sudo apt-get update
            sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
            ;;
        redhat)
            # CentOS/RHEL/Fedora
            sudo yum install -y yum-utils
            sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
            sudo yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
            sudo systemctl start docker
            sudo systemctl enable docker
            ;;
        macos)
            log_warning "Por favor, instale Docker Desktop manualmente: https://docs.docker.com/desktop/mac/install/"
            return
            ;;
        *)
            log_error "Sistema operacional não suportado para instalação automática do Docker"
            return
            ;;
    esac
    
    # Adicionar usuário ao grupo docker
    sudo usermod -aG docker $USER
    
    log_success "Docker instalado com sucesso"
    log_warning "Você precisa fazer logout/login para usar Docker sem sudo"
}

# Instalar Docker Compose
install_docker_compose() {
    log "🐙 Verificando Docker Compose..."
    
    if docker compose version &> /dev/null; then
        log_success "Docker Compose (plugin) já está disponível"
        return
    fi
    
    if command -v docker-compose &> /dev/null; then
        log_success "Docker Compose (standalone) já está instalado"
        return
    fi
    
    log "Instalando Docker Compose..."
    
    # Instalar versão standalone
    DOCKER_COMPOSE_VERSION="2.20.2"
    sudo curl -L "https://github.com/docker/compose/releases/download/v${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    
    log_success "Docker Compose instalado"
}

# Instalar Python
install_python() {
    log "🐍 Verificando Python..."
    
    if command -v python3 &> /dev/null; then
        CURRENT_PYTHON=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
        log_success "Python $CURRENT_PYTHON já está instalado"
        return
    fi
    
    log "Instalando Python $PYTHON_VERSION..."
    
    case $OS in
        debian)
            sudo apt-get update
            sudo apt-get install -y python3 python3-pip python3-venv python3-dev
            ;;
        redhat)
            sudo yum install -y python3 python3-pip python3-venv python3-devel
            ;;
        macos)
            if command -v brew &> /dev/null; then
                brew install python@$PYTHON_VERSION
            else
                log_warning "Homebrew não encontrado. Instale Python manualmente."
            fi
            ;;
        *)
            log_error "Sistema operacional não suportado para instalação automática do Python"
            return
            ;;
    esac
    
    log_success "Python instalado"
}

# Configurar ambiente virtual Python
setup_python_env() {
    log "🔧 Configurando ambiente virtual Python..."
    
    # Criar ambiente virtual
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        log_success "Ambiente virtual criado"
    else
        log_success "Ambiente virtual já existe"
    fi
    
    # Ativar ambiente virtual
    source venv/bin/activate
    
    # Atualizar pip
    pip install --upgrade pip
    
    # Instalar dependências
    if [ -f "requirements.txt" ]; then
        log "📦 Instalando dependências Python..."
        pip install -r requirements.txt
        log_success "Dependências Python instaladas"
    else
        log_warning "Arquivo requirements.txt não encontrado"
    fi
}

# Instalar Node.js (opcional)
install_nodejs() {
    if [ "$INSTALL_NODE" != true ]; then
        return
    fi
    
    log "📦 Verificando Node.js..."
    
    if command -v node &> /dev/null; then
        CURRENT_NODE=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
        log_success "Node.js v$CURRENT_NODE já está instalado"
        return
    fi
    
    log "Instalando Node.js $NODE_VERSION..."
    
    case $OS in
        debian)
            curl -fsSL https://deb.nodesource.com/setup_${NODE_VERSION}.x | sudo -E bash -
            sudo apt-get install -y nodejs
            ;;
        redhat)
            curl -fsSL https://rpm.nodesource.com/setup_${NODE_VERSION}.x | sudo bash -
            sudo yum install -y nodejs
            ;;
        macos)
            if command -v brew &> /dev/null; then
                brew install node@$NODE_VERSION
            else
                log_warning "Homebrew não encontrado. Instale Node.js manualmente."
            fi
            ;;
        *)
            log_error "Sistema operacional não suportado para instalação automática do Node.js"
            return
            ;;
    esac
    
    log_success "Node.js instalado"
}

# Configurar banco de dados
setup_database() {
    log "🗄️ Configurando banco de dados..."
    
    # Criar diretórios necessários
    mkdir -p data/database data/backups logs
    
    # Configurar permissões
    chmod 755 data/database data/backups logs
    
    log_success "Estrutura de banco configurada"
}

# Configurar arquivos de ambiente
setup_env_files() {
    log "⚙️ Configurando arquivos de ambiente..."
    
    # Copiar .env.example para .env se não existir
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            log_success "Arquivo .env criado a partir do .env.example"
            log_warning "Por favor, edite o arquivo .env com suas configurações"
        else
            log_error "Arquivo .env.example não encontrado"
        fi
    else
        log_success "Arquivo .env já existe"
    fi
}

# Configurar Git hooks
setup_git_hooks() {
    if [ "$SETUP_GIT_HOOKS" != true ]; then
        return
    fi
    
    log "🔗 Configurando Git hooks..."
    
    # Criar diretório de hooks se não existir
    mkdir -p .git/hooks
    
    # Pre-commit hook
    cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Pre-commit hook para verificações de qualidade

echo "🔍 Executando verificações pre-commit..."

# Verificar se há arquivos Python
if git diff --cached --name-only | grep -q '\.py$'; then
    echo "📝 Verificando código Python..."
    
    # Verificar sintaxe Python
    for file in $(git diff --cached --name-only | grep '\.py$'); do
        if [ -f "$file" ]; then
            python3 -m py_compile "$file"
            if [ $? -ne 0 ]; then
                echo "❌ Erro de sintaxe em $file"
                exit 1
            fi
        fi
    done
    
    echo "✅ Verificações Python concluídas"
fi

# Verificar se há arquivos grandes
for file in $(git diff --cached --name-only); do
    if [ -f "$file" ]; then
        size=$(wc -c < "$file")
        if [ $size -gt 1048576 ]; then  # 1MB
            echo "⚠️ Arquivo grande detectado: $file ($(($size / 1024))KB)"
            echo "Considere usar Git LFS para arquivos grandes"
        fi
    fi
done

echo "✅ Verificações pre-commit concluídas"
EOF
    
    chmod +x .git/hooks/pre-commit
    log_success "Git hooks configurados"
}

# Executar testes iniciais
run_initial_tests() {
    log "🧪 Executando testes iniciais..."
    
    # Testar importações Python
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        
        # Testar importações básicas
        python3 -c "
import sys
print(f'Python version: {sys.version}')

try:
    import fastapi
    print('✅ FastAPI importado com sucesso')
except ImportError:
    print('❌ Erro ao importar FastAPI')

try:
    import streamlit
    print('✅ Streamlit importado com sucesso')
except ImportError:
    print('❌ Erro ao importar Streamlit')

try:
    import pandas
    print('✅ Pandas importado com sucesso')
except ImportError:
    print('❌ Erro ao importar Pandas')
"
    fi
    
    # Testar Docker
    if command -v docker &> /dev/null; then
        docker --version
        log_success "Docker funcional"
    fi
    
    # Testar Docker Compose
    if command -v docker-compose &> /dev/null; then
        docker-compose --version
        log_success "Docker Compose funcional"
    elif docker compose version &> /dev/null; then
        docker compose version
        log_success "Docker Compose (plugin) funcional"
    fi
    
    log_success "Testes iniciais concluídos"
}

# Mostrar resumo final
show_summary() {
    echo
    echo "🎉 ====================================="
    echo "   Setup Concluído com Sucesso!"
    echo "===================================== 🎉"
    echo
    echo "📋 Próximos passos:"
    echo
    echo "1. 📝 Editar arquivo .env com suas configurações:"
    echo "   nano .env"
    echo
    echo "2. 🚀 Fazer primeiro deploy:"
    echo "   ./scripts/deploy.sh development"
    echo
    echo "3. 🌐 Acessar aplicação:"
    echo "   • API:       http://localhost:8000"
    echo "   • Dashboard: http://localhost:8501"
    echo "   • Docs:      http://localhost:8000/docs"
    echo
    echo "4. 📊 Verificar saúde dos serviços:"
    echo "   ./scripts/deploy.sh --health-check"
    echo
    echo "5. 📋 Ver logs:"
    echo "   ./scripts/deploy.sh --logs"
    echo
    if [ "$OS" != "macos" ] && [ "$DOCKER_INSTALLED" = true ]; then
        echo "⚠️  IMPORTANTE: Faça logout/login para usar Docker sem sudo"
        echo
    fi
}

# Função de ajuda
show_help() {
    cat << EOF
🛠️ Script de Setup - MVP Bot de Trading

USAGE:
    ./scripts/setup.sh [OPTIONS]

OPTIONS:
    --prod              Setup para produção (instala dependências extras)
    --docker-only       Instalar apenas Docker e Docker Compose
    --python-only       Configurar apenas ambiente Python
    --node              Instalar Node.js também
    --git-hooks         Configurar Git hooks
    --force             Forçar reinstalação de componentes
    --help              Mostrar esta ajuda

EXAMPLES:
    ./scripts/setup.sh                    # Setup completo para desenvolvimento
    ./scripts/setup.sh --prod             # Setup para produção
    ./scripts/setup.sh --docker-only      # Apenas Docker
    ./scripts/setup.sh --python-only      # Apenas Python
    ./scripts/setup.sh --node --git-hooks # Com Node.js e Git hooks

EOF
}

# Função principal
main() {
    # Valores padrão
    PRODUCTION=false
    DOCKER_ONLY=false
    PYTHON_ONLY=false
    INSTALL_NODE=false
    SETUP_GIT_HOOKS=false
    FORCE=false
    DOCKER_INSTALLED=false
    
    # Processar argumentos
    while [[ $# -gt 0 ]]; do
        case $1 in
            --prod)
                PRODUCTION=true
                shift
                ;;
            --docker-only)
                DOCKER_ONLY=true
                shift
                ;;
            --python-only)
                PYTHON_ONLY=true
                shift
                ;;
            --node)
                INSTALL_NODE=true
                shift
                ;;
            --git-hooks)
                SETUP_GIT_HOOKS=true
                shift
                ;;
            --force)
                FORCE=true
                shift
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                log_error "Opção desconhecida: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # Banner
    echo
    echo "🛠️ ====================================="
    echo "   MVP Bot de Trading - Setup Script"
    echo "===================================== 🛠️"
    echo
    
    # Detectar sistema operacional
    detect_os
    
    # Executar setup baseado nas opções
    if [ "$DOCKER_ONLY" = true ]; then
        install_docker
        install_docker_compose
        DOCKER_INSTALLED=true
    elif [ "$PYTHON_ONLY" = true ]; then
        install_python
        setup_python_env
    else
        # Setup completo
        install_docker
        install_docker_compose
        DOCKER_INSTALLED=true
        
        install_python
        setup_python_env
        
        install_nodejs
        
        setup_database
        setup_env_files
        setup_git_hooks
        
        run_initial_tests
    fi
    
    # Mostrar resumo
    show_summary
}

# Executar função principal
main "$@"

