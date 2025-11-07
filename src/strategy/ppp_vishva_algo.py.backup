            return True
        else:
            return False
    
    def analyze_pullback_reversal(self, signals: Dict[str, int]) -> bool:
        """
        Analisa reversão em pullback com Stoch RSI
        
        Args:
            signals: Sinais dos indicadores
            
        Returns:
            True se há confirmação de reversão
        """
        stoch_rsi_signal = signals.get('stoch_rsi', 0)
        ut_bot_signal = signals.get('ut_bot', 0)
        
        # Stoch RSI deve confirmar a direção do UT Bot
        if ut_bot_signal == 1 and stoch_rsi_signal == 1:
            return True
        elif ut_bot_signal == -1 and stoch_rsi_signal == -1:
            return True
        else:
            return False
    
    def analyze_multi_timeframe_validation(self, symbol: str) -> bool:
        """
        Analisa validação multi-timeframe (EMA20 + Heikin Ashi)
        
        Args:
            symbol: Símbolo do ativo
            
        Returns:
            True se a validação multi-timeframe confirma
        """
        try:
            # Obter dados de timeframes maiores (4h e diário)
            data_4h = self.get_market_data(symbol, "240", 50)  # 4h
            data_1d = self.get_market_data(symbol, "D", 30)    # Diário
            
            if not data_4h or not data_1d:
                return False
            
            # Analisar sinais em timeframes maiores
            signals_4h = self.indicators.get_signals(data_4h)
            signals_1d = self.indicators.get_signals(data_1d)
            
            # Verificar alinhamento de tendência
            ema20_4h = signals_4h.get('ema100_trend', 0)  # Usar EMA100 como proxy
            ema20_1d = signals_1d.get('ema100_trend', 0)
            ha_4h = signals_4h.get('heikin_ashi', 0)
            ha_1d = signals_1d.get('heikin_ashi', 0)
            
            # Tendência deve estar alinhada em pelo menos um timeframe maior
            return (ema20_4h != 0 and ha_4h != 0) or (ema20_1d != 0 and ha_1d != 0)
            
        except Exception as e:
            self.logger.error(f"Erro na validação multi-timeframe: {e}")
            return False
    
    def check_entry_conditions(self, symbol: str) -> Tuple[SignalType, Dict]:
        """
        Verifica todas as condições de entrada
        
        Args:
            symbol: Símbolo do ativo
            
        Returns:
            Tupla com (tipo_de_sinal, dados_adicionais)
        """
        try:
            # Obter dados de mercado
            kline_data = self.get_market_data(symbol, self.timeframe)
            if not kline_data:
                return SignalType.NONE, {}
            
            # Calcular indicadores e sinais
            signals = self.indicators.get_signals(kline_data)
            if not signals:
                return SignalType.NONE, {}
            
            # Obter preço atual e EMA100
            data = self.indicators.get_indicator('ema100').prepare_data(kline_data)
            current_price = float(kline_data[0][4])  # Close do último candle
            ema100_values = self.indicators.get_indicator('ema100').calculate(data)
            current_ema100 = ema100_values.iloc[-1]
            
            # 1. Verificar filtro de tendência EMA100
            if not self.analyze_trend_filter(signals, current_price, current_ema100):
                return SignalType.NONE, {}
            
            # 2. Verificar sinais de entrada do UT Bot
            entry_signal = self.analyze_entry_signals(signals)
            if entry_signal == SignalType.NONE:
                return SignalType.NONE, {}
            
            # 3. Verificar confirmação de momentum (EWO)
            if not self.analyze_momentum_confirmation(signals):
                return SignalType.NONE, {}
            
            # 4. Verificar reversão em pullback (Stoch RSI)
            if not self.analyze_pullback_reversal(signals):
                return SignalType.NONE, {}
            
            # 5. Verificar validação multi-timeframe
            if not self.analyze_multi_timeframe_validation(symbol):
                return SignalType.NONE, {}
            
            # Todas as condições atendidas
            additional_data = {
                'current_price': current_price,
                'ema100': current_ema100,
                'signals': signals,
                'atr': self._calculate_atr(data)
            }
            
            self.logger.info(f"Sinal de entrada confirmado para {symbol}: {entry_signal}")
            return entry_signal, additional_data
            
        except Exception as e:
            self.logger.error(f"Erro ao verificar condições de entrada para {symbol}: {e}")
            return SignalType.NONE, {}
    
    def _calculate_atr(self, data) -> float:
        """
        Calcula ATR atual para gerenciamento de risco
        
        Args:
            data: DataFrame com dados OHLCV
            
        Returns:
            Valor do ATR
        """
        try:
            atr_indicator = self.indicators.get_indicator('ut_bot').atr
            atr_values = atr_indicator.calculate(data)
            return atr_values.iloc[-1]
        except:
            return 0.0
    
    def calculate_position_size(self, symbol: str, current_price: float, atr: float) -> float:
        """
        Calcula tamanho da posição baseado no risco
        
        Args:
            symbol: Símbolo do ativo
            current_price: Preço atual
            atr: Valor do ATR
            
        Returns:
            Tamanho da posição
        """
        max_position_size = self.config.get('risk_management.max_position_size', 0.01)
        
        # Por enquanto, usar tamanho fixo
        # TODO: Implementar cálculo baseado em % do capital e ATR
        return max_position_size
    
    def calculate_stop_loss(self, entry_price: float, atr: float, side: PositionSide) -> float:
        """
        Calcula stop loss baseado no ATR
        
        Args:
            entry_price: Preço de entrada
            atr: Valor do ATR
            side: Lado da posição
            
        Returns:
            Preço do stop loss
        """
        sl_distance = atr * self.sl_ratio
        
        if side == PositionSide.LONG:
            return entry_price - sl_distance
        else:
            return entry_price + sl_distance
    
    def calculate_take_profit(self, entry_price: float, stop_loss: float, side: PositionSide) -> float:
        """
        Calcula take profit dinâmico
        
        Args:
            entry_price: Preço de entrada
            stop_loss: Preço do stop loss
            side: Lado da posição
            
        Returns:
            Preço do take profit
        """
        risk = abs(entry_price - stop_loss)
        reward_ratio = 2.0  # Risk:Reward 1:2
        
        if side == PositionSide.LONG:
            return entry_price + (risk * reward_ratio)
        else:
            return entry_price - (risk * reward_ratio)
    
    def execute_entry(self, symbol: str, signal: SignalType, additional_data: Dict) -> bool:
        """
        Executa entrada na posição
        
        Args:
            symbol: Símbolo do ativo
            signal: Tipo de sinal
            additional_data: Dados adicionais
            
        Returns:
            True se a entrada foi executada com sucesso
        """
        try:
            current_price = additional_data['current_price']
            atr = additional_data['atr']
            
            # Determinar lado da posição
            side = PositionSide.LONG if signal == SignalType.BUY else PositionSide.SHORT
            order_side = "Buy" if signal == SignalType.BUY else "Sell"
            
            # Calcular parâmetros da posição
            position_size = self.calculate_position_size(symbol, current_price, atr)
            stop_loss = self.calculate_stop_loss(current_price, atr, side)
            take_profit = self.calculate_take_profit(current_price, stop_loss, side)
            
            # Executar ordem de mercado
            order_result = self.client.place_order(
                symbol=symbol,
                side=order_side,
                order_type="Market",
                qty=str(position_size),
                stopLoss=str(stop_loss),
                takeProfit=str(take_profit)
            )
            
            if order_result:
                # Registrar posição
                self.positions[symbol] = {
                    'side': side,
                    'entry_price': current_price,
                    'size': position_size,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'pyramid_level': 1,
                    'entry_time': datetime.utcnow()
                }
                
                self.pyramid_levels[symbol] = 1
                
                self.logger.info(f"Entrada executada: {symbol} {side.value} @ {current_price}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Erro ao executar entrada: {e}")
            return False
    
    def check_exit_conditions(self, symbol: str) -> bool:
        """
        Verifica condições de saída
        
        Args:
            symbol: Símbolo do ativo
            
        Returns:
            True se deve sair da posição
        """
        if symbol not in self.positions:
            return False
        
        try:
            # Obter sinais atuais
            kline_data = self.get_market_data(symbol, self.timeframe)
            signals = self.indicators.get_signals(kline_data)
            
            position = self.positions[symbol]
            ut_bot_signal = signals.get('ut_bot', 0)
            
            # Sair se o UT Bot reverter o sinal
            if position['side'] == PositionSide.LONG and ut_bot_signal == -1:
                return True
            elif position['side'] == PositionSide.SHORT and ut_bot_signal == 1:
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Erro ao verificar condições de saída: {e}")
            return False
    
    def execute_exit(self, symbol: str) -> bool:
        """
        Executa saída da posição
        
        Args:
            symbol: Símbolo do ativo
            
        Returns:
            True se a saída foi executada com sucesso
        """
        if symbol not in self.positions:
            return False
        
        try:
            position = self.positions[symbol]
            
            # Determinar lado da ordem de fechamento
            order_side = "Sell" if position['side'] == PositionSide.LONG else "Buy"
            
            # Executar ordem de fechamento
            order_result = self.client.place_order(
                symbol=symbol,
                side=order_side,
                order_type="Market",
                qty=str(position['size']),
                reduceOnly=True
            )
            
            if order_result:
                self.logger.info(f"Saída executada: {symbol} {position['side'].value}")
                
                # Remover posição
                del self.positions[symbol]
                if symbol in self.pyramid_levels:
                    del self.pyramid_levels[symbol]
                
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Erro ao executar saída: {e}")
            return False
    
    def run_cycle(self):
        """
        Executa um ciclo completo da estratégia
        """
        if not self.is_trading_session():
            return
        
        try:
            for symbol in self.symbols:
                # Verificar se já tem posição
                if symbol in self.positions:
                    # Verificar condições de saída
                    if self.check_exit_conditions(symbol):
                        self.execute_exit(symbol)
                else:
                    # Verificar condições de entrada
                    signal, additional_data = self.check_entry_conditions(symbol)
                    if signal != SignalType.NONE:
                        self.execute_entry(symbol, signal, additional_data)
                
                # Pequena pausa entre símbolos
                time.sleep(0.5)
                
        except Exception as e:
            self.logger.error(f"Erro no ciclo da estratégia: {e}")
    
    def get_positions_status(self) -> Dict:
        """
        Obtém status das posições atuais
        
        Returns:
            Dicionário com status das posições
        """
        return self.positions.copy()

