# 🔄 Middlewares da API - Inicialização
"""
Middlewares para processamento de requisições da API
Localização: /src/api/middleware/__init__.py
"""

# Importar todos os middlewares
from .auth_middleware import (
    AuthMiddleware,
    require_auth,
    get_current_user,
    verify_token,
)

from .cors_middleware import (
    CORSMiddleware,
    setup_cors,
)

from .rate_limit_middleware import (
    RateLimitMiddleware,
    rate_limit,
    get_client_ip,
)

from .logging_middleware import (
    LoggingMiddleware,
    request_logger,
    audit_logger,
)

from .error_middleware import (
    ErrorHandlerMiddleware,
    handle_api_error,
    format_error_response,
)

from .security_middleware import (
    SecurityMiddleware,
    security_headers,
    validate_request,
)

from .monitoring_middleware import (
    MonitoringMiddleware,
    metrics_collector,
    performance_tracker,
)

# Lista de todos os middlewares disponíveis
__all__ = [
    # Auth Middleware
    "AuthMiddleware",
    "require_auth",
    "get_current_user",
    "verify_token",
    
    # CORS Middleware
    "CORSMiddleware",
    "setup_cors",
    
    # Rate Limit Middleware
    "RateLimitMiddleware",
    "rate_limit",
    "get_client_ip",
    
    # Logging Middleware
    "LoggingMiddleware",
    "request_logger",
    "audit_logger",
    
    # Error Middleware
    "ErrorHandlerMiddleware",
    "handle_api_error",
    "format_error_response",
    
    # Security Middleware
    "SecurityMiddleware",
    "security_headers",
    "validate_request",
    
    # Monitoring Middleware
    "MonitoringMiddleware",
    "metrics_collector",
    "performance_tracker",
]

