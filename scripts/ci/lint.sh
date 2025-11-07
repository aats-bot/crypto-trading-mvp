#!/bin/bash
################################################################################
# Script de Linting - CI Pipeline
#
# Descrição: Executa verificações de linting no código Python
# Autor: Manus AI
# Data: 07/11/2025
################################################################################

set -e

echo "🔍 Executando linting do código..."
echo ""

# Verificar se está no ambiente virtual
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Aviso: Ambiente virtual não detectado"
    echo "   Recomenda-se ativar o ambiente virtual antes de executar"
fi

# Instalar dependências de linting se necessário
echo "▶️  Verificando dependências de linting..."
pip install -q flake8 black isort 2>/dev/null || true

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  1. Flake8 - Verificação de Estilo e Erros"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Flake8 - Erros críticos
echo "▶️  Verificando erros críticos..."
if flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics; then
    echo "✅ Nenhum erro crítico encontrado"
else
    echo "❌ Erros críticos encontrados!"
    exit 1
fi

echo ""

# Flake8 - Verificação completa
echo "▶️  Verificando estilo completo..."
if flake8 . --count --max-complexity=10 --max-line-length=100 --statistics; then
    echo "✅ Estilo de código aprovado"
else
    echo "⚠️  Avisos de estilo encontrados"
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  2. Black - Formatação de Código"
echo "═══════════════════════════════════════════════════════════"
echo ""

echo "▶️  Verificando formatação com Black..."
if black . --check --diff; then
    echo "✅ Código está formatado corretamente"
else
    echo "❌ Código precisa de formatação!"
    echo ""
    echo "💡 Para formatar automaticamente, execute:"
    echo "   black ."
    exit 1
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  3. isort - Ordenação de Imports"
echo "═══════════════════════════════════════════════════════════"
echo ""

echo "▶️  Verificando ordenação de imports..."
if isort . --check-only --diff; then
    echo "✅ Imports estão ordenados corretamente"
else
    echo "❌ Imports precisam ser ordenados!"
    echo ""
    echo "💡 Para ordenar automaticamente, execute:"
    echo "   isort ."
    exit 1
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  ✅ LINTING CONCLUÍDO COM SUCESSO!"
echo "═══════════════════════════════════════════════════════════"
echo ""
