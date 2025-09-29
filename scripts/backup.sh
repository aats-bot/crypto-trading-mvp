#!/bin/bash
# 💾 Script de Backup Completo - MVP Bot de Trading
# Localização: /scripts/backup.sh

set -e  # Parar em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configurações
PROJECT_NAME="crypto-trading-mvp"
BACKUP_DIR="./data/backups"
LOG_DIR="./logs"
RETENTION_DAYS=30
COMPRESSION_LEVEL=6

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

# Função de ajuda
show_help() {
    cat << EOF
💾 Script de Backup - MVP Bot de Trading

USAGE:
    ./scripts/backup.sh [OPTIONS]

OPTIONS:
    --full              Backup completo (padrão)
    --database-only     Apenas backup do banco de dados
    --files-only        Apenas backup de arquivos
    --config-only       Apenas backup de configurações
    --logs-only         Apenas backup de logs
    --encrypt           Criptografar backup com GPG
    --remote            Enviar backup para armazenamento remoto
    --list              Listar backups existentes
    --restore FILE      Restaurar backup específico
    --cleanup           Limpar backups antigos
    --verify FILE       Verificar integridade do backup
    --help              Mostrar esta ajuda

EXAMPLES:
    ./scripts/backup.sh                    # Backup completo
    ./scripts/backup.sh --database-only    # Apenas banco
    ./scripts/backup.sh --encrypt --remote # Backup criptografado e remoto
    ./scripts/backup.sh --list             # Listar backups
    ./scripts/backup.sh --restore backup.tar.gz
    ./scripts/backup.sh --cleanup          # Limpar antigos

EOF
}

# Criar diretórios necessários
create_directories() {
    mkdir -p "$BACKUP_DIR" "$LOG_DIR"
    chmod 755 "$BACKUP_DIR" "$LOG_DIR"
}

# Verificar pré-requisitos
check_prerequisites() {
    log "🔍 Verificando pré-requisitos..."
    
    # Verificar Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker não está instalado"
        exit 1
    fi
    
    # Verificar Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose não está instalado"
        exit 1
    fi
    
    # Verificar espaço em disco
    AVAILABLE_SPACE=$(df "$BACKUP_DIR" | awk 'NR==2 {print $4}')
    if [ "$AVAILABLE_SPACE" -lt 1048576 ]; then  # 1GB em KB
        log_warning "Pouco espaço em disco disponível: $(($AVAILABLE_SPACE / 1024))MB"
    fi
    
    log_success "Pré-requisitos verificados"
}

# Backup do banco de dados
backup_database() {
    log "🗄️ Fazendo backup do banco de dados..."
    
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local db_backup_file="$BACKUP_DIR/db_backup_$timestamp.sql"
    
    # Verificar se PostgreSQL está rodando
    if command -v docker-compose &> /dev/null; then
        if ! docker-compose ps postgres | grep -q "Up"; then
            log_warning "PostgreSQL não está rodando, pulando backup do banco"
            return
        fi
        
        # Fazer backup
        docker-compose exec -T postgres pg_dump -U postgres trading_bot > "$db_backup_file"
    else
        if ! docker compose ps postgres | grep -q "Up"; then
            log_warning "PostgreSQL não está rodando, pulando backup do banco"
            return
        fi
        
        # Fazer backup
        docker compose exec -T postgres pg_dump -U postgres trading_bot > "$db_backup_file"
    fi
    
    # Comprimir backup
    gzip "$db_backup_file"
    
    log_success "Backup do banco criado: ${db_backup_file}.gz"
    echo "$db_backup_file.gz"
}

# Backup de arquivos
backup_files() {
    log "📁 Fazendo backup de arquivos..."
    
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local files_backup="$BACKUP_DIR/files_backup_$timestamp.tar.gz"
    
    # Criar backup dos arquivos importantes
    tar -czf "$files_backup" \
        --exclude="$BACKUP_DIR" \
        --exclude="$LOG_DIR" \
        --exclude='.git' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='venv' \
        --exclude='node_modules' \
        --exclude='.pytest_cache' \
        src/ config/ docker/ scripts/ requirements.txt .env 2>/dev/null || true
    
    log_success "Backup de arquivos criado: $files_backup"
    echo "$files_backup"
}

# Backup de configurações
backup_config() {
    log "⚙️ Fazendo backup de configurações..."
    
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local config_backup="$BACKUP_DIR/config_backup_$timestamp.tar.gz"
    
    # Backup apenas das configurações
    tar -czf "$config_backup" \
        config/ \
        docker/ \
        .env \
        docker-compose.yml \
        requirements.txt 2>/dev/null || true
    
    log_success "Backup de configurações criado: $config_backup"
    echo "$config_backup"
}

