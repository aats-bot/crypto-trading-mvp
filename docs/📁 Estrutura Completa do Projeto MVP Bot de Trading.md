# 📁 Estrutura Completa do Projeto MVP Bot de Trading

## 🏗️ Visão Geral da Arquitetura

```
crypto-trading-mvp/
├── 📋 DOCUMENTAÇÃO E GESTÃO
├── 🔧 CONFIGURAÇÃO E INFRAESTRUTURA  
├── 🤖 CORE DO BOT DE TRADING
├── 🌐 API E BACKEND
├── 🎨 DASHBOARD E FRONTEND
├── 🔒 SEGURANÇA E DADOS
├── 📊 ESTRATÉGIAS E INDICADORES
├── 🧪 TESTES E UTILITÁRIOS
└── 🚀 DEPLOY E PRODUÇÃO
```

## 📂 Estrutura Detalhada de Diretórios

### 📋 **DOCUMENTAÇÃO E GESTÃO** (`/docs/` e `/project-management/`)
```
docs[x]
├── PROJECT_STRUCTURE.md  [x]         # 📁 Esta documentação [x]
├── API_DOCUMENTATION.md   [x]       # 📖 Documentação da API[x]
├── STRATEGY_GUIDE.md     [x]        # 📊 Guia das estratégias[x]
├── DEPLOYMENT_GUIDE.md    [x]       # 🚀 Guia de deploy *[x]
├── USER_MANUAL.md                # 👤 Manual do usuário
└── TECHNICAL_SPECS.md            # 🔧 Especificações técnicas

project-management/[x]
├── todo.md   [x]                    # ✅ Lista de tarefas (TODO principal)[x]
├── roadmap.md  [x]                  # 🗺️ Roadmap do projeto[x]
├── changelog.md [x]                 # 📝 Log de mudanças[x]
├── requirements.md               # 📋 Requisitos do projeto
└── meeting-notes/[x]             # 📝 Notas de reuniões[x]
    ├── 2025-01-30-planning.md
    └── ...
```

### 🔧 **CONFIGURAÇÃO E INFRAESTRUTURA** (`/config/`, `/docker/`)
```
config/*
├── settings.py[x]                   # ⚙️ Configurações principais[x]
├── environments/[x]           # 🌍 Configs por ambiente*
│   ├── development.py[x]
│   ├── staging.py
│   └── production.py[x]
└── logging.conf                  # 📝 Configuração de logs

docker/
├── Dockerfile.api  [x]             # 🐳 Container da API*
├── Dockerfile.dashboard    [x]     # 🐳 Container do Dashboard*
├── Dockerfile.bot     [x]          # 🐳 Container do Bot*
├── nginx/*[x]
│   └── nginx.conf   [x]           # 🌐 Configuração Nginx*
├── postgres/*[x]
│   └── init.sql    [x]            # 🗄️ Inicialização do DB*
└── prometheus/*[x]
    └── prometheus.yml   [x]       # 📊 Configuração Prometheus*

# Arquivos de configuração raiz
├── docker-compose.yml  [x]         # 🐳 Orquestração Docker*
├── requirements.txt    [x]         # 📦 Dependências Python*
├── .env.example   [x]             # 🔐 Exemplo de variáveis ambiente*
├── .gitignore                  # 🚫 Arquivos ignorados pelo Git*
└── README.md       [x]            # 📖 Documentação principal
```

### 🤖 **CORE DO BOT DE TRADING** (`/src/bot/`)
```
src/bot/
├── __init__.py [x]                 # 📦 Inicialização do módulo*
├── interfaces.py [x]               # 🔌 Interfaces abstratas*
├── trading_bot.py  [x]            # 🤖 Core principal do bot*
├── worker.py    [x]               # ⚙️ Worker multi-cliente*
├── strategies.py    [x]           # 📊 Factory de estratégias*
├── risk_manager.py    [x]         # ⚠️ Gerenciador de risco*
├── bybit_provider.py [x]          # 🔗 Provider da Bybit*
└── strategies/                 # 📊 Estratégias específicas*
    ├── __init__.py
    ├── sma_strategy.py         # 📈 Estratégia SMA
    ├── rsi_strategy.py         # 📉 Estratégia RSI
    └── ppp_vishva_strategy.py[x]  # 🔬 Estratégia PPP Vishva*
```

