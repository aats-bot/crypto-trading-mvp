#!/bin/bash
# Script de Deploy - Bot de Trading MVP
# Este script automatiza o processo de deploy para diferentes ambientes

set -e  # Parar em caso de erro

# Configurações
PROJECT_NAME="trading-bot-mvp"
DOCKER_REGISTRY="ghcr.io"
BACKUP_RETENTION_DAYS=7

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
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
    log "Verificando dependências para deploy..."
    
    # Verificar Docker
    if ! command -v docker &> /dev/null; then
        error "Docker não encontrado!"
        exit 1
    fi
    
    # Verificar Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose não encontrado!"
        exit 1
    fi
    
    # Verificar Git
    if ! command -v git &> /dev/null; then
        error "Git não encontrado!"
        exit 1
    fi
    
    # Verificar curl
    if ! command -v curl &> /dev/null; then
        error "curl não encontrado!"
        exit 1
    fi
    
    success "Dependências verificadas"
}

# Função para validar ambiente
validate_environment() {
    local env=$1
    
    log "Validando ambiente: $env"
    
    case $env in
        development|dev)
            export ENVIRONMENT="development"
            export COMPOSE_FILE="docker-compose.yml"
            export ENV_FILE=".env"
            ;;
        staging|stage)
            export ENVIRONMENT="staging"
            export COMPOSE_FILE="docker-compose.staging.yml"
            export ENV_FILE=".env.staging"
            ;;
        production|prod)
            export ENVIRONMENT="production"
            export COMPOSE_FILE="docker-compose.production.yml"
            export ENV_FILE=".env.production"
            ;;
        *)
            error "Ambiente inválido: $env"
            error "Ambientes válidos: development, staging, production"
            exit 1
            ;;
    esac
    
    # Verificar se arquivo de compose existe
    if [ ! -f "$COMPOSE_FILE" ]; then
        error "Arquivo $COMPOSE_FILE não encontrado!"
        exit 1
    fi
    
    # Verificar se arquivo de ambiente existe
    if [ ! -f "$ENV_FILE" ]; then
        warning "Arquivo $ENV_FILE não encontrado - usando variáveis padrão"
    else
        source "$ENV_FILE"
        info "Variáveis carregadas de $ENV_FILE"
    fi
    
    success "Ambiente $ENVIRONMENT validado"
}

# Função para fazer backup
create_backup() {
    local env=$1
    
    log "Criando backup para ambiente $env..."
    
    # Criar diretório de backup
    local backup_dir="backups/$(date +%Y%m%d_%H%M%S)_${env}"
    mkdir -p "$backup_dir"
    
    # Backup do banco de dados
    if docker ps | grep -q "${PROJECT_NAME}_db"; then
        log "Fazendo backup do banco de dados..."
        docker exec "${PROJECT_NAME}_db_1" pg_dump -U postgres trading_bot > "$backup_dir/database.sql"
        success "Backup do banco criado"
    fi
    
    # Backup dos volumes Docker
    if docker volume ls | grep -q "${PROJECT_NAME}"; then
        log "Fazendo backup dos volumes..."
        docker run --rm -v "${PROJECT_NAME}_data:/data" -v "$(pwd)/$backup_dir:/backup" alpine tar czf /backup/volumes.tar.gz -C /data .
        success "Backup dos volumes criado"
    fi
    
    # Backup da configuração atual
    cp "$COMPOSE_FILE" "$backup_dir/"
    cp "$ENV_FILE" "$backup_dir/" 2>/dev/null || true
    
    # Salvar informações do deploy atual
    cat > "$backup_dir/deploy-info.json" << EOF
{
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "environment": "$env",
    "git_commit": "$(git rev-parse HEAD 2>/dev/null || echo 'unknown')",
    "git_branch": "$(git branch --show-current 2>/dev/null || echo 'unknown')",
    "docker_images": $(docker images --format "table {{.Repository}}:{{.Tag}}" | grep "$PROJECT_NAME" | jq -R . | jq -s . 2>/dev/null || echo '[]')
}
EOF
    
    success "Backup criado em $backup_dir"
    echo "$backup_dir" > .last_backup
}

# Função para limpar backups antigos
cleanup_old_backups() {
    log "Limpando backups antigos (>${BACKUP_RETENTION_DAYS} dias)..."
    
    if [ -d "backups" ]; then
        find backups/ -type d -name "*_*" -mtime +${BACKUP_RETENTION_DAYS} -exec rm -rf {} + 2>/dev/null || true
        success "Backups antigos removidos"
    fi
}