# Backup de logs
backup_logs() {
    log "📋 Fazendo backup de logs..."
    
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local logs_backup="$BACKUP_DIR/logs_backup_$timestamp.tar.gz"
    
    if [ -d "$LOG_DIR" ] && [ "$(ls -A $LOG_DIR)" ]; then
        tar -czf "$logs_backup" "$LOG_DIR" 2>/dev/null || true
        log_success "Backup de logs criado: $logs_backup"
        echo "$logs_backup"
    else
        log_warning "Diretório de logs vazio, pulando backup"
    fi
}

# Backup completo
backup_full() {
    log "🎯 Fazendo backup completo..."
    
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local full_backup="$BACKUP_DIR/full_backup_$timestamp.tar.gz"
    local temp_dir="/tmp/backup_$timestamp"
    
    # Criar diretório temporário
    mkdir -p "$temp_dir"
    
    # Backup do banco de dados
    local db_backup=$(backup_database)
    if [ -n "$db_backup" ]; then
        cp "$db_backup" "$temp_dir/"
    fi
    
    # Backup de arquivos
    tar -czf "$temp_dir/files.tar.gz" \
        --exclude="$BACKUP_DIR" \
        --exclude="$LOG_DIR" \
        --exclude='.git' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='venv' \
        --exclude='node_modules' \
        --exclude='.pytest_cache' \
        . 2>/dev/null || true
    
    # Criar backup final
    tar -czf "$full_backup" -C "$temp_dir" . 2>/dev/null || true
    
    # Limpar diretório temporário
    rm -rf "$temp_dir"
    
    log_success "Backup completo criado: $full_backup"
    echo "$full_backup"
}

# Criptografar backup
encrypt_backup() {
    local backup_file=$1
    
    if [ -z "$backup_file" ] || [ ! -f "$backup_file" ]; then
        log_error "Arquivo de backup não encontrado: $backup_file"
        return 1
    fi
    
    log "🔐 Criptografando backup..."
    
    # Verificar se GPG está disponível
    if ! command -v gpg &> /dev/null; then
        log_error "GPG não está instalado"
        return 1
    fi
    
    # Criptografar arquivo
    local encrypted_file="${backup_file}.gpg"
    gpg --symmetric --cipher-algo AES256 --compress-algo 2 --s2k-mode 3 \
        --s2k-digest-algo SHA512 --s2k-count 65536 \
        --output "$encrypted_file" "$backup_file"
    
    # Remover arquivo original
    rm "$backup_file"
    
    log_success "Backup criptografado: $encrypted_file"
    echo "$encrypted_file"
}

# Enviar backup para armazenamento remoto
upload_remote() {
    local backup_file=$1
    
    if [ -z "$backup_file" ] || [ ! -f "$backup_file" ]; then
        log_error "Arquivo de backup não encontrado: $backup_file"
        return 1
    fi
    
    log "☁️ Enviando backup para armazenamento remoto..."
    
    # Verificar configurações de remote
    if [ -z "$REMOTE_HOST" ] && [ -z "$AWS_S3_BUCKET" ] && [ -z "$FTP_HOST" ]; then
        log_warning "Nenhuma configuração de armazenamento remoto encontrada"
        log_warning "Configure REMOTE_HOST, AWS_S3_BUCKET ou FTP_HOST no .env"
        return 1
    fi
    
    # Upload via SCP/SSH
    if [ -n "$REMOTE_HOST" ]; then
        log "📤 Enviando via SCP para $REMOTE_HOST..."
        scp "$backup_file" "$REMOTE_USER@$REMOTE_HOST:$REMOTE_PATH/" || {
            log_error "Falha no upload via SCP"
            return 1
        }
        log_success "Upload via SCP concluído"
    fi
    
    # Upload via AWS S3
    if [ -n "$AWS_S3_BUCKET" ] && command -v aws &> /dev/null; then
        log "📤 Enviando para AWS S3: $AWS_S3_BUCKET..."
        aws s3 cp "$backup_file" "s3://$AWS_S3_BUCKET/backups/" || {
            log_error "Falha no upload para S3"
            return 1
        }
        log_success "Upload para S3 concluído"
    fi
    
    # Upload via FTP
    if [ -n "$FTP_HOST" ] && command -v ftp &> /dev/null; then
        log "📤 Enviando via FTP para $FTP_HOST..."
        ftp -n "$FTP_HOST" << EOF
user $FTP_USER $FTP_PASS
binary
put $backup_file
quit
EOF
        log_success "Upload via FTP concluído"
    fi
}