### 🌐 **API E BACKEND** (`/src/api/`)
```
src/api/
├── __init__.py   [x]               # 📦 Inicialização*
├── main.py     [x]                # 🚀 Aplicação FastAPI principal*
├── routes/     [x]                # 🛣️ Rotas da API*
│   ├── __init__.py*[x]
│   ├── auth.py       [x]          # 🔐 Autenticação*
│   ├── clients.py    [x]          # 👤 Gerenciamento clientes*
│   ├── trading.py     [x]         # 📊 Operações de trading*
│   └── admin.py                # 👑 Rotas administrativas
├── services/                   # 🔧 Lógica de negócio
│   ├── __init__.py*
│   ├── client_service.py [x]        # 👤 Serviços de cliente*
│   ├── trading_service.py   [x]    # 📊 Serviços de trading
│   └── notification_service.py    # 📢 Serviços de notificação
└── middleware/*                   # 🔄 Middlewares
    ├── __init__.py*[x] 
    ├── auth_middleware.py  [x]     # 🔐 Middleware de auth
    └── rate_limit_middleware.py     # 🚦 Rate limiting
```

### 🎨 **DASHBOARD E FRONTEND** (`/src/dashboard/`)
```
src/dashboard/
├── __init__.py [x]             # 📦 Inicialização*
├── main.py    [x]             # 🎨 Aplicação Streamlit principal
├── pages/[x]              # 📄 Páginas do dashboard
│   ├── __init__.py
│   ├── login.py                # 🔐 Página de login
│   ├── dashboard.py            # 📊 Dashboard principal
│   ├── settings.py             # ⚙️ Configurações
│   ├── performance.py          # 📈 Performance
│   └── history.py              # 📜 Histórico
├── components/*  	               # 🧩 Componentes reutilizáveis
│   ├── __init__.py[x]
│   ├── charts.py               # 📊 Gráficos
│   ├── forms.py                # 📝 Formulários
│   └── widgets.py              # 🎛️ Widgets
└── static/*                     # 📁 Arquivos estáticos
    ├── css/*
    ├── js/*
    └── images/*
```

### 🔒 **SEGURANÇA E DADOS** (`/src/security/`, `/src/models/`)
```
src/security/*
├── __init__.py* [x]                 # 📦 Inicialização
├── encryption.py *  [x]            # 🔐 Criptografia
├── auth.py                     # 🔑 Autenticação
├── permissions.py              # 🛡️ Permissões
└── audit.py                    # 📋 Auditoria

src/models/*
├── __init__.py [x]                  # 📦 Inicialização*
├── database.py [x]                # 🗄️ Configuração DB*
├── client.py [x]                  # 👤 Modelo Cliente*
├── trading.py                  # 📊 Modelos Trading
├── audit.py                    # 📋 Modelo Auditoria
└── migrations/[x]                # 🔄 Migrações DB
    ├── __init__.py
    ├── 001_initial.py
    └── ...
```

### 📊 **ESTRATÉGIAS E INDICADORES** (`/src/strategy/`)
```
src/strategy/
├── __init__.py * [x]                 # 📦 Inicialização
├── ppp_vishva_algo.py * [x]         # 🔬 Algoritmo PPP Vishva original
└── indicators/     *   [x]          # 📊 Indicadores técnicos
    ├── __init__.py*[x] 
    ├── base_indicator.py   * [x]    # 🏗️ Classe base
    ├── indicator_manager.py * [x]   # 🎛️ Gerenciador
    ├── atr.py             *  [x]    # 📊 Average True Range
    ├── ema.py               * [x]   # 📈 Exponential Moving Average
    ├── ewo.py                *  [x] # 🌊 Elliott Wave Oscillator
    ├── heikin_ashi.py       *  [x]  # 🕯️ Heikin Ashi
    ├── rsi.py                *  [x] # 📉 Relative Strength Index
    ├── stoch_rsi.py          *  [x] # 📊 Stochastic RSI
    └── ut_bot.py             *  [x] # 🤖 UT Bot Indicator
```

### 🧪 **TESTES E UTILITÁRIOS** (`/tests/`, `/src/utils/`)
```
tests/[x] 
├── __init__.py*                   # 📦 Inicialização
├── conftest.py                 # ⚙️ Configuração pytest
├── unit/*                       # 🧪 Testes unitários
│   ├── test_strategies.py
│   ├── test_indicators.py
│   ├── test_risk_manager.py
│   └── test_api.py
├── integration/*                # 🔗 Testes integração
│   ├── test_bot_workflow.py
│   ├── test_api_integration.py
│   └── test_dashboard.py
└── performance/ *               # ⚡ Testes performance
    ├── test_strategy_speed.py
    └── test_api_load.py

src/utils/
├── __init__.py * [x]                 # 📦 Inicialização
├── bybit_test.py        [x]       # 🧪 Teste Bybit
├── bybit_test_mock.py[x]     # 🎭 Mock Bybit
├── data_helpers.py             # 📊 Helpers de dados
├── logging_helpers.py          # 📝 Helpers de log
└── validation.py               # ✅ Validações

# Testes específicos na raiz
├── test_ppp_vishva.py  *        # 🔬 Teste PPP Vishva
└── test_integration.py         # 🔗 Teste integração geral
```