# Função para parar serviços gracefully
stop_services() {
    local env=$1
    
    log "Parando serviços do ambiente $env..."
    
    # Parar trading primeiro (graceful shutdown)
    if docker ps | grep -q "${PROJECT_NAME}_api"; then
        log "Parando trading gracefully..."
        docker exec "${PROJECT_NAME}_api_1" python -c "
import requests
try:
    response = requests.post('http://localhost:8000/api/v1/trading/stop', timeout=30)
    print(f'Trading stopped: {response.status_code}')
except Exception as e:
    print(f'Error stopping trading: {e}')
" || warning "Não foi possível parar trading gracefully"
        
        # Aguardar posições serem fechadas
        sleep 30
    fi
    
    # Parar todos os containers
    docker-compose -f "$COMPOSE_FILE" down --timeout 60
    
    success "Serviços parados"
}

# Função para atualizar imagens Docker
update_images() {
    local tag=${1:-latest}
    
    log "Atualizando imagens Docker (tag: $tag)..."
    
    # Pull das novas imagens
    if [ -n "$DOCKER_REGISTRY" ]; then
        docker pull "${DOCKER_REGISTRY}/${PROJECT_NAME}:${tag}"
    else
        docker-compose -f "$COMPOSE_FILE" pull
    fi
    
    success "Imagens atualizadas"
}

# Função para executar migrations
run_migrations() {
    log "Executando migrations do banco de dados..."
    
    # Verificar se Alembic está configurado
    if [ -f "alembic.ini" ]; then
        # Executar migrations usando container temporário
        docker run --rm \
            --network "${PROJECT_NAME}_default" \
            -e DATABASE_URL="$DATABASE_URL" \
            -v "$(pwd):/app" \
            -w /app \
            "${DOCKER_REGISTRY}/${PROJECT_NAME}:latest" \
            python -m alembic upgrade head
        
        success "Migrations executadas"
    else
        warning "Alembic não configurado - pulando migrations"
    fi
}

# Função para iniciar serviços
start_services() {
    log "Iniciando serviços..."
    
    # Iniciar containers
    docker-compose -f "$COMPOSE_FILE" up -d
    
    # Aguardar serviços ficarem prontos
    log "Aguardando serviços ficarem prontos..."
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f http://localhost:8000/health &> /dev/null; then
            success "Serviços iniciados e prontos"
            return 0
        fi
        
        log "Tentativa $attempt/$max_attempts - aguardando..."
        sleep 10
        ((attempt++))
    done
    
    error "Serviços não ficaram prontos no tempo esperado"
    return 1
}

# Função para executar health checks
run_health_checks() {
    log "Executando verificações de saúde..."
    
    local checks_passed=0
    local total_checks=0
    
    # Health check da API
    ((total_checks++))
    if curl -f http://localhost:8000/health &> /dev/null; then
        success "✅ API health check passou"
        ((checks_passed++))
    else
        error "❌ API health check falhou"
    fi
    
    # Health check do banco de dados
    ((total_checks++))
    if docker exec "${PROJECT_NAME}_db_1" pg_isready -U postgres &> /dev/null; then
        success "✅ Database health check passou"
        ((checks_passed++))
    else
        error "❌ Database health check falhou"
    fi
    
    # Health check do Redis
    ((total_checks++))
    if docker exec "${PROJECT_NAME}_redis_1" redis-cli ping &> /dev/null; then
        success "✅ Redis health check passou"
        ((checks_passed++))
    else
        error "❌ Redis health check falhou"
    fi
    
    # Verificar endpoints críticos
    ((total_checks++))
    if curl -f http://localhost:8000/api/v1/status &> /dev/null; then
        success "✅ API status endpoint passou"
        ((checks_passed++))
    else
        error "❌ API status endpoint falhou"
    fi
    
    # Resumo dos health checks
    log "Health checks: $checks_passed/$total_checks passaram"
    
    if [ $checks_passed -eq $total_checks ]; then
        success "Todos os health checks passaram! 🎉"
        return 0
    else
        error "Alguns health checks falharam!"
        return 1
    fi
}

