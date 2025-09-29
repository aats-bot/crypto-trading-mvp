# 📁 Guia de Organização de Arquivos - MVP Bot de Trading

## 🎯 **Onde Colocar Cada Tipo de Arquivo**

### 📊 **Estratégias de Trading**
```
📍 Local: /src/bot/strategies/
📝 Nomenclatura: nome_estrategia_strategy.py
📋 Exemplo: sma_strategy.py, rsi_strategy.py, ppp_vishva_strategy.py

🔧 Como adicionar:
1. Criar arquivo em /src/bot/strategies/
2. Implementar interface TradingStrategy
3. Adicionar ao factory em /src/bot/strategies.py
4. Atualizar dashboard em /src/dashboard/main.py
```

### 📈 **Indicadores Técnicos**
```
📍 Local: /src/strategy/indicators/
📝 Nomenclatura: nome_indicador.py
📋 Exemplo: ema.py, rsi.py, atr.py, ut_bot.py

🔧 Como adicionar:
1. Criar arquivo em /src/strategy/indicators/
2. Herdar de BaseIndicator
3. Implementar método calculate()
4. Adicionar ao IndicatorManager se necessário
```

### 🌐 **Rotas da API**
```
📍 Local: /src/api/routes/
📝 Nomenclatura: nome_rota.py
📋 Exemplo: auth.py, clients.py, trading.py

🔧 Como adicionar:
1. Criar arquivo em /src/api/routes/
2. Definir router = APIRouter()
3. Implementar endpoints
4. Incluir router em /src/api/main.py
```

### 🎨 **Páginas do Dashboard**
```
📍 Local: /src/dashboard/pages/
📝 Nomenclatura: nome_pagina.py
📋 Exemplo: login.py, dashboard.py, settings.py

🔧 Como adicionar:
1. Criar arquivo em /src/dashboard/pages/
2. Implementar função da página
3. Importar em /src/dashboard/main.py
4. Adicionar à navegação
```

### 🧩 **Componentes Reutilizáveis**
```
📍 Local: /src/dashboard/components/
📝 Nomenclatura: nome_componente.py
📋 Exemplo: charts.py, forms.py, widgets.py

🔧 Como adicionar:
1. Criar arquivo em /src/dashboard/components/
2. Implementar funções de componente
3. Importar onde necessário
```

### 🧪 **Testes**
```
📍 Local: /tests/
📂 Subdiretórios:
   - /tests/unit/ - Testes unitários
   - /tests/integration/ - Testes de integração
   - /tests/performance/ - Testes de performance

📝 Nomenclatura: test_nome.py
📋 Exemplo: test_strategies.py, test_api.py

🔧 Como adicionar:
1. Criar arquivo no subdiretório apropriado
2. Usar pytest para estrutura
3. Executar com: pytest tests/
```

### 📖 **Documentação**
```
📍 Local: /docs/
📝 Nomenclatura: NOME_DOCUMENTO.md (MAIÚSCULO)
📋 Exemplo: API_DOCUMENTATION.md, STRATEGY_GUIDE.md

🔧 Como adicionar:
1. Criar arquivo .md em /docs/
2. Usar formato Markdown
3. Atualizar README.md com link
```

### 📋 **Gestão de Projeto**
```
📍 Local: /project-management/
📝 Nomenclatura: nome_arquivo.md
📋 Exemplo: todo.md, roadmap.md, changelog.md

🔧 Como adicionar:
1. Criar arquivo .md em /project-management/
2. Manter atualizado regularmente
3. Usar para tracking de progresso
```

### ⚙️ **Configurações**
```
📍 Local: /config/
📂 Subdiretórios:
   - /config/environments/ - Configs por ambiente

📝 Nomenclatura: nome_config.py
📋 Exemplo: settings.py, logging.conf

🔧 Como adicionar:
1. Criar arquivo em /config/
2. Usar variáveis de ambiente quando possível
3. Documentar configurações necessárias
```

### 🔧 **Utilitários**
```
📍 Local: /src/utils/
📝 Nomenclatura: nome_util.py
📋 Exemplo: data_helpers.py, validation.py

🔧 Como adicionar:
1. Criar arquivo em /src/utils/
2. Implementar funções auxiliares
3. Manter funções pequenas e focadas
```

### 🗄️ **Modelos de Dados**
```
📍 Local: /src/models/
📂 Subdiretórios:
   - /src/models/migrations/ - Migrações de DB

📝 Nomenclatura: nome_modelo.py
📋 Exemplo: client.py, trading.py

🔧 Como adicionar:
1. Criar arquivo em /src/models/
2. Definir modelos SQLAlchemy
3. Criar migração se necessário
```