### 🚀 **DEPLOY E PRODUÇÃO** (`/deployment/`, `/monitoring/`)
```
deployment/
├── kubernetes/ *                # ☸️ Configs Kubernetes
│   ├── namespace.yaml
│   ├── api-deployment.yaml
│   ├── dashboard-deployment.yaml
│   ├── bot-deployment.yaml
│   └── services.yaml
├── terraform/  *                # 🏗️ Infraestrutura como código
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
├── scripts/     *               # 📜 Scripts de deploy
│   ├── deploy.sh
│   ├── backup.sh
│   └── rollback.sh
└── environments/   *            # 🌍 Configs por ambiente
    ├── staging.env
    └── production.env

monitoring/*
├── grafana/  *                  # 📊 Dashboards Grafana
│   ├── dashboards/*
│   └── provisioning/*
├── prometheus/ *                # 📈 Configurações Prometheus
│   ├── rules/*
│   └── targets/*
└── alerts/   *                  # 🚨 Configurações alertas
    ├── trading-alerts.yml
    └── system-alerts.yml

# Scripts utilitários na raiz
├── start_services.py [x]       # 🚀 Iniciar todos serviços
├── backup_data.py             # 💾 Backup de dados
└── health_check.py             # 🏥 Health check
``

### 📝 **LOGS E DADOS** (`/logs/`, `/data/`)
```
logs/                           # 📝 Logs da aplicação
├── api/
│   ├── api-2025-01-30.log
│   └── error-2025-01-30.log
├── bot/
│   ├── trading-2025-01-30.log
│   └── strategy-2025-01-30.log
├── dashboard/
│   └── dashboard-2025-01-30.log
└── system/
    └── system-2025-01-30.log

data/                           # 📊 Dados da aplicação
├── database/                   # 🗄️ Arquivos de banco
│   └── trading_bot.db
├── backups/                    # 💾 Backups
│   ├── db-backup-2025-01-30.sql
│   └── config-backup-2025-01-30.tar.gz
├── exports/                    # 📤 Dados exportados
│   └── trading-report-2025-01.csv
└── temp/                       # 🗂️ Arquivos temporários
    └── processing/
```

## 🎯 **Regras de Organização**

### 📁 **Onde Colocar Novos Arquivos:**

1. **📊 Novas Estratégias**: `/src/bot/strategies/nome_estrategia.py`
2. **📈 Novos Indicadores**: `/src/strategy/indicators/nome_indicador.py`
3. **🛣️ Novas Rotas API**: `/src/api/routes/nome_rota.py`
4. **📄 Novas Páginas Dashboard**: `/src/dashboard/pages/nome_pagina.py`
5. **🧪 Novos Testes**: `/tests/unit/test_nome.py` ou `/tests/integration/`
6. **📖 Nova Documentação**: `/docs/NOME_DOC.md`
7. **⚙️ Novas Configurações**: `/config/nome_config.py`
8. **🔧 Novos Utilitários**: `/src/utils/nome_util.py`
9. **📝 Gestão de Projeto**: `/project-management/nome_arquivo.md`
10. **🚀 Scripts Deploy**: `/deployment/scripts/nome_script.sh`

### 🏷️ **Convenções de Nomenclatura:**

- **Arquivos Python**: `snake_case.py`
- **Classes**: `PascalCase`
- **Funções/Variáveis**: `snake_case`
- **Constantes**: `UPPER_SNAKE_CASE`
- **Documentação**: `UPPER_CASE.md`
- **Configs**: `lowercase.yml/yaml`
- **Scripts**: `kebab-case.sh`

### 📋 **Arquivos Obrigatórios em Cada Módulo:**

1. `__init__.py` - Em todos os diretórios Python
2. `README.md` - Em diretórios principais
3. `.gitignore` - Para ignorar arquivos específicos
4. `requirements.txt` - Para dependências específicas (se aplicável)

## 🔄 **Fluxo de Desenvolvimento:**

1. **📝 Planejamento**: Atualizar `/project-management/todo.md`
2. **💻 Desenvolvimento**: Criar arquivos na estrutura apropriada
3. **🧪 Testes**: Adicionar testes em `/tests/`
4. **📖 Documentação**: Atualizar `/docs/`
5. **🚀 Deploy**: Usar scripts em `/deployment/`
6. **📊 Monitoramento**: Verificar logs em `/logs/`

Esta estrutura garante **máxima organização**, **escalabilidade** e **manutenibilidade** do projeto MVP Bot de Trading!

