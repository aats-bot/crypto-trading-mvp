# 📊 Utilitários de Dados - MVP Bot de Trading
"""
Utilitários para manipulação, validação e formatação de dados
Localização: /src/utils/data_utils.py
"""
import re
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Tuple
from decimal import Decimal, ROUND_HALF_UP
import logging


logger = logging.getLogger(__name__)


# Constantes
VALID_TIMEFRAMES = ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M']
VALID_SIDES = ['buy', 'sell', 'long', 'short']
VALID_ORDER_TYPES = ['market', 'limit', 'stop', 'stop_limit']


def format_currency(amount: float, currency: str = "USD", decimals: int = 2) -> str:
    """
    Formatar valor monetário
    
    Args:
        amount: Valor a ser formatado
        currency: Moeda (USD, BTC, ETH, etc.)
        decimals: Número de casas decimais
        
    Returns:
        String formatada (ex: "$1,234.56")
    """
    try:
        if currency.upper() == "USD":
            return f"${amount:,.{decimals}f}"
        elif currency.upper() in ["BTC", "ETH"]:
            return f"{amount:.{decimals}f} {currency.upper()}"
        else:
            return f"{amount:,.{decimals}f} {currency.upper()}"
    except (ValueError, TypeError):
        return f"0.00 {currency.upper()}"


def format_percentage(value: float, decimals: int = 2, show_sign: bool = True) -> str:
    """
    Formatar percentual
    
    Args:
        value: Valor decimal (0.1234 = 12.34%)
        decimals: Casas decimais
        show_sign: Mostrar sinal + para valores positivos
        
    Returns:
        String formatada (ex: "+12.34%")
    """
    try:
        percentage = value * 100
        sign = "+" if show_sign and percentage > 0 else ""
        return f"{sign}{percentage:.{decimals}f}%"
    except (ValueError, TypeError):
        return "0.00%"


def format_datetime(dt: datetime, format_type: str = "default") -> str:
    """
    Formatar data/hora
    
    Args:
        dt: Objeto datetime
        format_type: Tipo de formato (default, short, long, iso)
        
    Returns:
        String formatada
    """
    try:
        formats = {
            "default": "%Y-%m-%d %H:%M:%S",
            "short": "%m/%d %H:%M",
            "long": "%A, %B %d, %Y at %I:%M %p",
            "iso": "%Y-%m-%dT%H:%M:%SZ",
            "date_only": "%Y-%m-%d",
            "time_only": "%H:%M:%S"
        }
        
        return dt.strftime(formats.get(format_type, formats["default"]))
    except (ValueError, AttributeError):
        return "Invalid Date"


def format_number(number: float, decimals: int = 2, use_thousands_separator: bool = True) -> str:
    """
    Formatar número com separadores
    
    Args:
        number: Número a ser formatado
        decimals: Casas decimais
        use_thousands_separator: Usar separador de milhares
        
    Returns:
        String formatada
    """
    try:
        if use_thousands_separator:
            return f"{number:,.{decimals}f}"
        else:
            return f"{number:.{decimals}f}"
    except (ValueError, TypeError):
        return "0.00"


def validate_symbol(symbol: str) -> bool:
    """
    Validar símbolo de trading
    
    Args:
        symbol: Símbolo a ser validado (ex: BTCUSDT)
        
    Returns:
        True se válido
    """
    if not isinstance(symbol, str):
        return False
    
    # Padrão: 3-10 caracteres + USDT/BUSD/BTC/ETH
    pattern = r'^[A-Z]{2,10}(USDT|BUSD|BTC|ETH|USD)$'
    return bool(re.match(pattern, symbol.upper()))


def validate_timeframe(timeframe: str) -> bool:
    """
    Validar timeframe
    
    Args:
        timeframe: Timeframe a ser validado (ex: 1h, 4h, 1d)
        
    Returns:
        True se válido
    """
    return timeframe in VALID_TIMEFRAMES


def validate_side(side: str) -> bool:
    """
    Validar lado da operação
    
    Args:
        side: Lado a ser validado (buy, sell, long, short)
        
    Returns:
        True se válido
    """
    return side.lower() in VALID_SIDES


def validate_order_type(order_type: str) -> bool:
    """
    Validar tipo de ordem
    
    Args:
        order_type: Tipo a ser validado
        
    Returns:
        True se válido
    """
    return order_type.lower() in VALID_ORDER_TYPES


