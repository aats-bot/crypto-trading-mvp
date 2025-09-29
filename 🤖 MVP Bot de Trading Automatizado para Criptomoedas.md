# 🤖 MVP Bot de Trading Automatizado para Criptomoedas

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)

## 🎯 **Visão Geral**

Sistema completo de bot de trading automatizado para criptomoedas com:
- 🔗 **Integração Bybit** - API oficial para trading real
- 👥 **Multi-tenant** - Suporte a múltiplos clientes
- 📊 **3 Estratégias** - SMA, RSI e PPP Vishva avançada
- 🎨 **Dashboard** - Interface web profissional
- 🔒 **Segurança** - Criptografia e gestão de riscos
- 🐳 **Docker** - Deploy simplificado

## 🚀 **Quick Start**

### 1. **Instalação**
```bash
git clone <repository>
cd crypto-trading-mvp
pip install -r requirements.txt
```

### 2. **Configuração**
```bash
cp .env.example .env
# Editar .env com suas chaves API
```

### 3. **Execução**
```bash
python start_services.py
```

### 4. **Acesso**
- 🎨 **Dashboard**: http://localhost:8501
- 🌐 **API**: http://localhost:8000/docs

## 📊 **Estratégias Disponíveis**

### 1. **SMA (Simple Moving Average)**
- 📈 Cruzamento de médias móveis
- ⚙️ Configurável: períodos rápido/lento
- 🎯 Ideal para: Tendências claras

### 2. **RSI (Relative Strength Index)**
- 📉 Reversão à média
- ⚙️ Configurável: período, níveis sobrecompra/sobrevenda
- 🎯 Ideal para: Mercados laterais

### 3. **PPP Vishva (Avançada)**
- 🔬 Multi-indicadores: EMA100, UT Bot, EWO, Stoch RSI
- 📊 Validação multi-timeframe
- ⚠️ Gerenciamento de risco dinâmico
- 🎯 Ideal para: Trading profissional

## 🏗️ **Arquitetura**

```
🤖 Bot Core ←→ 🌐 FastAPI ←→ 🎨 Streamlit
     ↓              ↓              ↓
🔗 Bybit API   🗄️ Database   👤 Usuários
```

### **Componentes Principais:**
- **Bot Core**: Engine de trading e estratégias
- **FastAPI**: API REST para comunicação
- **Streamlit**: Dashboard web interativo
- **Database**: Dados de clientes e trading
- **Security**: Criptografia e autenticação

## 📁 **Estrutura do Projeto**

```
crypto-trading-mvp/
├── 📋 project-management/     # Gestão do projeto
├── 📖 docs/                   # Documentação
├── ⚙️ config/                 # Configurações
├── 🤖 src/bot/                # Core do bot
├── 🌐 src/api/                # API FastAPI
├── 🎨 src/dashboard/          # Dashboard Streamlit
├── 📊 src/strategy/           # Estratégias e indicadores
├── 🔒 src/security/           # Segurança
├── 🗄️ src/models/             # Modelos de dados
├── 🧪 tests/                  # Testes
├── 🐳 docker/                 # Containers
└── 🚀 deployment/             # Deploy
```

## 🔧 **Configuração Avançada**

### **Variáveis de Ambiente (.env)**
```env
# Bybit API
BYBIT_API_KEY=your_api_key
BYBIT_API_SECRET=your_api_secret
BYBIT_TESTNET=true

# Database
DATABASE_URL=sqlite:///./data/database/trading_bot.db

# Security
SECRET_KEY=your_secret_key
ENCRYPTION_KEY=your_encryption_key

# Services
API_PORT=8000
STREAMLIT_PORT=8501
```

### **Docker Compose**
```bash
docker-compose up -d
```

## 📊 **Monitoramento**

### **Logs**
- 📝 API: `logs/api/`
- 🤖 Bot: `logs/bot/`
- 🎨 Dashboard: `logs/dashboard/`

### **Métricas**
- 📈 Prometheus: http://localhost:9090
- 📊 Grafana: http://localhost:3000

## 🧪 **Testes**

```bash
# Testes unitários
pytest tests/unit/

# Testes de integração
pytest tests/integration/

# Teste específico PPP Vishva
python tests/integration/test_ppp_vishva.py
```

## 🔒 **Segurança**

- 🔐 **Criptografia AES-256** para chaves API
- 🔑 **JWT tokens** para autenticação
- 🛡️ **Rate limiting** e validação
- 📋 **Auditoria** completa de operações

## ⚠️ **Gerenciamento de Risco**

- 💰 **Position sizing** baseado em capital
- 🛑 **Stop loss** automático
- 📈 **Take profit** dinâmico
- 🚫 **Limites diários** de perda
- 📊 **Diversificação** de posições

## 📖 **Documentação**

- 📁 **Estrutura**: [docs/📁 Estrutura Completa do Projeto MVP Bot de Trading.md](docs/📁%20Estrutura%20Completa%20do%20Projeto%20MVP%20Bot%20de%20Trading.md)
- 📋 **Organização**: [docs/📁 Guia de Organização de Arquivos - MVP Bot de Trading.md](docs/📁%20Guia%20de%20Organização%20de%20Arquivos%20-%20MVP%20Bot%20de%20Trading.md)
- 📊 **Análise**: [docs/MISSING_FILES_ANALYSIS.md](docs/MISSING_FILES_ANALYSIS.md)

## 🤝 **Contribuição**

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-estrategia`)
3. Commit suas mudanças (`git commit -am 'Add nova estratégia'`)
4. Push para a branch (`git push origin feature/nova-estrategia`)
5. Abra um Pull Request

## 📋 **Roadmap**

- ✅ **MVP 1.0**: Sistema completo funcional
- 🔄 **V2.0**: Backtesting e otimização
- 🔮 **V3.0**: Machine Learning e copy trading

## ⚖️ **Licença**

Este projeto está sob a licença MIT. Veja [LICENSE](LICENSE) para detalhes.

## ⚠️ **Disclaimer**

**AVISO IMPORTANTE**: Este software é para fins educacionais e de demonstração. Trading de criptomoedas envolve riscos significativos. Use por sua própria conta e risco.

---

**Desenvolvido com ❤️ para a comunidade de trading**

