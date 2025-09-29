# 🌐 Documentação da API - MVP Bot de Trading

**Versão:** 1.0.0  
**Autor:** Manus AI  
**Data:** Janeiro 2025  
**Localização:** `/docs/API_DOCUMENTATION.md`

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Autenticação](#autenticação)
3. [Endpoints de Saúde](#endpoints-de-saúde)
4. [Endpoints de Autenticação](#endpoints-de-autenticação)
5. [Endpoints de Clientes](#endpoints-de-clientes)
6. [Endpoints de Trading](#endpoints-de-trading)
7. [Modelos de Dados](#modelos-de-dados)
8. [Códigos de Erro](#códigos-de-erro)
9. [Exemplos de Uso](#exemplos-de-uso)
10. [Rate Limiting](#rate-limiting)
11. [Webhooks](#webhooks)

---

## 🎯 Visão Geral

A API REST do MVP Bot de Trading é construída com **FastAPI** e fornece acesso programático completo a todas as funcionalidades do sistema de trading automatizado. A API segue os padrões RESTful e utiliza autenticação JWT para segurança.

### Características Principais

- **Framework:** FastAPI 0.104+
- **Autenticação:** JWT (JSON Web Tokens)
- **Formato:** JSON
- **Protocolo:** HTTPS (recomendado para produção)
- **Documentação Interativa:** Swagger UI disponível em `/docs`

### URL Base

```
Desenvolvimento: http://localhost:8000
Produção: https://api.seu-dominio.com
```

### Versionamento

A API utiliza versionamento por prefixo de URL:
- **v1:** `/api/v1/` (versão atual)
- **Futuras versões:** `/api/v2/`, `/api/v3/`, etc.

---

## 🔐 Autenticação

A API utiliza **JWT (JSON Web Tokens)** para autenticação. Todos os endpoints protegidos requerem um token válido no header `Authorization`.

### Fluxo de Autenticação

1. **Registro:** Criar conta via `/api/auth/register`
2. **Login:** Obter token via `/api/auth/login`
3. **Uso:** Incluir token em todas as requisições protegidas
4. **Renovação:** Fazer login novamente quando o token expirar

### Header de Autenticação

```http
Authorization: Bearer <seu_jwt_token>
```

### Exemplo de Token JWT

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "client_id": 123
}
```

---

## 🏥 Endpoints de Saúde

### GET /health

Verifica o status de saúde da API.

**Parâmetros:** Nenhum  
**Autenticação:** Não requerida

#### Resposta de Sucesso (200)

```json
{
  "status": "healthy",
  "timestamp": "2025-01-15T10:30:00Z",
  "version": "1.0.0",
  "uptime": 3600,
  "database": "connected",
  "external_apis": {
    "bybit": "connected"
  }
}
```

#### Exemplo de Uso

```bash
curl -X GET "http://localhost:8000/health"
```

### GET /

Endpoint raiz da API.

**Parâmetros:** Nenhum  
**Autenticação:** Não requerida

#### Resposta de Sucesso (200)

```json
{
  "message": "MVP Bot de Trading API",
  "version": "1.0.0",
  "documentation": "/docs",
  "health": "/health"
}
```

---

## 🔑 Endpoints de Autenticação

### POST /api/auth/register

Registra um novo cliente no sistema.

**Autenticação:** Não requerida

#### Parâmetros do Body

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `email` | string | Sim | Email válido do cliente |
| `password` | string | Sim | Senha (mín. 8 caracteres) |
| `bybit_api_key` | string | Sim | Chave API da Bybit |
| `bybit_api_secret` | string | Sim | Secret API da Bybit |
| `trading_config` | object | Não | Configuração inicial de trading |

#### Exemplo de Requisição

```json
{
  "email": "trader@example.com",
  "password": "senha_segura_123",
  "bybit_api_key": "sua_api_key_bybit",
  "bybit_api_secret": "seu_api_secret_bybit",
  "trading_config": {
    "strategy": "sma",
    "symbols": ["BTCUSDT"],
    "risk_per_trade": 0.02
  }
}
```

#### Resposta de Sucesso (201)

```json
{
  "message": "Cliente criado com sucesso",
  "client_id": 123,
  "email": "trader@example.com",
  "created_at": "2025-01-15T10:30:00Z"
}
```

#### Possíveis Erros

- **400:** Email já cadastrado
- **422:** Dados de entrada inválidos
- **500:** Erro interno do servidor

### POST /api/auth/login

Autentica um cliente e retorna token JWT.

**Autenticação:** Não requerida

#### Parâmetros do Body

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `email` | string | Sim | Email do cliente |
| `password` | string | Sim | Senha do cliente |

#### Exemplo de Requisição

```json
{
  "email": "trader@example.com",
  "password": "senha_segura_123"
}
```

#### Resposta de Sucesso (200)

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "client_id": 123,
  "email": "trader@example.com"
}
```

#### Possíveis Erros

- **401:** Credenciais inválidas
- **422:** Dados de entrada inválidos
- **500:** Erro interno do servidor

### POST /api/auth/logout

Invalida o token JWT atual.

**Autenticação:** Requerida

#### Parâmetros

Nenhum parâmetro adicional necessário além do token de autenticação.

#### Resposta de Sucesso (200)

```json
{
  "message": "Logout realizado com sucesso"
}
```

#### Possíveis Erros

- **401:** Token inválido ou expirado

---

## 👤 Endpoints de Clientes

### GET /api/clients/profile

Obtém o perfil do cliente autenticado.

**Autenticação:** Requerida

#### Resposta de Sucesso (200)

```json
{
  "id": 123,
  "email": "trader@example.com",
  "created_at": "2025-01-15T10:30:00Z",
  "last_login": "2025-01-15T15:45:00Z",
  "trading_config": {
    "strategy": "sma",
    "symbols": ["BTCUSDT", "ETHUSDT"],
    "risk_per_trade": 0.02,
    "fast_period": 10,
    "slow_period": 20
  },
  "account_status": "active",
  "api_keys_configured": true
}
```

### PUT /api/clients/profile

Atualiza o perfil do cliente.

**Autenticação:** Requerida

#### Parâmetros do Body

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `email` | string | Não | Novo email |
| `password` | string | Não | Nova senha |

#### Exemplo de Requisição

```json
{
  "email": "novo_email@example.com"
}
```

#### Resposta de Sucesso (200)

```json
{
  "message": "Perfil atualizado com sucesso",
  "updated_fields": ["email"]
}
```

### GET /api/clients/trading-config

Obtém a configuração de trading do cliente.

**Autenticação:** Requerida

#### Resposta de Sucesso (200)

```json
{
  "strategy": "sma",
  "symbols": ["BTCUSDT", "ETHUSDT"],
  "risk_per_trade": 0.02,
  "max_position_size": 1000.0,
  "max_daily_loss": 100.0,
  "fast_period": 10,
  "slow_period": 20,
  "stop_loss_pct": 0.02,
  "take_profit_pct": 0.04
}
```

### PUT /api/clients/trading-config

Atualiza a configuração de trading do cliente.

**Autenticação:** Requerida

#### Parâmetros do Body

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `strategy` | string | Não | Estratégia: "sma", "rsi", "ppp_vishva" |
| `symbols` | array | Não | Lista de símbolos para trading |
| `risk_per_trade` | number | Não | Risco por trade (0.01 = 1%) |
| `max_position_size` | number | Não | Tamanho máximo de posição (USDT) |
| `max_daily_loss` | number | Não | Perda máxima diária (USDT) |

#### Exemplo de Requisição

```json
{
  "strategy": "rsi",
  "symbols": ["BTCUSDT", "ETHUSDT", "ADAUSDT"],
  "risk_per_trade": 0.015,
  "rsi_period": 14,
  "oversold": 30,
  "overbought": 70
}
```

#### Resposta de Sucesso (200)

```json
{
  "message": "Configuração atualizada com sucesso",
  "updated_config": {
    "strategy": "rsi",
    "symbols": ["BTCUSDT", "ETHUSDT", "ADAUSDT"],
    "risk_per_trade": 0.015,
    "rsi_period": 14,
    "oversold": 30,
    "overbought": 70
  }
}
```

---

## 📈 Endpoints de Trading

### GET /api/trading/status

Obtém o status atual do bot de trading do cliente.

**Autenticação:** Requerida

#### Resposta de Sucesso (200)

```json
{
  "client_id": 123,
  "bot_status": "running",
  "strategy": "sma",
  "symbols": ["BTCUSDT", "ETHUSDT"],
  "uptime": 3600,
  "last_update": "2025-01-15T15:45:00Z",
  "positions_count": 2,
  "daily_pnl": 15.50,
  "total_trades_today": 5,
  "account_balance": {
    "USDT": 1250.75,
    "BTC": 0.001,
    "ETH": 0.05
  }
}
```

### POST /api/trading/start

Inicia o bot de trading para o cliente.

**Autenticação:** Requerida

#### Resposta de Sucesso (200)

```json
{
  "message": "Bot iniciado com sucesso",
  "client_id": 123,
  "started_at": "2025-01-15T15:45:00Z",
  "strategy": "sma",
  "symbols": ["BTCUSDT", "ETHUSDT"]
}
```

#### Possíveis Erros

- **400:** Bot já está rodando
- **422:** Configuração de trading inválida
- **500:** Erro ao conectar com Bybit

### POST /api/trading/stop

Para o bot de trading do cliente.

**Autenticação:** Requerida

#### Resposta de Sucesso (200)

```json
{
  "message": "Bot parado com sucesso",
  "client_id": 123,
  "stopped_at": "2025-01-15T15:45:00Z",
  "final_positions": 0,
  "session_pnl": 25.30
}
```

### POST /api/trading/pause

Pausa temporariamente o bot de trading.

**Autenticação:** Requerida

#### Resposta de Sucesso (200)

```json
{
  "message": "Bot pausado com sucesso",
  "client_id": 123,
  "paused_at": "2025-01-15T15:45:00Z"
}
```

### POST /api/trading/resume

Resume o bot de trading pausado.

**Autenticação:** Requerida

#### Resposta de Sucesso (200)

```json
{
  "message": "Bot resumido com sucesso",
  "client_id": 123,
  "resumed_at": "2025-01-15T15:45:00Z"
}
```

### GET /api/trading/positions

Obtém as posições abertas do cliente.

**Autenticação:** Requerida

#### Parâmetros de Query

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `symbol` | string | Não | Filtrar por símbolo específico |
| `side` | string | Não | Filtrar por lado: "LONG" ou "SHORT" |

#### Resposta de Sucesso (200)

```json
[
  {
    "id": "pos_123",
    "symbol": "BTCUSDT",
    "side": "LONG",
    "size": 0.001,
    "entry_price": 49500.00,
    "current_price": 50000.00,
    "unrealized_pnl": 0.50,
    "unrealized_pnl_pct": 1.01,
    "opened_at": "2025-01-15T14:30:00Z",
    "stop_loss": 48510.00,
    "take_profit": 51480.00
  },
  {
    "id": "pos_124",
    "symbol": "ETHUSDT",
    "side": "LONG",
    "size": 0.1,
    "entry_price": 3200.00,
    "current_price": 3250.00,
    "unrealized_pnl": 5.00,
    "unrealized_pnl_pct": 1.56,
    "opened_at": "2025-01-15T15:00:00Z",
    "stop_loss": 3136.00,
    "take_profit": 3328.00
  }
]
```

### GET /api/trading/orders

Obtém o histórico de ordens do cliente.

**Autenticação:** Requerida

#### Parâmetros de Query

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `symbol` | string | Não | Filtrar por símbolo |
| `status` | string | Não | Filtrar por status: "filled", "cancelled", "pending" |
| `limit` | integer | Não | Número máximo de resultados (padrão: 50) |
| `offset` | integer | Não | Offset para paginação (padrão: 0) |
| `start_date` | string | Não | Data inicial (ISO 8601) |
| `end_date` | string | Não | Data final (ISO 8601) |

#### Resposta de Sucesso (200)

```json
{
  "total": 25,
  "limit": 10,
  "offset": 0,
  "orders": [
    {
      "id": "order_123",
      "symbol": "BTCUSDT",
      "side": "BUY",
      "type": "MARKET",
      "quantity": 0.001,
      "price": null,
      "filled_price": 49500.00,
      "filled_quantity": 0.001,
      "status": "filled",
      "created_at": "2025-01-15T14:30:00Z",
      "filled_at": "2025-01-15T14:30:05Z",
      "commission": 0.025,
      "commission_asset": "USDT"
    }
  ]
}
```

### GET /api/trading/performance

Obtém métricas de performance do cliente.

**Autenticação:** Requerida

#### Parâmetros de Query

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `period` | string | Não | Período: "1d", "7d", "30d", "all" (padrão: "7d") |

#### Resposta de Sucesso (200)

```json
{
  "period": "7d",
  "total_trades": 45,
  "winning_trades": 28,
  "losing_trades": 17,
  "win_rate": 62.22,
  "total_pnl": 125.50,
  "total_pnl_pct": 12.55,
  "best_trade": 25.30,
  "worst_trade": -15.20,
  "average_trade": 2.79,
  "profit_factor": 1.85,
  "sharpe_ratio": 1.42,
  "max_drawdown": -35.20,
  "max_drawdown_pct": -3.52,
  "daily_pnl": [
    {"date": "2025-01-09", "pnl": 15.20},
    {"date": "2025-01-10", "pnl": -5.30},
    {"date": "2025-01-11", "pnl": 22.10},
    {"date": "2025-01-12", "pnl": 8.75},
    {"date": "2025-01-13", "pnl": -12.40},
    {"date": "2025-01-14", "pnl": 18.90},
    {"date": "2025-01-15", "pnl": 78.25}
  ]
}
```

---

## 📊 Modelos de Dados

### Cliente (Client)

```json
{
  "id": 123,
  "email": "trader@example.com",
  "created_at": "2025-01-15T10:30:00Z",
  "last_login": "2025-01-15T15:45:00Z",
  "account_status": "active",
  "api_keys_configured": true,
  "trading_config": {
    "strategy": "sma",
    "symbols": ["BTCUSDT"],
    "risk_per_trade": 0.02
  }
}
```

### Configuração de Trading (TradingConfig)

```json
{
  "strategy": "sma",
  "symbols": ["BTCUSDT", "ETHUSDT"],
  "risk_per_trade": 0.02,
  "max_position_size": 1000.0,
  "max_daily_loss": 100.0,
  "fast_period": 10,
  "slow_period": 20,
  "stop_loss_pct": 0.02,
  "take_profit_pct": 0.04
}
```

### Posição (Position)

```json
{
  "id": "pos_123",
  "symbol": "BTCUSDT",
  "side": "LONG",
  "size": 0.001,
  "entry_price": 49500.00,
  "current_price": 50000.00,
  "unrealized_pnl": 0.50,
  "unrealized_pnl_pct": 1.01,
  "opened_at": "2025-01-15T14:30:00Z",
  "stop_loss": 48510.00,
  "take_profit": 51480.00
}
```

### Ordem (Order)

```json
{
  "id": "order_123",
  "symbol": "BTCUSDT",
  "side": "BUY",
  "type": "MARKET",
  "quantity": 0.001,
  "price": null,
  "filled_price": 49500.00,
  "filled_quantity": 0.001,
  "status": "filled",
  "created_at": "2025-01-15T14:30:00Z",
  "filled_at": "2025-01-15T14:30:05Z",
  "commission": 0.025,
  "commission_asset": "USDT"
}
```

---

## ❌ Códigos de Erro

### Códigos HTTP Padrão

| Código | Descrição | Quando Ocorre |
|--------|-----------|---------------|
| 200 | OK | Requisição bem-sucedida |
| 201 | Created | Recurso criado com sucesso |
| 400 | Bad Request | Dados de entrada inválidos |
| 401 | Unauthorized | Token ausente ou inválido |
| 403 | Forbidden | Acesso negado |
| 404 | Not Found | Recurso não encontrado |
| 422 | Unprocessable Entity | Validação de dados falhou |
| 429 | Too Many Requests | Rate limit excedido |
| 500 | Internal Server Error | Erro interno do servidor |

### Estrutura de Erro Padrão

```json
{
  "detail": "Descrição do erro",
  "error_code": "SPECIFIC_ERROR_CODE",
  "timestamp": "2025-01-15T15:45:00Z",
  "path": "/api/trading/start",
  "request_id": "req_123456"
}
```

### Códigos de Erro Específicos

| Código | Descrição |
|--------|-----------|
| `INVALID_CREDENTIALS` | Email ou senha incorretos |
| `TOKEN_EXPIRED` | Token JWT expirado |
| `INSUFFICIENT_BALANCE` | Saldo insuficiente para trading |
| `INVALID_STRATEGY` | Estratégia não suportada |
| `BOT_ALREADY_RUNNING` | Bot já está em execução |
| `BOT_NOT_RUNNING` | Bot não está rodando |
| `BYBIT_API_ERROR` | Erro na API da Bybit |
| `RISK_LIMIT_EXCEEDED` | Limite de risco excedido |
| `INVALID_SYMBOL` | Símbolo de trading inválido |
| `CONFIGURATION_ERROR` | Erro na configuração |

---

## 💡 Exemplos de Uso

### Exemplo 1: Fluxo Completo de Registro e Trading

```python
import requests
import json

# 1. Registrar novo cliente
register_data = {
    "email": "trader@example.com",
    "password": "senha_segura_123",
    "bybit_api_key": "sua_api_key",
    "bybit_api_secret": "seu_api_secret"
}

response = requests.post(
    "http://localhost:8000/api/auth/register",
    json=register_data
)
print(f"Registro: {response.status_code}")

# 2. Fazer login
login_data = {
    "email": "trader@example.com",
    "password": "senha_segura_123"
}

response = requests.post(
    "http://localhost:8000/api/auth/login",
    json=login_data
)
token_data = response.json()
token = token_data["access_token"]

# 3. Configurar headers de autenticação
headers = {"Authorization": f"Bearer {token}"}

# 4. Configurar trading
config_data = {
    "strategy": "sma",
    "symbols": ["BTCUSDT", "ETHUSDT"],
    "risk_per_trade": 0.02,
    "fast_period": 10,
    "slow_period": 20
}

response = requests.put(
    "http://localhost:8000/api/clients/trading-config",
    json=config_data,
    headers=headers
)
print(f"Configuração: {response.status_code}")

# 5. Iniciar bot
response = requests.post(
    "http://localhost:8000/api/trading/start",
    headers=headers
)
print(f"Início do bot: {response.status_code}")

# 6. Verificar status
response = requests.get(
    "http://localhost:8000/api/trading/status",
    headers=headers
)
status = response.json()
print(f"Status: {status['bot_status']}")

# 7. Obter posições
response = requests.get(
    "http://localhost:8000/api/trading/positions",
    headers=headers
)
positions = response.json()
print(f"Posições abertas: {len(positions)}")
```

### Exemplo 2: Monitoramento de Performance

```python
import requests
import matplotlib.pyplot as plt

# Headers de autenticação (assumindo token já obtido)
headers = {"Authorization": f"Bearer {token}"}

# Obter performance dos últimos 30 dias
response = requests.get(
    "http://localhost:8000/api/trading/performance?period=30d",
    headers=headers
)
performance = response.json()

# Extrair dados para gráfico
dates = [day["date"] for day in performance["daily_pnl"]]
pnl_values = [day["pnl"] for day in performance["daily_pnl"]]

# Criar gráfico
plt.figure(figsize=(12, 6))
plt.plot(dates, pnl_values, marker='o')
plt.title(f'PnL Diário - {performance["period"]}')
plt.xlabel('Data')
plt.ylabel('PnL (USDT)')
plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()
plt.show()

print(f"Win Rate: {performance['win_rate']:.2f}%")
print(f"Total PnL: {performance['total_pnl']:.2f} USDT")
print(f"Sharpe Ratio: {performance['sharpe_ratio']:.2f}")
```

### Exemplo 3: Cliente JavaScript/Node.js

```javascript
const axios = require('axios');

class TradingBotAPI {
    constructor(baseURL = 'http://localhost:8000') {
        this.baseURL = baseURL;
        this.token = null;
    }

    async login(email, password) {
        try {
            const response = await axios.post(`${this.baseURL}/api/auth/login`, {
                email,
                password
            });
            
            this.token = response.data.access_token;
            return response.data;
        } catch (error) {
            throw new Error(`Login failed: ${error.response.data.detail}`);
        }
    }

    getHeaders() {
        if (!this.token) {
            throw new Error('Not authenticated. Please login first.');
        }
        return {
            'Authorization': `Bearer ${this.token}`,
            'Content-Type': 'application/json'
        };
    }

    async getStatus() {
        const response = await axios.get(
            `${this.baseURL}/api/trading/status`,
            { headers: this.getHeaders() }
        );
        return response.data;
    }

    async startBot() {
        const response = await axios.post(
            `${this.baseURL}/api/trading/start`,
            {},
            { headers: this.getHeaders() }
        );
        return response.data;
    }

    async stopBot() {
        const response = await axios.post(
            `${this.baseURL}/api/trading/stop`,
            {},
            { headers: this.getHeaders() }
        );
        return response.data;
    }

    async getPositions() {
        const response = await axios.get(
            `${this.baseURL}/api/trading/positions`,
            { headers: this.getHeaders() }
        );
        return response.data;
    }
}

// Uso da classe
async function main() {
    const api = new TradingBotAPI();
    
    try {
        // Login
        await api.login('trader@example.com', 'senha_segura_123');
        console.log('Login realizado com sucesso');
        
        // Verificar status
        const status = await api.getStatus();
        console.log('Status do bot:', status.bot_status);
        
        // Obter posições
        const positions = await api.getPositions();
        console.log(`Posições abertas: ${positions.length}`);
        
    } catch (error) {
        console.error('Erro:', error.message);
    }
}

main();
```

---

## 🚦 Rate Limiting

A API implementa rate limiting para prevenir abuso e garantir estabilidade.

### Limites Padrão

| Endpoint | Limite | Janela |
|----------|--------|--------|
| `/api/auth/login` | 5 tentativas | 15 minutos |
| `/api/auth/register` | 3 tentativas | 1 hora |
| Endpoints gerais | 100 requisições | 1 minuto |
| Endpoints de trading | 60 requisições | 1 minuto |

### Headers de Rate Limiting

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642248000
```

### Resposta de Rate Limit Excedido (429)

```json
{
  "detail": "Rate limit exceeded",
  "error_code": "RATE_LIMIT_EXCEEDED",
  "retry_after": 60,
  "limit": 100,
  "window": 60
}
```

---

## 🔗 Webhooks

A API suporta webhooks para notificações em tempo real de eventos importantes.

### Configuração de Webhooks

```json
{
  "url": "https://seu-site.com/webhook",
  "events": ["order_filled", "position_opened", "position_closed"],
  "secret": "seu_webhook_secret"
}
```

### Eventos Disponíveis

| Evento | Descrição |
|--------|-----------|
| `order_filled` | Ordem executada |
| `position_opened` | Nova posição aberta |
| `position_closed` | Posição fechada |
| `bot_started` | Bot iniciado |
| `bot_stopped` | Bot parado |
| `risk_alert` | Alerta de risco |

### Exemplo de Payload de Webhook

```json
{
  "event": "order_filled",
  "timestamp": "2025-01-15T15:45:00Z",
  "client_id": 123,
  "data": {
    "order_id": "order_123",
    "symbol": "BTCUSDT",
    "side": "BUY",
    "quantity": 0.001,
    "price": 49500.00,
    "commission": 0.025
  },
  "signature": "sha256=..."
}
```

---

## 📚 Recursos Adicionais

### Documentação Interativa

- **Swagger UI:** `/docs`
- **ReDoc:** `/redoc`

### SDKs Oficiais

- **Python:** `pip install trading-bot-sdk`
- **JavaScript:** `npm install trading-bot-sdk`
- **Go:** Em desenvolvimento
- **PHP:** Em desenvolvimento

### Suporte e Comunidade

- **GitHub:** [github.com/seu-repo/trading-bot](https://github.com/seu-repo/trading-bot)
- **Discord:** [discord.gg/trading-bot](https://discord.gg/trading-bot)
- **Email:** support@trading-bot.com

### Changelog da API

- **v1.0.0:** Lançamento inicial
- **v1.0.1:** Correções de bugs menores
- **v1.1.0:** Adição de webhooks
- **v1.2.0:** Novos endpoints de performance

---

**Última atualização:** Janeiro 2025  
**Versão da documentação:** 1.0.0

