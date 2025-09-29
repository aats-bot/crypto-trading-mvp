[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
# Script de Verificacao de Status - Crypto Trading MVP
# Verifica status completo da infraestrutura Docker

Write-Host "============================================" -ForegroundColor Cyan
Write-Host " CRYPTO TRADING MVP - STATUS CHECK" -ForegroundColor Cyan
Write-Host " Verificacao da Infraestrutura Docker" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Funcao para exibir secao
function Show-Section {
    param($Title, $Color = "Yellow")
    Write-Host ""
    Write-Host " $Title" -ForegroundColor $Color
    Write-Host ("=" * ($Title.Length + 4)) -ForegroundColor Gray
}

# Verificar se Docker esta rodando
Show-Section "DOCKER ENGINE STATUS"
try {
    $dockerVersion = docker version --format "{{.Server.Version}}" 2>$null
    if ($dockerVersion) {
        Write-Host " Docker Engine: v$dockerVersion" -ForegroundColor Green
    } else {
        Write-Host " Docker Engine nao esta rodando" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host " Docker nao encontrado ou nao esta rodando" -ForegroundColor Red
    exit 1
}

# Verificar Docker Compose
try {
    $composeVersion = docker-compose version --short 2>$null
    if ($composeVersion) {
        Write-Host " Docker Compose: v$composeVersion" -ForegroundColor Green
    } else {
        Write-Host "  Docker Compose nao encontrado" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  Docker Compose nao disponivel" -ForegroundColor Yellow
}

# Status dos containers
Show-Section "CONTAINERS STATUS"
$containers = docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" --filter "name=crypto-trading"

if ($containers -and $containers.Count -gt 1) {
    Write-Host $containers -ForegroundColor White
} else {
    Write-Host "i  Nenhum container do Crypto Trading encontrado" -ForegroundColor Blue
}

# Containers em execucao
Show-Section "RUNNING CONTAINERS"
$runningContainers = docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}" --filter "name=crypto-trading"

if ($runningContainers -and $runningContainers.Count -gt 1) {
    Write-Host $runningContainers -ForegroundColor Green
} else {
    Write-Host "i  Nenhum container em execucao" -ForegroundColor Blue
}

# Imagens Docker
Show-Section "DOCKER IMAGES"
$images = docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}" --filter "reference=crypto-trading*"

if ($images -and $images.Count -gt 1) {
    Write-Host $images -ForegroundColor White
} else {
    Write-Host "i  Nenhuma imagem do Crypto Trading encontrada" -ForegroundColor Blue
}

# Volumes Docker
Show-Section "DOCKER VOLUMES"
$volumes = docker volume ls --format "table {{.Name}}\t{{.Driver}}" --filter "name=crypto-trading"

if ($volumes -and $volumes.Count -gt 1) {
    Write-Host $volumes -ForegroundColor White
} else {
    Write-Host "i  Nenhum volume do Crypto Trading encontrado" -ForegroundColor Blue
}

# Networks Docker
Show-Section "DOCKER NETWORKS"
$networks = docker network ls --format "table {{.Name}}\t{{.Driver}}\t{{.Scope}}" --filter "name=crypto-trading"

if ($networks -and $networks.Count -gt 1) {
    Write-Host $networks -ForegroundColor White
} else {
    Write-Host "i  Nenhuma rede do Crypto Trading encontrada" -ForegroundColor Blue
}

# Uso de recursos
Show-Section "RESOURCE USAGE"
try {
    $stats = docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}" --filter "name=crypto-trading" 2>$null
    
    if ($stats -and $stats.Count -gt 1) {
        Write-Host $stats -ForegroundColor Cyan
    } else {
        Write-Host "i  Nenhum container em execucao para mostrar estatisticas" -ForegroundColor Blue
    }
} catch {
    Write-Host "  Nao foi possivel obter estatisticas de recursos" -ForegroundColor Yellow
}