# Listar backups
list_backups() {
    log "📋 Listando backups existentes..."
    
    if [ ! -d "$BACKUP_DIR" ] || [ -z "$(ls -A $BACKUP_DIR)" ]; then
        log_warning "Nenhum backup encontrado"
        return
    fi
    
    echo
    echo "📁 Backups locais:"
    echo "=================="
    
    for backup in "$BACKUP_DIR"/*.{tar.gz,sql.gz,gpg} 2>/dev/null; do
        if [ -f "$backup" ]; then
            local size=$(du -h "$backup" | cut -f1)
            local date=$(stat -c %y "$backup" | cut -d' ' -f1,2 | cut -d'.' -f1)
            local name=$(basename "$backup")
            printf "%-40s %8s %s\n" "$name" "$size" "$date"
        fi
    done
    
    echo
}

# Restaurar backup
restore_backup() {
    local backup_file=$1
    
    if [ -z "$backup_file" ]; then
        log_error "Nome do arquivo de backup não especificado"
        exit 1
    fi
    
    # Verificar se arquivo existe
    if [ ! -f "$BACKUP_DIR/$backup_file" ] && [ ! -f "$backup_file" ]; then
        log_error "Arquivo de backup não encontrado: $backup_file"
        exit 1
    fi
    
    # Usar caminho completo se necessário
    if [ ! -f "$backup_file" ]; then
        backup_file="$BACKUP_DIR/$backup_file"
    fi
    
    log "🔄 Restaurando backup: $backup_file"
    
    # Confirmar ação
    echo
    log_warning "Esta operação irá sobrescrever dados existentes!"
    read -p "Deseja continuar? (y/N): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log "Operação cancelada pelo usuário"
        exit 0
    fi
    
    # Parar serviços
    log "⏹️ Parando serviços..."
    if command -v docker-compose &> /dev/null; then
        docker-compose down || true
    else
        docker compose down || true
    fi
    
    # Descriptografar se necessário
    if [[ "$backup_file" == *.gpg ]]; then
        log "🔓 Descriptografando backup..."
        local decrypted_file="${backup_file%.gpg}"
        gpg --decrypt "$backup_file" > "$decrypted_file"
        backup_file="$decrypted_file"
    fi
    
    # Restaurar baseado no tipo de backup
    if [[ "$backup_file" == *"db_backup"* ]]; then
        # Restaurar apenas banco de dados
        log "🗄️ Restaurando banco de dados..."
        
        # Iniciar apenas PostgreSQL
        if command -v docker-compose &> /dev/null; then
            docker-compose up -d postgres
        else
            docker compose up -d postgres
        fi
        
        sleep 10  # Aguardar inicialização
        
        # Restaurar banco
        if [[ "$backup_file" == *.gz ]]; then
            zcat "$backup_file" | docker-compose exec -T postgres psql -U postgres -d trading_bot
        else
            docker-compose exec -T postgres psql -U postgres -d trading_bot < "$backup_file"
        fi
        
    elif [[ "$backup_file" == *"full_backup"* ]]; then
        # Restaurar backup completo
        log "🎯 Restaurando backup completo..."
        
        # Extrair backup
        local temp_dir="/tmp/restore_$(date +%s)"
        mkdir -p "$temp_dir"
        tar -xzf "$backup_file" -C "$temp_dir"
        
        # Restaurar arquivos
        if [ -f "$temp_dir/files.tar.gz" ]; then
            tar -xzf "$temp_dir/files.tar.gz" --overwrite
        fi
        
        # Restaurar banco de dados
        for db_file in "$temp_dir"/db_backup_*.sql.gz; do
            if [ -f "$db_file" ]; then
                # Iniciar PostgreSQL
                if command -v docker-compose &> /dev/null; then
                    docker-compose up -d postgres
                else
                    docker compose up -d postgres
                fi
                
                sleep 10
                
                # Restaurar banco
                zcat "$db_file" | docker-compose exec -T postgres psql -U postgres -d trading_bot
                break
            fi
        done
        
        # Limpar diretório temporário
        rm -rf "$temp_dir"
        
    else
        # Restaurar backup de arquivos
        log "📁 Restaurando arquivos..."
        tar -xzf "$backup_file" --overwrite
    fi
    
    # Reiniciar todos os serviços
    log "▶️ Reiniciando serviços..."
    if command -v docker-compose &> /dev/null; then
        docker-compose up -d
    else
        docker compose up -d
    fi
    
    log_success "Restauração concluída"
}

# Verificar integridade do backup
verify_backup() {
    local backup_file=$1
    
    if [ -z "$backup_file" ]; then
        log_error "Nome do arquivo de backup não especificado"
        exit 1
    fi
    
    if [ ! -f "$BACKUP_DIR/$backup_file" ] && [ ! -f "$backup_file" ]; then
        log_error "Arquivo de backup não encontrado: $backup_file"
        exit 1
    fi
    
    # Usar caminho completo se necessário
    if [ ! -f "$backup_file" ]; then
        backup_file="$BACKUP_DIR/$backup_file"
    fi
    
    log "🔍 Verificando integridade do backup: $backup_file"
    
    # Verificar baseado na extensão
    if [[ "$backup_file" == *.tar.gz ]]; then
        if tar -tzf "$backup_file" > /dev/null 2>&1; then
            log_success "Backup tar.gz íntegro"
        else
            log_error "Backup tar.gz corrompido"
            exit 1
        fi
    elif [[ "$backup_file" == *.sql.gz ]]; then
        if gzip -t "$backup_file" 2>/dev/null; then
            log_success "Backup SQL íntegro"
        else
            log_error "Backup SQL corrompido"
            exit 1
        fi
    elif [[ "$backup_file" == *.gpg ]]; then
        if gpg --list-packets "$backup_file" > /dev/null 2>&1; then
            log_success "Backup criptografado íntegro"
        else
            log_error "Backup criptografado corrompido"
            exit 1
        fi
    else
        log_warning "Tipo de arquivo não reconhecido para verificação"
    fi
}

# Limpar backups antigos
cleanup_backups() {
    log "🧹 Limpando backups antigos (>${RETENTION_DAYS} dias)..."
    
    if [ ! -d "$BACKUP_DIR" ]; then
        log_warning "Diretório de backup não existe"
        return
    fi
    
    local deleted_count=0
    
    # Encontrar e deletar arquivos antigos
    while IFS= read -r -d '' file; do
        rm "$file"
        deleted_count=$((deleted_count + 1))
        log "🗑️ Removido: $(basename "$file")"
    done < <(find "$BACKUP_DIR" -name "*.tar.gz" -o -name "*.sql.gz" -o -name "*.gpg" -type f -mtime +$RETENTION_DAYS -print0 2>/dev/null)
    
    if [ $deleted_count -eq 0 ]; then
        log_success "Nenhum backup antigo encontrado"
    else
        log_success "Removidos $deleted_count backups antigos"
    fi
}

# Função principal
main() {
    # Valores padrão
    BACKUP_TYPE="full"
    ENCRYPT=false
    REMOTE=false
    LIST_ONLY=false
    RESTORE_FILE=""
    CLEANUP_ONLY=false
    VERIFY_FILE=""
    
    # Processar argumentos
    while [[ $# -gt 0 ]]; do
        case $1 in
            --full)
                BACKUP_TYPE="full"
                shift
                ;;
            --database-only)
                BACKUP_TYPE="database"
                shift
                ;;
            --files-only)
                BACKUP_TYPE="files"
                shift
                ;;
            --config-only)
                BACKUP_TYPE="config"
                shift
                ;;
            --logs-only)
                BACKUP_TYPE="logs"
                shift
                ;;
            --encrypt)
                ENCRYPT=true
                shift
                ;;
            --remote)
                REMOTE=true
                shift
                ;;
            --list)
                LIST_ONLY=true
                shift
                ;;
            --restore)
                RESTORE_FILE="$2"
                shift 2
                ;;
            --cleanup)
                CLEANUP_ONLY=true
                shift
                ;;
            --verify)
                VERIFY_FILE="$2"
                shift 2
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
    echo "💾 ====================================="
    echo "   MVP Bot de Trading - Backup Script"
    echo "===================================== 💾"
    echo
    
    # Criar diretórios
    create_directories
    
    # Executar ação solicitada
    if [ "$LIST_ONLY" = true ]; then
        list_backups
        exit 0
    elif [ -n "$RESTORE_FILE" ]; then
        check_prerequisites
        restore_backup "$RESTORE_FILE"
        exit 0
    elif [ "$CLEANUP_ONLY" = true ]; then
        cleanup_backups
        exit 0
    elif [ -n "$VERIFY_FILE" ]; then
        verify_backup "$VERIFY_FILE"
        exit 0
    fi
    
    # Verificar pré-requisitos para backup
    check_prerequisites
    
    # Executar backup
    local backup_file=""
    
    case $BACKUP_TYPE in
        full)
            backup_file=$(backup_full)
            ;;
        database)
            backup_file=$(backup_database)
            ;;
        files)
            backup_file=$(backup_files)
            ;;
        config)
            backup_file=$(backup_config)
            ;;
        logs)
            backup_file=$(backup_logs)
            ;;
    esac
    
    # Criptografar se solicitado
    if [ "$ENCRYPT" = true ] && [ -n "$backup_file" ]; then
        backup_file=$(encrypt_backup "$backup_file")
    fi
    
    # Enviar para remoto se solicitado
    if [ "$REMOTE" = true ] && [ -n "$backup_file" ]; then
        upload_remote "$backup_file"
    fi
    
    # Limpar backups antigos
    cleanup_backups
    
    # Sucesso
    echo
    log_success "🎉 Backup concluído com sucesso!"
    if [ -n "$backup_file" ]; then
        echo "📁 Arquivo: $backup_file"
        echo "📊 Tamanho: $(du -h "$backup_file" | cut -f1)"
    fi
    echo
}

# Executar função principal
main "$@"

