# 🤝 Guia de Contribuição - MVP Bot de Trading

Obrigado por seu interesse em contribuir para o MVP Bot de Trading! Este documento fornece diretrizes para contribuições efetivas e colaboração produtiva.

## 📋 Índice

- [Como Contribuir](#como-contribuir)
- [Processo de Desenvolvimento](#processo-de-desenvolvimento)
- [Padrões de Código](#padrões-de-código)
- [Testes](#testes)
- [Documentação](#documentação)
- [Reportar Bugs](#reportar-bugs)
- [Solicitar Features](#solicitar-features)
- [Pull Requests](#pull-requests)
- [Código de Conduta](#código-de-conduta)
- [Reconhecimento](#reconhecimento)

## 🚀 Como Contribuir

### Tipos de Contribuição

Aceitamos vários tipos de contribuição:

- 🐛 **Correção de bugs**
- ✨ **Novas funcionalidades**
- 📚 **Melhorias na documentação**
- 🧪 **Testes adicionais**
- 🎨 **Melhorias na interface**
- 📊 **Novas estratégias de trading**
- 🔧 **Otimizações de performance**
- 🛡️ **Melhorias de segurança**

### Primeiros Passos

1. **Fork** o repositório
2. **Clone** seu fork localmente
3. **Configure** o ambiente de desenvolvimento
4. **Crie** uma branch para sua contribuição
5. **Faça** suas alterações
6. **Teste** suas alterações
7. **Submeta** um Pull Request

```bash
# 1. Fork no GitHub, depois clone
git clone https://github.com/SEU_USUARIO/crypto-trading-mvp.git
cd crypto-trading-mvp

# 2. Configure o ambiente
./scripts/setup.sh

# 3. Crie uma branch
git checkout -b feature/nova-funcionalidade

# 4. Faça suas alterações
# ... código ...

# 5. Teste
python -m pytest tests/
./scripts/deploy.sh --health-check

# 6. Commit e push
git add .
git commit -m "feat: adiciona nova funcionalidade"
git push origin feature/nova-funcionalidade

# 7. Abra Pull Request no GitHub
```

## 🔄 Processo de Desenvolvimento

### Workflow Git

Seguimos o **Git Flow** simplificado:

- `main`: Código de produção estável
- `develop`: Código de desenvolvimento
- `feature/*`: Novas funcionalidades
- `bugfix/*`: Correções de bugs
- `hotfix/*`: Correções urgentes para produção

### Convenção de Commits

Usamos [Conventional Commits](https://www.conventionalcommits.org/):

```
<tipo>[escopo opcional]: <descrição>

[corpo opcional]

[rodapé opcional]
```

**Tipos:**
- `feat`: Nova funcionalidade
- `fix`: Correção de bug
- `docs`: Documentação
- `style`: Formatação (não afeta lógica)
- `refactor`: Refatoração de código
- `test`: Testes
- `chore`: Tarefas de manutenção

**Exemplos:**
```
feat(bot): adiciona estratégia Bollinger Bands
fix(api): corrige erro de autenticação JWT
docs(readme): atualiza instruções de instalação
test(strategies): adiciona testes para RSI
```

### Branches

**Nomenclatura:**
- `feature/nome-da-funcionalidade`
- `bugfix/descricao-do-bug`
- `hotfix/correcao-urgente`
- `docs/atualizacao-documentacao`

## 📝 Padrões de Código

### Python

Seguimos **PEP 8** com algumas adaptações:

```python
# ✅ Bom
def calculate_rsi(prices: List[float], period: int = 14) -> float:
    """
    Calcular RSI (Relative Strength Index)
    
    Args:
        prices: Lista de preços
        period: Período para cálculo (padrão: 14)
        
    Returns:
        Valor do RSI (0-100)
    """
    if len(prices) < period + 1:
        return 50.0
    
    gains = []
    losses = []
    
    for i in range(1, len(prices)):
        change = prices[i] - prices[i-1]
        if change > 0:
            gains.append(change)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(change))
    
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    
    if avg_loss == 0:
        return 100.0
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi

# ❌ Ruim
def calc_rsi(p,per=14):
    if len(p)<per+1:return 50
    g,l=[],[]
    for i in range(1,len(p)):
        c=p[i]-p[i-1]
        if c>0:g.append(c);l.append(0)
        else:g.append(0);l.append(abs(c))
    ag,al=sum(g[-per:])/per,sum(l[-per:])/per
    if al==0:return 100
    return 100-(100/(1+ag/al))
```

### Configurações de Linting

```python
# pyproject.toml
[tool.black]
line-length = 88
target-version = ['py311']

[tool.isort]
profile = "black"
multi_line_output = 3

[tool.flake8]
max-line-length = 88
extend-ignore = ["E203", "W503"]
```

### TypeScript/JavaScript

Para componentes frontend:

```typescript
// ✅ Bom
interface TradingStrategy {
  name: string;
  parameters: Record<string, number>;
  isActive: boolean;
}

const calculateMovingAverage = (
  prices: number[],
  period: number
): number => {
  if (prices.length < period) {
    throw new Error('Insufficient data points');
  }
  
  const sum = prices.slice(-period).reduce((a, b) => a + b, 0);
  return sum / period;
};

// ❌ Ruim
const calcMA = (p, per) => {
  return p.slice(-per).reduce((a,b)=>a+b)/per;
};
```

## 🧪 Testes

### Estrutura de Testes

```
tests/
├── unit/                 # Testes unitários
│   ├── test_strategies.py
│   ├── test_indicators.py
│   └── test_api.py
├── integration/          # Testes de integração
│   ├── test_bot_workflow.py
│   └── test_api_endpoints.py
├── performance/          # Testes de performance
│   └── test_strategy_speed.py
└── fixtures/            # Dados de teste
    └── sample_data.json
```

### Escrevendo Testes

```python
import pytest
from src.bot.strategies import RSIStrategy

class TestRSIStrategy:
    """Testes para estratégia RSI"""
    
    @pytest.fixture
    def sample_prices(self):
        """Preços de exemplo para testes"""
        return [100, 102, 101, 103, 105, 104, 106, 108, 107, 109]
    
    @pytest.fixture
    def rsi_strategy(self):
        """Instância da estratégia RSI"""
        return RSIStrategy(period=14, oversold=30, overbought=70)
    
    def test_rsi_calculation(self, rsi_strategy, sample_prices):
        """Testar cálculo do RSI"""
        rsi = rsi_strategy.calculate_rsi(sample_prices)
        
        assert isinstance(rsi, float)
        assert 0 <= rsi <= 100
    
    def test_buy_signal(self, rsi_strategy):
        """Testar sinal de compra"""
        # RSI baixo (oversold)
        low_rsi_prices = [100, 95, 90, 85, 80, 75, 70, 65, 60, 55]
        signal = rsi_strategy.analyze(low_rsi_prices)
        
        assert signal['action'] == 'buy'
        assert signal['confidence'] > 0.5
    
    def test_sell_signal(self, rsi_strategy):
        """Testar sinal de venda"""
        # RSI alto (overbought)
        high_rsi_prices = [100, 105, 110, 115, 120, 125, 130, 135, 140, 145]
        signal = rsi_strategy.analyze(high_rsi_prices)
        
        assert signal['action'] == 'sell'
        assert signal['confidence'] > 0.5
    
    @pytest.mark.parametrize("period", [7, 14, 21])
    def test_different_periods(self, sample_prices, period):
        """Testar diferentes períodos"""
        strategy = RSIStrategy(period=period)
        rsi = strategy.calculate_rsi(sample_prices)
        
        assert isinstance(rsi, float)
        assert 0 <= rsi <= 100
```

### Executando Testes

```bash
# Todos os testes
python -m pytest

# Testes específicos
python -m pytest tests/unit/test_strategies.py

# Com cobertura
python -m pytest --cov=src tests/

# Testes de performance
python -m pytest tests/performance/ -v
```

## 📚 Documentação

### Docstrings

Use formato **Google Style**:

```python
def calculate_sharpe_ratio(returns: List[float], risk_free_rate: float = 0.02) -> float:
    """
    Calcular Sharpe Ratio para avaliar performance ajustada ao risco.
    
    O Sharpe Ratio mede o retorno em excesso por unidade de risco,
    sendo uma métrica fundamental para avaliar estratégias de trading.
    
    Args:
        returns: Lista de retornos percentuais da estratégia
        risk_free_rate: Taxa livre de risco anualizada (padrão: 2%)
        
    Returns:
        Sharpe ratio calculado (valores maiores são melhores)
        
    Raises:
        ValueError: Se a lista de retornos estiver vazia
        ZeroDivisionError: Se o desvio padrão for zero
        
    Example:
        >>> returns = [0.01, 0.02, -0.01, 0.03, 0.00]
        >>> sharpe = calculate_sharpe_ratio(returns)
        >>> print(f"Sharpe Ratio: {sharpe:.2f}")
        Sharpe Ratio: 1.23
        
    Note:
        - Retornos devem estar em formato decimal (0.01 = 1%)
        - Taxa livre de risco é anualizada automaticamente
        - Valores acima de 1.0 são considerados bons
    """
```

### README e Documentação

- Mantenha o README atualizado
- Documente novas funcionalidades
- Inclua exemplos de uso
- Atualize diagramas se necessário

## 🐛 Reportar Bugs

### Template de Bug Report

```markdown
**Descrição do Bug**
Descrição clara e concisa do problema.

**Reproduzir**
Passos para reproduzir o comportamento:
1. Vá para '...'
2. Clique em '....'
3. Role para baixo até '....'
4. Veja o erro

**Comportamento Esperado**
Descrição clara do que deveria acontecer.

**Screenshots**
Se aplicável, adicione screenshots.

**Ambiente:**
 - OS: [e.g. Ubuntu 22.04]
 - Python: [e.g. 3.11]
 - Versão: [e.g. 1.0.0]

**Contexto Adicional**
Qualquer outro contexto sobre o problema.
```

### Informações Importantes

- **Logs relevantes**
- **Configuração do ambiente**
- **Dados de entrada** (se possível)
- **Comportamento esperado vs atual**

## ✨ Solicitar Features

### Template de Feature Request

```markdown
**Sua solicitação de feature está relacionada a um problema?**
Descrição clara e concisa do problema. Ex: Estou sempre frustrado quando [...]

**Descreva a solução que você gostaria**
Descrição clara e concisa do que você quer que aconteça.

**Descreva alternativas consideradas**
Descrição clara e concisa de soluções alternativas ou features consideradas.

**Contexto adicional**
Qualquer outro contexto ou screenshots sobre a solicitação.
```

### Critérios de Aceitação

- **Utilidade geral** para a comunidade
- **Alinhamento** com objetivos do projeto
- **Viabilidade técnica**
- **Impacto na performance**
- **Complexidade de manutenção**

## 🔄 Pull Requests

### Checklist do PR

Antes de submeter, verifique:

- [ ] **Código** segue padrões estabelecidos
- [ ] **Testes** passam (`python -m pytest`)
- [ ] **Linting** sem erros (`flake8`, `black`)
- [ ] **Documentação** atualizada
- [ ] **Changelog** atualizado (se aplicável)
- [ ] **Commits** seguem convenção
- [ ] **Branch** atualizada com `main`

### Template de PR

```markdown
## Descrição
Breve descrição das mudanças.

## Tipo de Mudança
- [ ] Bug fix (mudança que corrige um problema)
- [ ] Nova feature (mudança que adiciona funcionalidade)
- [ ] Breaking change (correção ou feature que causa mudança incompatível)
- [ ] Documentação

## Como Foi Testado?
Descreva os testes realizados.

## Checklist:
- [ ] Meu código segue os padrões do projeto
- [ ] Realizei auto-review do código
- [ ] Comentei código em partes complexas
- [ ] Fiz mudanças correspondentes na documentação
- [ ] Minhas mudanças não geram novos warnings
- [ ] Adicionei testes que provam que minha correção/feature funciona
- [ ] Testes novos e existentes passam localmente
```

### Processo de Review

1. **Automated checks** devem passar
2. **Code review** por pelo menos 1 maintainer
3. **Testing** em ambiente de desenvolvimento
4. **Approval** e merge

## 📜 Código de Conduta

### Nossos Padrões

**Comportamentos que contribuem para um ambiente positivo:**

- Usar linguagem acolhedora e inclusiva
- Respeitar diferentes pontos de vista e experiências
- Aceitar críticas construtivas graciosamente
- Focar no que é melhor para a comunidade
- Mostrar empatia com outros membros da comunidade

**Comportamentos inaceitáveis:**

- Uso de linguagem ou imagens sexualizadas
- Trolling, comentários insultuosos/depreciativos
- Assédio público ou privado
- Publicar informações privadas de outros sem permissão
- Outras condutas consideradas inapropriadas

### Aplicação

Instâncias de comportamento abusivo, de assédio ou inaceitável podem ser reportadas entrando em contato com a equipe do projeto. Todas as reclamações serão revisadas e investigadas.

## 🏆 Reconhecimento

### Contribuidores

Reconhecemos todos os tipos de contribuição:

- **Code Contributors**: Código, correções, features
- **Documentation Contributors**: Documentação, tutoriais
- **Community Contributors**: Suporte, moderação
- **Testing Contributors**: Testes, QA, bug reports
- **Design Contributors**: UI/UX, assets visuais

### Hall of Fame

Contribuidores destacados serão reconhecidos em:

- README principal
- Página de contribuidores
- Release notes
- Redes sociais do projeto

## 📞 Canais de Comunicação

### Onde Buscar Ajuda

- **GitHub Issues**: Bugs e feature requests
- **GitHub Discussions**: Perguntas gerais e discussões
- **Discord**: Chat em tempo real (se disponível)
- **Email**: contato@projeto.com (para questões sensíveis)

### Tempo de Resposta

- **Issues críticos**: 24-48 horas
- **Pull Requests**: 3-5 dias úteis
- **Perguntas gerais**: 1 semana
- **Feature requests**: 2 semanas

## 🎯 Roadmap de Contribuições

### Prioridades Atuais

1. **Novas Estratégias**: Bollinger Bands, MACD, Stochastic
2. **Melhorias de Performance**: Otimização de indicadores
3. **Testes**: Aumentar cobertura para 90%+
4. **Documentação**: Tutoriais e guias avançados
5. **Segurança**: Auditoria e melhorias

### Como Escolher uma Tarefa

1. Verifique **Issues** marcadas como `good first issue`
2. Procure por **TODOs** no código
3. Consulte o **Project Board**
4. Proponha suas próprias ideias

---

**Obrigado por contribuir para o MVP Bot de Trading! 🚀**

Sua contribuição ajuda a construir uma ferramenta melhor para toda a comunidade de trading algorítmico.