def validate_price(price: Union[float, str]) -> bool:
    """
    Validar preço
    
    Args:
        price: Preço a ser validado
        
    Returns:
        True se válido
    """
    try:
        price_float = float(price)
        return price_float > 0 and price_float < 1e10  # Limite razoável
    except (ValueError, TypeError):
        return False


def validate_quantity(quantity: Union[float, str]) -> bool:
    """
    Validar quantidade
    
    Args:
        quantity: Quantidade a ser validada
        
    Returns:
        True se válido
    """
    try:
        qty_float = float(quantity)
        return qty_float > 0 and qty_float < 1e6  # Limite razoável
    except (ValueError, TypeError):
        return False


def sanitize_numeric_input(value: Any, default: float = 0.0) -> float:
    """
    Sanitizar entrada numérica
    
    Args:
        value: Valor a ser sanitizado
        default: Valor padrão se inválido
        
    Returns:
        Valor float sanitizado
    """
    try:
        if isinstance(value, str):
            # Remover caracteres não numéricos exceto . e -
            cleaned = re.sub(r'[^\d.-]', '', value)
            return float(cleaned) if cleaned else default
        return float(value)
    except (ValueError, TypeError):
        return default


def parse_timeframe(timeframe: str) -> int:
    """
    Converter timeframe para segundos
    
    Args:
        timeframe: Timeframe (ex: 1m, 1h, 1d)
        
    Returns:
        Segundos correspondentes
    """
    if not validate_timeframe(timeframe):
        raise ValueError(f"Invalid timeframe: {timeframe}")
    
    multipliers = {
        'm': 60,           # minutos
        'h': 3600,         # horas
        'd': 86400,        # dias
        'w': 604800,       # semanas
        'M': 2592000       # meses (30 dias)
    }
    
    # Extrair número e unidade
    match = re.match(r'(\d+)([mhdwM])', timeframe)
    if not match:
        raise ValueError(f"Invalid timeframe format: {timeframe}")
    
    number, unit = match.groups()
    return int(number) * multipliers[unit]


def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """
    Calcular mudança percentual
    
    Args:
        old_value: Valor antigo
        new_value: Valor novo
        
    Returns:
        Mudança percentual (decimal)
    """
    if old_value == 0:
        return 0.0
    
    return (new_value - old_value) / old_value


def calculate_position_size(account_balance: float, risk_per_trade: float, 
                          entry_price: float, stop_loss_price: float) -> Dict[str, float]:
    """
    Calcular tamanho da posição baseado no risco
    
    Args:
        account_balance: Saldo da conta
        risk_per_trade: Risco por trade (decimal, ex: 0.02 = 2%)
        entry_price: Preço de entrada
        stop_loss_price: Preço do stop loss
        
    Returns:
        Dict com informações da posição
    """
    if entry_price <= 0 or stop_loss_price <= 0:
        raise ValueError("Prices must be positive")
    
    if entry_price == stop_loss_price:
        raise ValueError("Entry and stop loss prices cannot be equal")
    
    # Calcular risco por unidade
    risk_per_unit = abs(entry_price - stop_loss_price)
    
    # Calcular valor total de risco
    total_risk_amount = account_balance * risk_per_trade
    
    # Calcular quantidade
    quantity = total_risk_amount / risk_per_unit
    
    # Calcular valor da posição
    position_value = quantity * entry_price
    
    # Calcular risco real (pode ser menor devido a arredondamentos)
    actual_risk = quantity * risk_per_unit
    actual_risk_percentage = actual_risk / account_balance
    
    return {
        "quantity": round(quantity, 8),
        "position_value": round(position_value, 2),
        "risk_amount": round(actual_risk, 2),
        "risk_percentage": round(actual_risk_percentage, 4),
        "risk_per_unit": round(risk_per_unit, 2)
    }