# Função para executar testes de smoke
run_smoke_tests() {
    log "Executando testes de smoke..."
    
    # Testes básicos de funcionalidade
    local tests_passed=0
    local total_tests=0
    
    # Teste 1: API responde
    ((total_tests++))
    if curl -s http://localhost:8000/api/v1/status | grep -q "ok"; then
        success "✅ API responde corretamente"
        ((tests_passed++))
    else
        error "❌ API não responde corretamente"
    fi
    
    # Teste 2: Autenticação funciona
    ((total_tests++))
    if curl -s http://localhost:8000/api/v1/auth/test &> /dev/null; then
        success "✅ Sistema de autenticação funciona"
        ((tests_passed++))
    else
        warning "⚠️  Sistema de autenticação pode ter problemas"
    fi
    
    # Teste 3: Conexão com Bybit
    ((total_tests++))
    if curl -s http://localhost:8000/api/v1/trading/connection-test | grep -q "connected"; then
        success "✅ Conexão com Bybit funciona"
        ((tests_passed++))
    else
        warning "⚠️  Conexão com Bybit pode ter problemas"
    fi
    
    log "Smoke tests: $tests_passed/$total_tests passaram"
    
    if [ $tests_passed -ge $((total_tests - 1)) ]; then
        success "Smoke tests passaram! ✅"
        return 0
    else
        error "Muitos smoke tests falharam!"
        return 1
    fi
}

# Função para rollback
rollback() {
    local backup_dir=$1
    
    error "Executando rollback..."
    
    if [ -z "$backup_dir" ] && [ -f ".last_backup" ]; then
        backup_dir=$(cat .last_backup)
    fi
    
    if [ -z "$backup_dir" ] || [ ! -d "$backup_dir" ]; then
        error "Backup não encontrado para rollback!"
        exit 1
    fi
    
    log "Fazendo rollback usando backup: $backup_dir"
    
    # Parar serviços atuais
    docker-compose -f "$COMPOSE_FILE" down --timeout 30
    
    # Restaurar configuração
    cp "$backup_dir/$COMPOSE_FILE" .
    cp "$backup_dir/$ENV_FILE" . 2>/dev/null || true
    
    # Restaurar banco de dados
    if [ -f "$backup_dir/database.sql" ]; then
        log "Restaurando banco de dados..."
        docker-compose -f "$COMPOSE_FILE" up -d db
        sleep 10
        docker exec -i "${PROJECT_NAME}_db_1" psql -U postgres trading_bot < "$backup_dir/database.sql"
    fi
    
    # Restaurar volumes
    if [ -f "$backup_dir/volumes.tar.gz" ]; then
        log "Restaurando volumes..."
        docker run --rm -v "${PROJECT_NAME}_data:/data" -v "$(pwd)/$backup_dir:/backup" alpine tar xzf /backup/volumes.tar.gz -C /data
    fi
    
    # Iniciar serviços
    docker-compose -f "$COMPOSE_FILE" up -d
    
    success "Rollback concluído!"
}

# Função para monitoramento pós-deploy
post_deploy_monitoring() {
    local duration=${1:-300}  # 5 minutos por padrão
    
    log "Iniciando monitoramento pós-deploy por ${duration}s..."
    
    local start_time=$(date +%s)
    local end_time=$((start_time + duration))
    local check_interval=30
    
    while [ $(date +%s) -lt $end_time ]; do
        local current_time=$(date +%s)
        local elapsed=$((current_time - start_time))
        local remaining=$((end_time - current_time))
        
        log "Monitoramento: ${elapsed}s/${duration}s (${remaining}s restantes)"
        
        # Verificar métricas básicas
        local cpu_usage=$(docker stats --no-stream --format "table {{.CPUPerc}}" | tail -n +2 | head -1 | sed 's/%//')
        local memory_usage=$(docker stats --no-stream --format "table {{.MemPerc}}" | tail -n +2 | head -1 | sed 's/%//')
        
        info "CPU: ${cpu_usage}%, Memória: ${memory_usage}%"
        
        # Verificar se API ainda responde
        if ! curl -f http://localhost:8000/health &> /dev/null; then
            error "API parou de responder durante monitoramento!"
            return 1
        fi
        
        # Verificar logs por erros
        if docker-compose -f "$COMPOSE_FILE" logs --tail=10 | grep -i "error\|exception\|failed" &> /dev/null; then
            warning "Erros detectados nos logs"
        fi
        
        sleep $check_interval
    done
    
    success "Monitoramento pós-deploy concluído - Sistema estável! ✅"
}

# Função para mostrar ajuda
show_help() {
    echo "Uso: $0 <ambiente> [opções]"
    echo ""
    echo "Ambientes:"
    echo "  development, dev     Deploy para desenvolvimento"
    echo "  staging, stage       Deploy para staging"
    echo "  production, prod     Deploy para produção"
    echo ""
    echo "Opções:"
    echo "  --tag TAG           Tag da imagem Docker (padrão: latest)"
    echo "  --no-backup         Não criar backup antes do deploy"
    echo "  --no-tests          Pular testes de smoke"
    echo "  --no-monitoring     Pular monitoramento pós-deploy"
    echo "  --rollback [DIR]    Fazer rollback usando backup"
    echo "  --force             Forçar deploy mesmo com falhas"
    echo "  --dry-run           Simular deploy sem executar"
    echo "  -h, --help          Mostrar esta ajuda"
    echo ""
    echo "Exemplos:"
    echo "  $0 staging                    # Deploy para staging"
    echo "  $0 production --tag v1.2.3    # Deploy para produção com tag específica"
    echo "  $0 staging --rollback         # Rollback no staging"
}

