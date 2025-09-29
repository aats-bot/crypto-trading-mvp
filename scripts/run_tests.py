#!/usr/bin/env python3
"""
Script de Execução de Testes - Crypto Trading MVP
Executa infraestrutura de testes da Onda 1 de forma otimizada
"""

import os
import sys
import subprocess
import argparse
import platform
from pathlib import Path
import time

def print_banner():
    """Exibe banner dos testes"""
    print("=" * 60)
    print("🧪 CRYPTO TRADING MVP - TESTES AUTOMATIZADOS")
    print("📊 Infraestrutura da Onda 1 - 130+ Testes")
    print("=" * 60)
    print()

def check_environment():
    """Verifica ambiente de execução"""
    print("🔍 Verificando ambiente...")
    
    # Verificar se está em ambiente virtual
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    
    if in_venv:
        print(f"✅ Ambiente virtual ativo: {sys.prefix}")
    else:
        print("⚠️  Ambiente virtual não detectado")
    
    # Verificar pytest
    try:
        import pytest
        print(f"✅ Pytest {pytest.__version__} disponível")
    except ImportError:
        print("❌ Pytest não instalado")
        print("💡 Execute: pip install -r requirements-test.txt")
        sys.exit(1)
    
    print()

def run_test_category(category, description, test_path, extra_args=None):
    """Executa categoria específica de testes"""
    print(f"🧪 {description}...")
    print(f"📁 Caminho: {test_path}")
    
    start_time = time.time()
    
    # Construir comando
    cmd = [sys.executable, "-m", "pytest", test_path, "-v", "--tb=short"]
    if extra_args:
        cmd.extend(extra_args)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        duration = time.time() - start_time
        
        # Analisar resultado
        output_lines = result.stdout.split('\n')
        passed = sum(1 for line in output_lines if 'PASSED' in line)
        failed = sum(1 for line in output_lines if 'FAILED' in line)
        skipped = sum(1 for line in output_lines if 'SKIPPED' in line)
        
        if result.returncode == 0:
            print(f"✅ {category}: {passed} passou, {skipped} pulados")
        else:
            print(f"⚠️  {category}: {passed} passou, {failed} falharam, {skipped} pulados")
        
        print(f"⏱️  Tempo: {duration:.2f}s")
        print()
        
        return {
            'category': category,
            'passed': passed,
            'failed': failed,
            'skipped': skipped,
            'duration': duration,
            'success': result.returncode == 0
        }
        
    except Exception as e:
        print(f"❌ Erro ao executar {category}: {e}")
        return {
            'category': category,
            'passed': 0,
            'failed': 1,
            'skipped': 0,
            'duration': 0,
            'success': False
        }

def run_quick_tests():
    """Executa testes rápidos essenciais"""
    print("⚡ MODO RÁPIDO - Testes Essenciais")
    print("=" * 40)
    
    results = []
    
    # Testes essenciais
    essential_tests = [
        ("Estratégia PPP Vishva", "tests/unit/test_ppp_vishva_strategy.py"),
        ("Integração Simples", "tests/integration/test_simple_integration.py"),
        ("E2E Simplificados", "tests/e2e/test_e2e_simplified.py")
    ]
    
    for name, path in essential_tests:
        if Path(path).exists():
            result = run_test_category(name, f"Executando {name}", path)
            results.append(result)
        else:
            print(f"⚠️  {name}: Arquivo não encontrado - {path}")
    
    return results

def run_full_tests():
    """Executa suite completa de testes"""
    print("🔬 MODO COMPLETO - Suite Completa")
    print("=" * 40)
    
    results = []
    
    # Todas as categorias
    test_categories = [
        ("Unitários", "Testes Unitários", "tests/unit/"),
        ("Integração", "Testes de Integração", "tests/integration/test_simple_integration.py"),
        ("E2E", "Testes End-to-End", "tests/e2e/test_e2e_simplified.py")
    ]
    
    for category, description, path in test_categories:
        if Path(path).exists():
            result = run_test_category(category, description, path)
            results.append(result)
        else:
            print(f"⚠️  {category}: Caminho não encontrado - {path}")
    
    return results

def run_coverage_tests():
    """Executa testes com relatório de cobertura"""
    print("📊 MODO COBERTURA - Análise Completa")
    print("=" * 40)
    
    coverage_args = [
        "--cov=src",
        "--cov=app", 
        "--cov-report=html:htmlcov",
        "--cov-report=term-missing",
        "--cov-fail-under=80"
    ]
    
    result = run_test_category(
        "Cobertura",
        "Executando análise de cobertura",
        "tests/",
        coverage_args
    )
    
    if result['success']:
        print("📈 Relatório de cobertura gerado em: htmlcov/index.html")
    
    return [result]

def run_performance_tests():
    """Executa testes de performance"""
    print("🚀 MODO PERFORMANCE - Testes de Velocidade")
    print("=" * 40)
    
    performance_args = [
        "-m", "performance",
        "--durations=10"
    ]
    
    result = run_test_category(
        "Performance",
        "Executando testes de performance",
        "tests/",
        performance_args
    )
    
    return [result]

def show_summary(results):
    """Mostra resumo dos resultados"""
    print("📋 RESUMO DOS RESULTADOS")
    print("=" * 40)
    
    total_passed = sum(r['passed'] for r in results)
    total_failed = sum(r['failed'] for r in results)
    total_skipped = sum(r['skipped'] for r in results)
    total_duration = sum(r['duration'] for r in results)
    
    print(f"✅ Testes Passaram: {total_passed}")
    print(f"❌ Testes Falharam: {total_failed}")
    print(f"⏭️  Testes Pulados: {total_skipped}")
    print(f"⏱️  Tempo Total: {total_duration:.2f}s")
    
    success_rate = (total_passed / (total_passed + total_failed)) * 100 if (total_passed + total_failed) > 0 else 0
    print(f"📊 Taxa de Sucesso: {success_rate:.1f}%")
    
    print()
    
    # Status por categoria
    for result in results:
        status = "✅" if result['success'] else "❌"
        print(f"{status} {result['category']}: {result['passed']} passou, {result['failed']} falharam")
    
    print()
    
    # Recomendações
    if total_failed == 0:
        print("🎉 Todos os testes passaram! Infraestrutura sólida.")
    elif total_failed <= 3:
        print("⚠️  Poucos testes falharam - Qualidade boa, pequenos ajustes necessários.")
    else:
        print("🔧 Vários testes falharam - Revisar implementação necessária.")
    
    print()
    print("📚 Para mais detalhes, execute com -v ou --verbose")

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Executa testes do Crypto Trading MVP")
    parser.add_argument("--mode", "-m", 
                       choices=["quick", "full", "coverage", "performance"],
                       default="quick",
                       help="Modo de execução dos testes")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Saída detalhada")
    
    args = parser.parse_args()
    
    print_banner()
    check_environment()
    
    # Executar testes baseado no modo
    if args.mode == "quick":
        results = run_quick_tests()
    elif args.mode == "full":
        results = run_full_tests()
    elif args.mode == "coverage":
        results = run_coverage_tests()
    elif args.mode == "performance":
        results = run_performance_tests()
    
    show_summary(results)
    
    # Exit code baseado nos resultados
    total_failed = sum(r['failed'] for r in results)
    sys.exit(0 if total_failed == 0 else 1)

if __name__ == "__main__":
    main()

