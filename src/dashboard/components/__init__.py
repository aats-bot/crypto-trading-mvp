# 🧩 Componentes do Dashboard - Inicialização
"""
Componentes reutilizáveis para o dashboard Streamlit
Localização: /src/dashboard/components/__init__.py
"""

# Importar todos os componentes principais
from .auth_components import (
    login_form,
    register_form,
    logout_button,
    auth_status_indicator,
)

from .trading_components import (
    bot_status_card,
    trading_controls,
    position_table,
    order_history_table,
    performance_metrics,
)

from .chart_components import (
    price_chart,
    performance_chart,
    portfolio_distribution_chart,
    strategy_comparison_chart,
)

from .config_components import (
    strategy_selector,
    risk_management_form,
    symbol_selector,
    trading_parameters_form,
)

from .ui_components import (
    sidebar_navigation,
    header_component,
    footer_component,
    notification_toast,
    loading_spinner,
    error_message,
    success_message,
)

from .data_components import (
    market_data_table,
    account_balance_display,
    trade_statistics,
    profit_loss_summary,
)

# Lista de todos os componentes disponíveis
__all__ = [
    # Auth Components
    "login_form",
    "register_form", 
    "logout_button",
    "auth_status_indicator",
    
    # Trading Components
    "bot_status_card",
    "trading_controls",
    "position_table",
    "order_history_table",
    "performance_metrics",
    
    # Chart Components
    "price_chart",
    "performance_chart",
    "portfolio_distribution_chart",
    "strategy_comparison_chart",
    
    # Config Components
    "strategy_selector",
    "risk_management_form",
    "symbol_selector",
    "trading_parameters_form",
    
    # UI Components
    "sidebar_navigation",
    "header_component",
    "footer_component",
    "notification_toast",
    "loading_spinner",
    "error_message",
    "success_message",
    
    # Data Components
    "market_data_table",
    "account_balance_display",
    "trade_statistics",
    "profit_loss_summary",
]