def aggregate_ohlcv_data(data: List[Dict[str, Any]], target_timeframe: str) -> List[Dict[str, Any]]:
    """
    Agregar dados OHLCV para timeframe maior
    
    Args:
        data: Lista de dados OHLCV
        target_timeframe: Timeframe alvo
        
    Returns:
        Dados agregados
    """
    if not data:
        return []
    
    # Converter para DataFrame para facilitar agregação
    df = pd.DataFrame(data)
    
    # Converter timestamp para datetime se necessário
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
    
    # Mapear timeframe para pandas frequency
    freq_map = {
        '1m': '1T', '3m': '3T', '5m': '5T', '15m': '15T', '30m': '30T',
        '1h': '1H', '2h': '2H', '4h': '4H', '6h': '6H', '8h': '8H', '12h': '12H',
        '1d': '1D', '3d': '3D', '1w': '1W', '1M': '1M'
    }
    
    freq = freq_map.get(target_timeframe)
    if not freq:
        raise ValueError(f"Unsupported timeframe: {target_timeframe}")
    
    # Agregar dados
    aggregated = df.resample(freq).agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    }).dropna()
    
    # Converter de volta para lista de dicts
    result = []
    for timestamp, row in aggregated.iterrows():
        result.append({
            'timestamp': timestamp.isoformat(),
            'open': float(row['open']),
            'high': float(row['high']),
            'low': float(row['low']),
            'close': float(row['close']),
            'volume': float(row['volume'])
        })
    
    return result


def calculate_support_resistance_levels(prices: List[float], window: int = 20) -> Dict[str, List[float]]:
    """
    Calcular níveis de suporte e resistência
    
    Args:
        prices: Lista de preços
        window: Janela para cálculo
        
    Returns:
        Dict com níveis de suporte e resistência
    """
    if len(prices) < window:
        return {"support": [], "resistance": []}
    
    prices_array = np.array(prices)
    
    # Encontrar máximos e mínimos locais
    support_levels = []
    resistance_levels = []
    
    for i in range(window, len(prices_array) - window):
        # Verificar se é mínimo local (suporte)
        if prices_array[i] == np.min(prices_array[i-window:i+window+1]):
            support_levels.append(prices_array[i])
        
        # Verificar se é máximo local (resistência)
        if prices_array[i] == np.max(prices_array[i-window:i+window+1]):
            resistance_levels.append(prices_array[i])
    
    # Remover duplicatas próximas (dentro de 1% de diferença)
    def remove_close_levels(levels: List[float], threshold: float = 0.01) -> List[float]:
        if not levels:
            return []
        
        levels_sorted = sorted(levels)
        filtered = [levels_sorted[0]]
        
        for level in levels_sorted[1:]:
            if abs(level - filtered[-1]) / filtered[-1] > threshold:
                filtered.append(level)
        
        return filtered
    
    support_levels = remove_close_levels(support_levels)
    resistance_levels = remove_close_levels(resistance_levels)
    
    return {
        "support": support_levels[-5:],  # Últimos 5 níveis
        "resistance": resistance_levels[-5:]
    }


def clean_data(data: List[Dict[str, Any]], required_fields: List[str]) -> List[Dict[str, Any]]:
    """
    Limpar dados removendo entradas inválidas
    
    Args:
        data: Lista de dados
        required_fields: Campos obrigatórios
        
    Returns:
        Dados limpos
    """
    cleaned_data = []
    
    for item in data:
        # Verificar se todos os campos obrigatórios estão presentes
        if not all(field in item for field in required_fields):
            continue
        
        # Verificar se valores numéricos são válidos
        valid_item = True
        for field in required_fields:
            value = item[field]
            
            # Se campo deve ser numérico
            if field in ['price', 'quantity', 'volume', 'open', 'high', 'low', 'close']:
                try:
                    float_value = float(value)
                    if not np.isfinite(float_value) or float_value < 0:
                        valid_item = False
                        break
                    item[field] = float_value
                except (ValueError, TypeError):
                    valid_item = False
                    break
        
        if valid_item:
            cleaned_data.append(item)
    
    return cleaned_data


def convert_to_decimal(value: Union[float, str], precision: int = 8) -> Decimal:
    """
    Converter para Decimal para cálculos precisos
    
    Args:
        value: Valor a ser convertido
        precision: Precisão decimal
        
    Returns:
        Valor Decimal
    """
    try:
        decimal_value = Decimal(str(value))
        return decimal_value.quantize(Decimal('0.' + '0' * precision), rounding=ROUND_HALF_UP)
    except (ValueError, TypeError):
        return Decimal('0')