# Função principal
main() {
    local environment=""
    local docker_tag="latest"
    local create_backup=true
    local run_tests=true
    local run_monitoring=true
    local force_deploy=false
    local dry_run=false
    local do_rollback=false
    local rollback_dir=""
    
    # Processar argumentos
    while [[ $# -gt 0 ]]; do
        case $1 in
            development|dev|staging|stage|production|prod)
                environment=$1
                shift
                ;;
            --tag)
                docker_tag=$2
                shift 2
                ;;
            --no-backup)
                create_backup=false
                shift
                ;;
            --no-tests)
                run_tests=false
                shift
                ;;
            --no-monitoring)
                run_monitoring=false
                shift
                ;;
            --rollback)
                do_rollback=true
                rollback_dir=$2
                shift 2
                ;;
            --force)
                force_deploy=true
                shift
                ;;
            --dry-run)
                dry_run=true
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
    
    # Verificar se ambiente foi especificado
    if [ -z "$environment" ] && [ "$do_rollback" = false ]; then
        error "Ambiente deve ser especificado!"
        show_help
        exit 1
    fi
    
    log "Iniciando deploy do $PROJECT_NAME..."
    
    # Verificar dependências
    check_dependencies
    
    # Executar rollback se solicitado
    if [ "$do_rollback" = true ]; then
        rollback "$rollback_dir"
        exit 0
    fi
    
    # Validar ambiente
    validate_environment "$environment"
    
    # Dry run
    if [ "$dry_run" = true ]; then
        log "🔍 DRY RUN - Simulando deploy para $ENVIRONMENT"
        log "  - Arquivo compose: $COMPOSE_FILE"
        log "  - Arquivo env: $ENV_FILE"
        log "  - Tag Docker: $docker_tag"
        log "  - Backup: $create_backup"
        log "  - Testes: $run_tests"
        log "  - Monitoramento: $run_monitoring"
        success "Dry run concluído - configuração válida!"
        exit 0
    fi
    
    # Executar deploy
    log "🚀 Executando deploy para $ENVIRONMENT..."
    
    # Criar backup
    if [ "$create_backup" = true ]; then
        create_backup "$ENVIRONMENT"
    fi
    
    # Parar serviços
    stop_services "$ENVIRONMENT"
    
    # Atualizar imagens
    update_images "$docker_tag"
    
    # Executar migrations
    run_migrations
    
    # Iniciar serviços
    if ! start_services; then
        if [ "$force_deploy" = false ]; then
            error "Falha ao iniciar serviços - executando rollback..."
            rollback
            exit 1
        else
            warning "Falha ao iniciar serviços - continuando devido ao --force"
        fi
    fi
    
    # Health checks
    if ! run_health_checks; then
        if [ "$force_deploy" = false ]; then
            error "Health checks falharam - executando rollback..."
            rollback
            exit 1
        else
            warning "Health checks falharam - continuando devido ao --force"
        fi
    fi
    
    # Smoke tests
    if [ "$run_tests" = true ]; then
        if ! run_smoke_tests; then
            if [ "$force_deploy" = false ]; then
                error "Smoke tests falharam - executando rollback..."
                rollback
                exit 1
            else
                warning "Smoke tests falharam - continuando devido ao --force"
            fi
        fi
    fi
    
    # Monitoramento pós-deploy
    if [ "$run_monitoring" = true ]; then
        post_deploy_monitoring 300  # 5 minutos
    fi
    
    # Limpeza
    cleanup_old_backups
    
    success "Deploy para $ENVIRONMENT concluído com sucesso! 🎉"
    
    # Mostrar resumo
    echo ""
    log "📊 Resumo do Deploy:"
    echo "  - Ambiente: $ENVIRONMENT"
    echo "  - Tag: $docker_tag"
    echo "  - Backup: $([ "$create_backup" = true ] && echo "Criado" || echo "Pulado")"
    echo "  - URL: http://localhost:8000"
    echo "  - Dashboard: http://localhost:8501"
    echo ""
    info "Para verificar logs: docker-compose -f $COMPOSE_FILE logs -f"
    info "Para verificar status: docker-compose -f $COMPOSE_FILE ps"
}

# Executar função principal
main "$@"