### 🔒 **Segurança**
```
📍 Local: /src/security/
📝 Nomenclatura: nome_security.py
📋 Exemplo: encryption.py, auth.py, permissions.py

🔧 Como adicionar:
1. Criar arquivo em /src/security/
2. Implementar funcionalidades de segurança
3. Seguir melhores práticas
```

### 🐳 **Docker e Deploy**
```
📍 Local: /docker/ e /deployment/
📂 Subdiretórios:
   - /docker/ - Dockerfiles e configs
   - /deployment/kubernetes/ - Configs K8s
   - /deployment/scripts/ - Scripts de deploy

📝 Nomenclatura: 
   - Dockerfile.nome
   - nome-deployment.yaml
   - nome-script.sh

🔧 Como adicionar:
1. Criar arquivo no diretório apropriado
2. Seguir convenções Docker/K8s
3. Testar em ambiente de desenvolvimento
```

### 📊 **Monitoramento**
```
📍 Local: /monitoring/
📂 Subdiretórios:
   - /monitoring/grafana/ - Dashboards Grafana
   - /monitoring/prometheus/ - Configs Prometheus
   - /monitoring/alerts/ - Configurações de alertas

🔧 Como adicionar:
1. Criar arquivo no subdiretório apropriado
2. Seguir formato YAML para configs
3. Testar alertas e dashboards
```

### 📝 **Logs e Dados**
```
📍 Local: /logs/ e /data/
📂 Subdiretórios:
   - /logs/api/, /logs/bot/, /logs/dashboard/
   - /data/database/, /data/backups/, /data/exports/

⚠️ Nota: Estes diretórios são criados automaticamente
🚫 Não versionar: Adicionar ao .gitignore
```

## 🏷️ **Convenções de Nomenclatura**

### 📁 **Diretórios**
- `lowercase-with-hyphens` para diretórios principais
- `snake_case` para subdiretórios Python

### 📄 **Arquivos Python**
- `snake_case.py` para todos os arquivos
- `test_nome.py` para testes
- `__init__.py` em todos os pacotes

### 📖 **Documentação**
- `UPPER_CASE.md` para docs principais
- `lowercase.md` para docs específicas

### ⚙️ **Configurações**
- `lowercase.yml` ou `lowercase.yaml`
- `lowercase.conf` para configs específicas

### 🐳 **Docker**
- `Dockerfile.service` para Dockerfiles
- `service-config.yml` para configs

## 🔄 **Fluxo de Adição de Arquivos**

### 1. **Identificar Tipo**
- Determinar categoria do arquivo
- Verificar local apropriado na estrutura

### 2. **Criar Arquivo**
- Usar nomenclatura correta
- Adicionar no diretório apropriado
- Criar `__init__.py` se necessário

### 3. **Implementar**
- Seguir padrões do projeto
- Implementar interfaces necessárias
- Adicionar documentação inline

### 4. **Integrar**
- Atualizar imports necessários
- Adicionar ao factory/registry se aplicável
- Atualizar configurações

### 5. **Testar**
- Criar testes apropriados
- Executar testes existentes
- Validar integração

### 6. **Documentar**
- Atualizar documentação relevante
- Adicionar ao changelog
- Atualizar README se necessário

## ✅ **Checklist para Novos Arquivos**

- [ ] Arquivo no diretório correto
- [ ] Nomenclatura seguindo convenções
- [ ] `__init__.py` criado se necessário
- [ ] Imports atualizados
- [ ] Testes criados
- [ ] Documentação atualizada
- [ ] .gitignore atualizado se necessário
- [ ] Changelog atualizado

## 🎯 **Benefícios da Organização**

### 🔍 **Facilita Localização**
- Estrutura lógica e previsível
- Convenções claras de nomenclatura
- Separação por responsabilidade

### 🚀 **Melhora Manutenibilidade**
- Código organizado e modular
- Fácil adição de novas funcionalidades
- Reduz acoplamento entre componentes

### 👥 **Facilita Colaboração**
- Estrutura padronizada
- Documentação clara
- Processo definido para mudanças

### 📈 **Escalabilidade**
- Estrutura preparada para crescimento
- Separação clara de responsabilidades
- Facilita refatoração quando necessário

---

**💡 Dica**: Sempre consulte este guia antes de adicionar novos arquivos ao projeto!

