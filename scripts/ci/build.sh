#!/bin/bash
################################################################################
# Script de Build - CI Pipeline
#
# Descrição: Constrói imagens Docker do projeto
# Autor: Manus AI
# Data: 07/11/2025
################################################################################

set -e

echo "🏗️  Construindo imagens Docker..."
echo ""

# Verificar se Docker está disponível
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não encontrado!"
    echo "   Por favor, instale o Docker antes de continuar"
    exit 1
fi

# Verificar se Docker está rodando
if ! docker info &> /dev/null; then
    echo "❌ Docker não está rodando!"
    echo "   Por favor, inicie o Docker Desktop"
    exit 1
fi

echo "✅ Docker disponível e rodando"
echo ""

# Definir tag
TAG="${1:-latest}"
echo "📦 Tag da build: $TAG"
echo ""

# Lista de serviços para build
SERVICES=()

# Verificar quais Dockerfiles existem
echo "▶️  Verificando Dockerfiles disponíveis..."
echo ""

if [ -f "docker/api/Dockerfile" ]; then
    SERVICES+=("api")
    echo "  ✅ API Dockerfile encontrado"
fi

if [ -f "docker/dashboard/Dockerfile" ]; then
    SERVICES+=("dashboard")
    echo "  ✅ Dashboard Dockerfile encontrado"
fi

if [ -f "docker/worker/Dockerfile" ]; then
    SERVICES+=("worker")
    echo "  ✅ Worker Dockerfile encontrado"
fi

if [ -f "docker/scheduler/Dockerfile" ]; then
    SERVICES+=("scheduler")
    echo "  ✅ Scheduler Dockerfile encontrado"
fi

if [ ${#SERVICES[@]} -eq 0 ]; then
    echo ""
    echo "⚠️  Nenhum Dockerfile encontrado!"
    echo "   Esperado em: docker/*/Dockerfile"
    echo ""
    echo "💡 Criando Dockerfile de exemplo..."
    mkdir -p docker/api
    cat > docker/api/Dockerfile <<'EOF'
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF
    echo "✅ Dockerfile de exemplo criado em docker/api/Dockerfile"
    SERVICES+=("api")
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  Construindo Imagens"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Build de cada serviço
BUILD_SUCCESS=true

for service in "${SERVICES[@]}"; do
    echo "▶️  Building $service..."
    
    IMAGE_NAME="crypto-trading-$service:$TAG"
    DOCKERFILE="docker/$service/Dockerfile"
    
    if docker build \
        -f "$DOCKERFILE" \
        -t "$IMAGE_NAME" \
        --build-arg BUILD_DATE="$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
        --build-arg VERSION="$TAG" \
        .; then
        echo "  ✅ $service build concluído: $IMAGE_NAME"
    else
        echo "  ❌ $service build falhou!"
        BUILD_SUCCESS=false
    fi
    
    echo ""
done

if [ "$BUILD_SUCCESS" = false ]; then
    echo "❌ Alguns builds falharam!"
    exit 1
fi

echo "═══════════════════════════════════════════════════════════"
echo "  📊 Imagens Construídas"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Listar imagens construídas
docker images | grep "crypto-trading" | grep "$TAG"

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  ✅ BUILD CONCLUÍDO COM SUCESSO!"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "💡 Para testar as imagens localmente:"
echo "   docker-compose up -d"
echo ""
