"""
Gerenciador de indicadores técnicos - VERSÃO ULTRA-CORRIGIDA
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, Any, List
from datetime import datetime, timedelta

class IndicatorManager:
    """Gerencia todos os indicadores técnicos"""
    
    def __init__(self, config_manager):
        """
        Inicializa o gerenciador de indicadores
        
        Args:
            config_manager: Instância do ConfigManager
        """
        self.config = config_manager
        self.logger = logging.getLogger(__name__)
        self.indicators = {}
        
        self._initialize_indicators()
        
    def _initialize_indicators(self):
        """Inicializa todos os indicadores necessários"""
        try:
            from .ema import EMA100, EMA20
            from .ut_bot import UTBot
            from .ewo import EWO
            from .stoch_rsi import StochRSI
            from .heikin_ashi import HeikinAshi
            
            # EMA100 para filtro de tendência
            ema100_config = self.config.get_indicator_config('ema100')
            self.indicators['ema100'] = EMA100(ema100_config)
            
            # UT Bot para sinais de entrada
            ut_bot_config = self.config.get_indicator_config('ut_bot')
            self.indicators['ut_bot'] = UTBot(ut_bot_config)
            
            # EWO para confirmação de momentum
            ewo_config = self.config.get_indicator_config('ewo')
            self.indicators['ewo'] = EWO(ewo_config)
            
            # Stochastic RSI para reversão em pullback
            stoch_rsi_config = self.config.get_indicator_config('stoch_rsi')
            self.indicators['stoch_rsi'] = StochRSI(stoch_rsi_config)
            
            # EMA20 para validação multi-timeframe
            ema20_config = self.config.get_indicator_config('ema20')
            self.indicators['ema20'] = EMA20(ema20_config)
            
            # Heikin Ashi para validação de tendência
            self.indicators['heikin_ashi'] = HeikinAshi({})
            
            self.logger.info("Indicadores inicializados com sucesso")
            
        except Exception as e:
            self.logger.error(f"Erro ao inicializar indicadores: {e}")
            raise
    
    def prepare_data_safe(self, kline_data: List[List]) -> pd.DataFrame:
        """
        Converte dados de kline da API em DataFrame de forma segura
        CORREÇÃO CRÍTICA: Resolve erro "DataFrame is ambiguous"
        
        Args:
            kline_data: Lista de dados de kline da API Bybit
            
        Returns:
            DataFrame formatado e limpo
        """
        try:
            # CORREÇÃO: Verificação explícita de dados vazios
            if not kline_data:
                self.logger.error("Lista de kline_data está vazia")
                return pd.DataFrame()
            
            if len(kline_data) == 0:
                self.logger.error("Lista de kline_data tem comprimento zero")
                return pd.DataFrame()
            
            # Detectar número de colunas automaticamente
            first_row = kline_data[0]
            if len(first_row) == 6:
                columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
            elif len(first_row) == 7:
                columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'turnover']
            else:
                self.logger.error(f"Formato de dados inesperado: {len(first_row)} colunas")
                return pd.DataFrame()
            
            df = pd.DataFrame(kline_data, columns=columns)
            
            # CORREÇÃO: Verificação explícita de DataFrame vazio
            if df.empty:
                self.logger.error("DataFrame criado está vazio")
                return pd.DataFrame()
            
            if len(df) == 0:
                self.logger.error("DataFrame criado tem 0 linhas")
                return pd.DataFrame()
            
            # Limpar dados antes de qualquer conversão
            numeric_columns = ['open', 'high', 'low', 'close', 'volume']
            if 'turnover' in df.columns:
                numeric_columns.append('turnover')
            
            # Converter para numérico
            for col in numeric_columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Limpar valores infinitos e NaN
            df = df.replace([np.inf, -np.inf], np.nan)
            df = df.ffill()  # Forward fill
            df = df.fillna(0)  # Preencher NaN restantes
            
            # Tratar timestamp
            try:
                df['timestamp'] = pd.to_numeric(df['timestamp'], errors='coerce')
                
                # Verificar se há timestamps válidos
                valid_timestamps = df['timestamp'].notna().sum()
                if valid_timestamps == 0:
                    # Gerar timestamps sequenciais
                    self.logger.warning("Todos os timestamps são inválidos, gerando sequenciais")
                    end_time = datetime.now()
                    start_time = end_time - timedelta(minutes=15 * len(df))
                    df['timestamp'] = pd.date_range(start=start_time, end=end_time, periods=len(df))
                else:
                    # Verificar range do timestamp
                    max_ts = df['timestamp'].max()
                    min_ts = df['timestamp'].min()
                    
                    # Se timestamps são muito grandes (microssegundos)
                    if max_ts > 1e12:
                        df['timestamp'] = df['timestamp'] / 1000
                    
                    # Se ainda muito grandes ou inválidos
                    if df['timestamp'].max() > 2e12 or df['timestamp'].min() < 1e9:
                        self.logger.warning("Timestamps fora do range válido, gerando sequenciais")
                        end_time = datetime.now()
                        start_time = end_time - timedelta(minutes=15 * len(df))
                        df['timestamp'] = pd.date_range(start=start_time, end=end_time, periods=len(df))
                    else:
                        # Converter para datetime
                        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms', errors='coerce')
                        
                        # Se conversão falhou, usar sequencial
                        if df['timestamp'].isna().any():
                            self.logger.warning("Conversão de timestamp falhou, gerando sequenciais")
                            end_time = datetime.now()
                            start_time = end_time - timedelta(minutes=15 * len(df))
                            df['timestamp'] = pd.date_range(start=start_time, end=end_time, periods=len(df))
            
            except Exception as ts_error:
                # Em caso de erro, usar timestamps sequenciais
                self.logger.warning(f"Erro no timestamp: {ts_error}, usando sequencial")
                end_time = datetime.now()
                start_time = end_time - timedelta(minutes=15 * len(df))
                df['timestamp'] = pd.date_range(start=start_time, end=end_time, periods=len(df))
            
            # Definir timestamp como índice
            df.set_index('timestamp', inplace=True)
            
            # Ordenar por timestamp
            df.sort_index(inplace=True)
            
            # Verificação final: garantir dados válidos
            for col in df.columns:
                df[col] = df[col].replace([np.inf, -np.inf], 0)
                df[col] = df[col].fillna(0)
                
                # Garantir que todos os valores são finitos
                if not np.isfinite(df[col]).all():
                    df[col] = df[col].fillna(0)
                    df[col] = df[col].replace([np.inf, -np.inf], 0)
            
            # CORREÇÃO: Verificação final explícita
            if df.empty:
                self.logger.error("DataFrame final está vazio após processamento")
                return pd.DataFrame()
            
            if len(df) < 10:
                self.logger.error(f"DataFrame final tem poucas linhas: {len(df)}")
                return pd.DataFrame()
            
            self.logger.info(f"DataFrame preparado com sucesso: {len(df)} linhas")
            return df
            
        except Exception as e:
            self.logger.error(f"Erro ao preparar dados: {e}")
            return pd.DataFrame()
    
    def calculate_all(self, kline_data: list) -> Dict[str, Any]:
        """
        Calcula todos os indicadores
        
        Args:
            kline_data: Dados de kline da API
            
        Returns:
            Dicionário com valores de todos os indicadores
        """
        try:
            # Usar método seguro para preparar dados
            data = self.prepare_data_safe(kline_data)
            
            # CORREÇÃO: Verificação explícita de DataFrame vazio
            if data.empty or len(data) < 100:
                self.logger.warning(f"Dados insuficientes para cálculo: {len(data)} linhas")
                return {}
            
            results = {}
            
            # Calcular cada indicador com proteção individual
            for name, indicator in self.indicators.items():
                try:
                    if name in ['ema100', 'ema20', 'ut_bot', 'ewo', 'stoch_rsi', 'heikin_ashi']:
                        results[name] = indicator.calculate(data)
                        self.logger.debug(f"Indicador {name} calculado com sucesso")
                except Exception as e:
                    self.logger.error(f"Erro ao calcular {name}: {e}")
                    results[name] = None
            
            return results
            
        except Exception as e:
            self.logger.error(f"Erro ao calcular indicadores: {e}")
            return {}
    
    def get_signals(self, kline_data: list) -> Dict[str, int]:
        """
        Obtém sinais de todos os indicadores
        
        Args:
            kline_data: Dados de kline da API
            
        Returns:
            Dicionário com sinais dos indicadores
        """
        try:
            # Usar método seguro para preparar dados
            data = self.prepare_data_safe(kline_data)
            
            # CORREÇÃO: Verificação explícita de DataFrame vazio
            if data.empty:
                self.logger.warning("DataFrame está vazio, não é possível obter sinais")
                return {}
            
            if len(data) < 100:
                self.logger.warning(f"Dados insuficientes para sinais: {len(data)} linhas")
                return {}
            
            signals = {}
            
            # Obter sinais com proteção individual
            try:
                signals['ut_bot'] = self.indicators['ut_bot'].get_signal(data)
                self.logger.debug("Sinal UT Bot obtido")
            except Exception as e:
                self.logger.error(f"Erro no UT Bot: {e}")
                signals['ut_bot'] = 0
            
            try:
                signals['ewo'] = self.indicators['ewo'].get_momentum_signal(data)
                self.logger.debug("Sinal EWO obtido")
            except Exception as e:
                self.logger.error(f"Erro no EWO: {e}")
                signals['ewo'] = 0
            
            try:
                signals['stoch_rsi'] = self.indicators['stoch_rsi'].get_reversal_signal(data)
                self.logger.debug("Sinal Stoch RSI obtido")
            except Exception as e:
                self.logger.error(f"Erro no Stoch RSI: {e}")
                signals['stoch_rsi'] = 0
            
            try:
                signals['heikin_ashi'] = self.indicators['heikin_ashi'].get_trend_signal(data)
                self.logger.debug("Sinal Heikin Ashi obtido")
            except Exception as e:
                self.logger.error(f"Erro no Heikin Ashi: {e}")
                signals['heikin_ashi'] = 0
            
            # Filtro de tendência EMA100
            try:
                ema100_values = self.indicators['ema100'].calculate(data)
                current_price = data['close'].iloc[-1]
                current_ema100 = ema100_values.iloc[-1]
                
                if current_price > current_ema100:
                    signals['ema100_trend'] = 1  # Tendência de alta
                elif current_price < current_ema100:
                    signals['ema100_trend'] = -1  # Tendência de baixa
                else:
                    signals['ema100_trend'] = 0  # Neutro
                    
                self.logger.debug("Sinal EMA100 obtido")
            except Exception as e:
                self.logger.error(f"Erro no EMA100: {e}")
                signals['ema100_trend'] = 0
            
            self.logger.info(f"Sinais obtidos com sucesso: {len(signals)} indicadores")
            return signals
            
        except Exception as e:
            self.logger.error(f"Erro ao obter sinais: {e}")
            return {}
    
    def get_indicator(self, name: str):
        """
        Obtém um indicador específico
        
        Args:
            name: Nome do indicador
            
        Returns:
            Instância do indicador
        """
        return self.indicators.get(name)

