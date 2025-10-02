# conftest.py (na raiz)
import builtins
import pytest  # noqa
import pytest_asyncio as _pytest_asyncio

# Disponibiliza o nome 'pytest_asyncio' em escopo global dos testes
builtins.pytest_asyncio = _pytest_asyncio

# (opcional) registre marks usados nos testes para evitar warnings
def pytest_configure(config):
    config.addinivalue_line("markers", "performance: marca de performance")
    config.addinivalue_line("markers", "integration: marca de integração")
    config.addinivalue_line("markers", "security: marca de segurança")
