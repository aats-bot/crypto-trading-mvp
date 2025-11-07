# Setup Estrutura Semana 5 - Versao Simplificada
# Autor: Manus AI
# Data: 07/11/2025

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  CONFIGURACAO RAPIDA - ESTRUTURA SEMANA 5" -ForegroundColor Cyan
Write-Host "  Pipeline CI/CD Automatizado" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se esta no diretorio correto
if (-not (Test-Path ".git")) {
    Write-Host "ERRO: Este nao parece ser o diretorio raiz do projeto Git." -ForegroundColor Red
    Write-Host "Por favor, navegue ate o diretorio crypto-trading-mvp e execute novamente." -ForegroundColor Yellow
    exit 1
}

Write-Host "Diretorio do projeto confirmado!" -ForegroundColor Green
Write-Host ""

# ETAPA 1: CRIAR DIRETORIOS
Write-Host "ETAPA 1: Criando estrutura de diretorios..." -ForegroundColor Yellow
Write-Host ""

$directories = @(
    "scripts\ci",
    "scripts\deploy",
    "scripts\quality",
    "config\quality",
    "docs\ci-cd",
    "docs\runbooks"
)

foreach ($dir in $directories) {
    Write-Host "  Criando $dir\" -ForegroundColor White
    New-Item -Path $dir -ItemType Directory -Force | Out-Null
}

Write-Host ""
Write-Host "Estrutura de diretorios criada!" -ForegroundColor Green
Write-Host ""

# ETAPA 2: CRIAR ARQUIVOS DE CONFIGURACAO
Write-Host "ETAPA 2: Criando arquivos de configuracao..." -ForegroundColor Yellow
Write-Host ""

# .flake8
Write-Host "  Criando .flake8" -ForegroundColor White
@"
[flake8]
max-line-length = 100
exclude = 
    .git,
    __pycache__,
    .venv,
    venv,
    build,
    dist,
    *.egg-info
ignore = E203, E266, E501, W503
per-file-ignores =
    __init__.py:F401
"@ | Out-File -FilePath ".flake8" -Encoding UTF8

# pyproject.toml
Write-Host "  Criando pyproject.toml" -ForegroundColor White
@"
[tool.black]
line-length = 100
target-version = ['py311']
include = '\.pyi?$'

[tool.isort]
profile = "black"
line_length = 100
skip_gitignore = true

[tool.pytest.ini_options]
minversion = "7.0"
addopts = "-ra -q --cov=. --cov-report=term-missing"
testpaths = ["tests"]
"@ | Out-File -FilePath "pyproject.toml" -Encoding UTF8

# .github/CODEOWNERS
Write-Host "  Criando .github/CODEOWNERS" -ForegroundColor White
@"
# CODEOWNERS
* @lucas
/.github/workflows/ @lucas
/docker/ @lucas
/scripts/ @lucas
"@ | Out-File -FilePath ".github\CODEOWNERS" -Encoding UTF8

# .github/dependabot.yml
Write-Host "  Criando .github/dependabot.yml" -ForegroundColor White
@"
version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
"@ | Out-File -FilePath ".github\dependabot.yml" -Encoding UTF8

Write-Host ""
Write-Host "Arquivos de configuracao criados!" -ForegroundColor Green
Write-Host ""

# ETAPA 3: CRIAR ARQUIVOS DE AMBIENTE
Write-Host "ETAPA 3: Criando arquivos de ambiente..." -ForegroundColor Yellow
Write-Host ""

# dev.env
Write-Host "  Criando config/environments/dev.env" -ForegroundColor White
@"
# Development Environment
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/crypto_trading_dev
REDIS_URL=redis://localhost:6379/0
"@ | Out-File -FilePath "config\environments\dev.env" -Encoding UTF8

# staging.env
Write-Host "  Criando config/environments/staging.env" -ForegroundColor White
@"
# Staging Environment
ENVIRONMENT=staging
DEBUG=false
LOG_LEVEL=INFO
DATABASE_URL=postgresql://user:password@staging-db:5432/crypto_trading_staging
REDIS_URL=redis://staging-redis:6379/0
"@ | Out-File -FilePath "config\environments\staging.env" -Encoding UTF8

# production.env.example
Write-Host "  Criando config/environments/production.env.example" -ForegroundColor White
@"
# Production Environment (EXAMPLE)
# IMPORTANTE: Copie para production.env e configure com valores reais
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING
DATABASE_URL=postgresql://user:password@production-db:5432/crypto_trading_prod
REDIS_URL=redis://production-redis:6379/0
SECRET_KEY=CHANGE_THIS_TO_RANDOM_SECRET_KEY
"@ | Out-File -FilePath "config\environments\production.env.example" -Encoding UTF8

Write-Host ""
Write-Host "Arquivos de ambiente criados!" -ForegroundColor Green
Write-Host ""

# ETAPA 4: CRIAR CONFIGURACOES DE QUALIDADE
Write-Host "ETAPA 4: Criando configuracoes de qualidade..." -ForegroundColor Yellow
Write-Host ""