# Logs recentes (se houver containers rodando)
Show-Section "RECENT LOGS"
$runningCount = (docker ps --filter "name=crypto-trading" --quiet | Measure-Object).Count

if ($runningCount -gt 0) {
    Write-Host " Logs dos ultimos 5 minutos:" -ForegroundColor Blue
    try {
        docker-compose -f docker-compose.production.yml logs --tail=10 --since=5m 2>$null
    } catch {
        Write-Host "  Nao foi possivel obter logs recentes" -ForegroundColor Yellow
    }
} else {
    Write-Host "i  Nenhum container rodando para mostrar logs" -ForegroundColor Blue
}

# Health checks
Show-Section "HEALTH CHECKS"
$healthyContainers = docker ps --filter "name=crypto-trading" --filter "health=healthy" --format "{{.Names}}"
$unhealthyContainers = docker ps --filter "name=crypto-trading" --filter "health=unhealthy" --format "{{.Names}}"

if ($healthyContainers) {
    Write-Host " Containers saudaveis:" -ForegroundColor Green
    $healthyContainers | ForEach-Object { Write-Host "   - $_" -ForegroundColor Green }
}

if ($unhealthyContainers) {
    Write-Host " Containers com problemas:" -ForegroundColor Red
    $unhealthyContainers | ForEach-Object { Write-Host "   - $_" -ForegroundColor Red }
}

if (-not $healthyContainers -and -not $unhealthyContainers) {
    Write-Host "i  Nenhum health check ativo" -ForegroundColor Blue
}

# Portas em uso
Show-Section "PORTS IN USE"
$ports = @(8000, 8501, 5432, 6379, 80, 443, 9090, 3000)
Write-Host " Verificando portas do projeto:" -ForegroundColor Blue

foreach ($port in $ports) {
    try {
        $connection = Test-NetConnection -ComputerName localhost -Port $port -WarningAction SilentlyContinue -InformationLevel Quiet
        if ($connection) {
            Write-Host "    Porta $($port): EM USO" -ForegroundColor Green
        } else {
            Write-Host "    Porta $($port): LIVRE" -ForegroundColor Gray
        }
    } catch {
        Write-Host "    Porta $($port): LIVRE" -ForegroundColor Gray
    }
}

# Resumo final
Show-Section "SUMMARY"
$totalContainers = (docker ps -a --filter "name=crypto-trading" --quiet | Measure-Object).Count
$runningContainers = (docker ps --filter "name=crypto-trading" --quiet | Measure-Object).Count
$totalImages = (docker images --filter "reference=crypto-trading*" --quiet | Measure-Object).Count

Write-Host " Resumo da Infraestrutura:" -ForegroundColor White
Write-Host "    Total de containers: $totalContainers" -ForegroundColor White
Write-Host "    Containers rodando: $runningContainers" -ForegroundColor White
Write-Host "    Imagens criadas: $totalImages" -ForegroundColor White

if ($runningContainers -eq 0 -and $totalContainers -eq 0) {
    Write-Host ""
    Write-Host " PROXIMOS PASSOS:" -ForegroundColor Yellow
    Write-Host "   1. Execute: docker-compose -f docker-compose.production.yml build" -ForegroundColor White
    Write-Host "   2. Execute: docker-compose -f docker-compose.production.yml up -d" -ForegroundColor White
} elseif ($runningContainers -gt 0) {
    Write-Host ""
    Write-Host " SISTEMA OPERACIONAL!" -ForegroundColor Green
    Write-Host "    Dashboard: http://localhost:8501" -ForegroundColor White
    Write-Host "    API: http://localhost:8000" -ForegroundColor White
    Write-Host "    API Docs: http://localhost:8000/docs" -ForegroundColor White
    Write-Host "    Grafana: http://localhost:3000" -ForegroundColor White
}

Write-Host ""
Write-Host " Verificacao de status concluida!" -ForegroundColor Green

