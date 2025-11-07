#!/bin/bash
################################################################################
# Script de Testes - CI Pipeline
#
# Descrição: Executa testes automatizados com cobertura
# Autor: Manus AI
# Data: 07/11/2025
################################################################################

set -e

echo "🧪 Executando testes automatizados..."
echo ""

# Verificar se está no ambiente virtual
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Aviso: Ambiente virtual não detectado"
    echo "   Recomenda-se ativar o ambiente virtual antes de executar"
fi

# Instalar dependências de teste se necessário
echo "▶️  Verificando dependências de teste..."
pip install -q pytest pytest-cov pytest-asyncio pytest-mock 2>/dev/null || true

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  Executando Testes com Cobertura"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Verificar se há testes
if [ ! -d "tests" ]; then
    echo "⚠️  Diretório 'tests' não encontrado"
    echo "   Criando estrutura básica de testes..."
    mkdir -p tests
    touch tests/__init__.py
    echo "✅ Estrutura de testes criada"
fi

# Executar testes
echo "▶️  Executando pytest..."
echo ""

if pytest \
    --verbose \
    --cov=. \
    --cov-report=term-missing \
    --cov-report=xml \
    --cov-report=html \
    --cov-config=pyproject.toml \
    --tb=short; then
    echo ""
    echo "✅ Todos os testes passaram!"
else
    echo ""
    echo "❌ Alguns testes falharam!"
    exit 1
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  Verificando Cobertura de Testes"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Verificar threshold de cobertura
echo "▶️  Verificando threshold de cobertura (mínimo: 90%)..."
if coverage report --fail-under=90; then
    echo ""
    echo "✅ Cobertura de testes aprovada (≥ 90%)"
else
    echo ""
    echo "⚠️  Cobertura de testes abaixo do mínimo"
    echo "   Threshold: 90%"
    echo ""
    echo "💡 Adicione mais testes para aumentar a cobertura"
    exit 1
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  📊 Relatórios Gerados"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "  📄 coverage.xml - Relatório XML (para CI/CD)"
echo "  📁 htmlcov/ - Relatório HTML (abra htmlcov/index.html)"
echo ""

echo "═══════════════════════════════════════════════════════════"
echo "  ✅ TESTES CONCLUÍDOS COM SUCESSO!"
echo "═══════════════════════════════════════════════════════════"
echo ""