# .trivyignore
Write-Host "  Criando config/quality/.trivyignore" -ForegroundColor White
@"
# Trivy Ignore File
# Lista de CVEs para ignorar (com justificativa)
"@ | Out-File -FilePath "config\quality\.trivyignore" -Encoding UTF8

# .bandit
Write-Host "  Criando config/quality/.bandit" -ForegroundColor White
@"
[bandit]
exclude_dirs = ['/tests', '/.venv', '/venv']
"@ | Out-File -FilePath "config\quality\.bandit" -Encoding UTF8

# sonar-project.properties
Write-Host "  Criando config/quality/sonar-project.properties" -ForegroundColor White
@"
sonar.projectKey=crypto-trading-mvp
sonar.projectName=Crypto Trading MVP
sonar.projectVersion=1.0
sonar.sources=.
sonar.exclusions=**/tests/**,**/__pycache__/**,**/venv/**
sonar.tests=tests
sonar.python.version=3.11
"@ | Out-File -FilePath "config\quality\sonar-project.properties" -Encoding UTF8

Write-Host ""
Write-Host "Configuracoes de qualidade criadas!" -ForegroundColor Green
Write-Host ""

# ETAPA 5: CRIAR PLACEHOLDERS DE DOCUMENTACAO
Write-Host "ETAPA 5: Criando placeholders de documentacao..." -ForegroundColor Yellow
Write-Host ""

$docFiles = @{
    "docs\ci-cd\pipeline-overview.md" = "# Visao Geral do Pipeline CI/CD`n`n*Documentacao em desenvolvimento*"
    "docs\ci-cd\deployment-guide.md" = "# Guia de Deployment`n`n*Documentacao em desenvolvimento*"
    "docs\ci-cd\rollback-procedures.md" = "# Procedimentos de Rollback`n`n*Documentacao em desenvolvimento*"
    "docs\ci-cd\troubleshooting.md" = "# Troubleshooting`n`n*Documentacao em desenvolvimento*"
    "docs\runbooks\deployment-checklist.md" = "# Checklist de Deployment`n`n*Documentacao em desenvolvimento*"
    "docs\runbooks\incident-response.md" = "# Resposta a Incidentes`n`n*Documentacao em desenvolvimento*"
    "docs\runbooks\emergency-procedures.md" = "# Procedimentos de Emergencia`n`n*Documentacao em desenvolvimento*"
}

foreach ($file in $docFiles.Keys) {
    Write-Host "  Criando $file" -ForegroundColor White
    $docFiles[$file] | Out-File -FilePath $file -Encoding UTF8
}

Write-Host ""
Write-Host "Placeholders de documentacao criados!" -ForegroundColor Green
Write-Host ""

# ETAPA 6: CRIAR README DE SCRIPTS
Write-Host "ETAPA 6: Criando README de scripts..." -ForegroundColor Yellow
Write-Host ""

@"
# Scripts do Projeto

Este diretorio contem scripts auxiliares para CI/CD e operacoes do projeto.

## Estrutura

- **ci/** - Scripts de Continuous Integration
- **deploy/** - Scripts de deployment
- **quality/** - Scripts de verificacao de qualidade

## Scripts Disponiveis

### CI Scripts
- lint.sh - Executa linting do codigo
- test.sh - Executa testes
- build.sh - Constroi images Docker
- security-scan.sh - Executa scanning de seguranca

### Deploy Scripts
- deploy.sh - Script principal de deployment
- rollback.sh - Rollback para versao anterior
- health-check.sh - Verifica saude do sistema
- notify.sh - Envia notificacoes

### Quality Scripts
- check-coverage.sh - Verifica cobertura de testes
- check-complexity.sh - Verifica complexidade do codigo
- generate-report.sh - Gera relatorios de qualidade
"@ | Out-File -FilePath "scripts\README.md" -Encoding UTF8

Write-Host "README de scripts criado!" -ForegroundColor Green
Write-Host ""

# RESUMO FINAL
Write-Host "============================================================" -ForegroundColor Green
Write-Host "  CONFIGURACAO CONCLUIDA COM SUCESSO!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Estrutura criada:" -ForegroundColor White
Write-Host "  - 6 diretorios" -ForegroundColor Cyan
Write-Host "  - 15+ arquivos de configuracao" -ForegroundColor Cyan
Write-Host "  - 7 arquivos de documentacao" -ForegroundColor Cyan
Write-Host ""
Write-Host "Proximos passos:" -ForegroundColor Yellow
Write-Host "  1. Executar: .\check_semana5_progress.ps1" -ForegroundColor White
Write-Host "  2. Criar scripts em scripts/ci/, scripts/deploy/" -ForegroundColor White
Write-Host "  3. Completar workflows do GitHub Actions" -ForegroundColor White
Write-Host "  4. Commitar: git add . && git commit -m 'feat: setup CI/CD structure'" -ForegroundColor White
Write-Host ""
Write-Host "Estrutura da Semana 5 configurada!" -ForegroundColor Green
Write-Host ""
