# Script de Build Docker - Crypto Trading MVP
# Constrói todas as imagens Docker do projeto

Write-Host "🐳 Construindo imagens Docker..." -ForegroundColor Blue

# Build da API
Write-Host "📊 Construindo API..." -ForegroundColor Green
docker build -t crypto-trading-api:latest -f docker/api/Dockerfile .

# Build do Dashboard
Write-Host "🎨 Construindo Dashboard..." -ForegroundColor Green
docker build -t crypto-trading-dashboard:latest -f docker/dashboard/Dockerfile .

Write-Host "✅ Build concluído!" -ForegroundColor Green
Write-Host "🚀 Para iniciar: docker-compose up -d" -ForegroundColor Yellow