def batch_process_data(data: List[Any], batch_size: int = 1000, 
                      processor_func: callable = None) -> List[Any]:
    """
    Processar dados em lotes
    
    Args:
        data: Dados a serem processados
        batch_size: Tamanho do lote
        processor_func: Função de processamento
        
    Returns:
        Dados processados
    """
    if not processor_func:
        return data
    
    processed_data = []
    
    for i in range(0, len(data), batch_size):
        batch = data[i:i + batch_size]
        try:
            processed_batch = processor_func(batch)
            processed_data.extend(processed_batch)
        except Exception as e:
            logger.error(f"Error processing batch {i//batch_size + 1}: {e}")
            # Continuar com próximo lote em caso de erro
            continue
    
    return processed_data


def merge_market_data(data1: List[Dict], data2: List[Dict], 
                     key_field: str = 'timestamp') -> List[Dict]:
    """
    Mesclar dados de mercado por timestamp
    
    Args:
        data1: Primeira lista de dados
        data2: Segunda lista de dados
        key_field: Campo chave para mesclagem
        
    Returns:
        Dados mesclados
    """
    # Converter para DataFrames
    df1 = pd.DataFrame(data1)
    df2 = pd.DataFrame(data2)
    
    if df1.empty or df2.empty:
        return data1 if not df1.empty else data2
    
    # Mesclar por timestamp
    merged_df = pd.merge(df1, df2, on=key_field, how='outer', suffixes=('_1', '_2'))
    
    # Converter de volta para lista de dicts
    return merged_df.to_dict('records')


def detect_outliers(data: List[float], method: str = 'iqr', threshold: float = 1.5) -> List[int]:
    """
    Detectar outliers nos dados
    
    Args:
        data: Lista de valores
        method: Método de detecção ('iqr', 'zscore')
        threshold: Threshold para detecção
        
    Returns:
        Índices dos outliers
    """
    if len(data) < 4:
        return []
    
    data_array = np.array(data)
    outlier_indices = []
    
    if method == 'iqr':
        Q1 = np.percentile(data_array, 25)
        Q3 = np.percentile(data_array, 75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - threshold * IQR
        upper_bound = Q3 + threshold * IQR
        
        outlier_indices = [i for i, value in enumerate(data_array) 
                          if value < lower_bound or value > upper_bound]
    
    elif method == 'zscore':
        mean = np.mean(data_array)
        std = np.std(data_array)
        
        if std > 0:
            z_scores = np.abs((data_array - mean) / std)
            outlier_indices = [i for i, z_score in enumerate(z_scores) 
                              if z_score > threshold]
    
    return outlier_indices


def interpolate_missing_data(data: List[Dict], time_field: str = 'timestamp', 
                           value_fields: List[str] = None) -> List[Dict]:
    """
    Interpolar dados faltantes
    
    Args:
        data: Dados com possíveis lacunas
        time_field: Campo de tempo
        value_fields: Campos de valor para interpolar
        
    Returns:
        Dados com lacunas preenchidas
    """
    if not data or len(data) < 2:
        return data
    
    df = pd.DataFrame(data)
    
    # Converter timestamp para datetime
    df[time_field] = pd.to_datetime(df[time_field])
    df.set_index(time_field, inplace=True)
    
    # Campos padrão se não especificados
    if value_fields is None:
        value_fields = [col for col in df.columns if col in ['price', 'close', 'volume']]
    
    # Interpolar valores faltantes
    for field in value_fields:
        if field in df.columns:
            df[field] = df[field].interpolate(method='linear')
    
    # Converter de volta
    df.reset_index(inplace=True)
    df[time_field] = df[time_field].dt.isoformat()
    
    return df.to_dict('records')


# Exportar funções principais
__all__ = [
    # Formatação
    'format_currency',
    'format_percentage', 
    'format_datetime',
    'format_number',
    
    # Validação
    'validate_symbol',
    'validate_timeframe',
    'validate_side',
    'validate_order_type',
    'validate_price',
    'validate_quantity',
    
    # Sanitização
    'sanitize_numeric_input',
    
    # Cálculos
    'parse_timeframe',
    'calculate_percentage_change',
    'calculate_position_size',
    'calculate_support_resistance_levels',
    
    # Processamento de dados
    'aggregate_ohlcv_data',
    'clean_data',
    'convert_to_decimal',
    'batch_process_data',
    'merge_market_data',
    'detect_outliers',
    'interpolate_missing_data',
    
    # Constantes
    'VALID_TIMEFRAMES',
    'VALID_SIDES',
    'VALID_ORDER_TYPES',
]

