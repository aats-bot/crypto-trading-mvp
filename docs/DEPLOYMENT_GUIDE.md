# 🚀 Guia Completo de Deploy - MVP Bot de Trading

**Versão:** 1.0.0  
**Autor:** Manus AI  
**Data:** Janeiro 2025  
**Localização:** `/docs/DEPLOYMENT_GUIDE.md`

## 📋 Índice

1. [Visão Geral do Deploy](#visão-geral-do-deploy)
2. [Pré-requisitos](#pré-requisitos)
3. [Deploy Local (Desenvolvimento)](#deploy-local)
4. [Deploy com Docker](#deploy-com-docker)
5. [Deploy em Produção](#deploy-em-produção)
6. [Deploy na AWS](#deploy-na-aws)
7. [Deploy no Google Cloud](#deploy-no-google-cloud)
8. [Deploy com Kubernetes](#deploy-com-kubernetes)
9. [Monitoramento e Logs](#monitoramento-e-logs)
10. [Backup e Recuperação](#backup-e-recuperação)
11. [Segurança em Produção](#segurança-em-produção)
12. [Troubleshooting](#troubleshooting)

---

## 🎯 Visão Geral do Deploy

O MVP Bot de Trading é uma aplicação distribuída composta por múltiplos serviços que podem ser deployados de diferentes formas, desde ambiente local para desenvolvimento até infraestrutura cloud escalável para produção.

### Arquitetura de Deploy

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load Balancer │    │     Nginx       │    │   Monitoring    │
│    (Optional)   │    │   (Reverse      │    │  (Prometheus/   │
│                 │    │    Proxy)       │    │   Grafana)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI       │    │   Streamlit     │    │   Bot Worker    │
│   (Backend)     │    │   (Dashboard)   │    │   (Trading)     │
│   Port: 8000    │    │   Port: 8501    │    │   Background    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   PostgreSQL    │
                    │   (Database)    │
                    │   Port: 5432    │
                    └─────────────────┘
```

### Componentes do Sistema

| Componente | Descrição | Porta Padrão | Obrigatório |
|------------|-----------|--------------|-------------|
| **FastAPI** | API REST backend | 8000 | Sim |
| **Streamlit** | Dashboard web | 8501 | Sim |
| **Bot Worker** | Engine de trading | N/A | Sim |
| **PostgreSQL** | Banco de dados | 5432 | Sim |
| **Nginx** | Reverse proxy | 80/443 | Produção |
| **Prometheus** | Métricas | 9090 | Opcional |
| **Grafana** | Dashboards | 3000 | Opcional |

---

## 📋 Pré-requisitos

### Requisitos de Sistema

#### Mínimo (Desenvolvimento)
- **CPU:** 2 cores
- **RAM:** 4GB
- **Armazenamento:** 20GB SSD
- **Rede:** Conexão estável à internet

#### Recomendado (Produção)
- **CPU:** 4+ cores
- **RAM:** 8GB+
- **Armazenamento:** 50GB+ SSD
- **Rede:** Baixa latência, alta disponibilidade

### Software Necessário

#### Para Deploy Local
```bash
# Python 3.11+
python3 --version

# pip (gerenciador de pacotes Python)
pip3 --version

# Git
git --version

# Opcional: PostgreSQL
psql --version
```

#### Para Deploy Docker
```bash
# Docker
docker --version

# Docker Compose
docker compose version
```

#### Para Deploy Cloud
```bash
# AWS CLI (para AWS)
aws --version

# gcloud CLI (para Google Cloud)
gcloud --version

# kubectl (para Kubernetes)
kubectl version
```

### Contas e Credenciais

1. **Bybit API:**
   - Conta na Bybit
   - API Key e Secret
   - Permissões de trading habilitadas

2. **Cloud Provider (se aplicável):**
   - Conta AWS/GCP/Azure
   - Credenciais configuradas
   - Billing habilitado

3. **Domínio (produção):**
   - Domínio registrado
   - Certificado SSL

---

## 💻 Deploy Local (Desenvolvimento)

### 1. Clonagem do Repositório

```bash
# Clonar repositório
git clone https://github.com/seu-usuario/crypto-trading-mvp.git
cd crypto-trading-mvp

# Verificar estrutura
ls -la
```

### 2. Configuração do Ambiente Python

```bash
# Criar ambiente virtual
python3 -m venv venv

# Ativar ambiente virtual
# Linux/Mac:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Verificar instalação
pip list
```

### 3. Configuração de Variáveis de Ambiente

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar configurações
nano .env
```

**Conteúdo do arquivo `.env`:**
```env
# Database
DATABASE_URL=sqlite:///./data/database/trading_bot.db

# Bybit API
BYBIT_API_KEY=sua_api_key_aqui
BYBIT_API_SECRET=seu_api_secret_aqui
BYBIT_TESTNET=true

# Security
SECRET_KEY=sua_chave_secreta_muito_longa_e_segura
ENCRYPTION_KEY=sua_chave_de_criptografia_32_bytes

# Services
API_HOST=0.0.0.0
API_PORT=8000
STREAMLIT_PORT=8501

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

### 4. Inicialização do Banco de Dados

```bash
# Criar diretórios necessários
mkdir -p data/database logs

# Inicializar banco (SQLite para desenvolvimento)
python -c "
from src.models.database import init_database
init_database()
print('Database initialized successfully')
"
```

### 5. Teste dos Componentes

```bash
# Testar API
cd crypto-trading-mvp
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload &

# Aguardar inicialização
sleep 5

# Testar endpoint de saúde
curl http://localhost:8000/health

# Testar Dashboard (em outro terminal)
streamlit run src/dashboard/main.py --server.port 8501 &

# Testar Bot Worker
python -m src.bot.worker &
```

### 6. Script de Inicialização Automática

```bash
# Usar script fornecido
chmod +x start_services.py
python start_services.py

# Ou criar script personalizado
cat > start_dev.sh << 'EOF'
#!/bin/bash

# Ativar ambiente virtual
source venv/bin/activate

# Iniciar serviços em background
echo "Starting FastAPI..."
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload &
API_PID=$!

echo "Starting Streamlit..."
streamlit run src/dashboard/main.py --server.port 8501 &
DASHBOARD_PID=$!

echo "Starting Bot Worker..."
python -m src.bot.worker &
BOT_PID=$!

echo "Services started:"
echo "- API: http://localhost:8000"
echo "- Dashboard: http://localhost:8501"
echo "- Bot Worker: Background process"

# Salvar PIDs para parada posterior
echo $API_PID > .api.pid
echo $DASHBOARD_PID > .dashboard.pid
echo $BOT_PID > .bot.pid

echo "To stop services, run: ./stop_dev.sh"
EOF

chmod +x start_dev.sh
```

### 7. Script de Parada

```bash
cat > stop_dev.sh << 'EOF'
#!/bin/bash

echo "Stopping services..."

# Parar serviços usando PIDs salvos
if [ -f .api.pid ]; then
    kill $(cat .api.pid) 2>/dev/null
    rm .api.pid
    echo "- API stopped"
fi

if [ -f .dashboard.pid ]; then
    kill $(cat .dashboard.pid) 2>/dev/null
    rm .dashboard.pid
    echo "- Dashboard stopped"
fi

if [ -f .bot.pid ]; then
    kill $(cat .bot.pid) 2>/dev/null
    rm .bot.pid
    echo "- Bot Worker stopped"
fi

echo "All services stopped"
EOF

chmod +x stop_dev.sh
```

---

## 🐳 Deploy com Docker

### 1. Verificação dos Dockerfiles

O projeto inclui Dockerfiles otimizados para cada componente:

```bash
# Verificar Dockerfiles
ls docker/
# Dockerfile.api
# Dockerfile.dashboard  
# Dockerfile.bot
```

### 2. Configuração do Docker Compose

**Arquivo `docker-compose.yml` (já incluído):**
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: trading_bot
      POSTGRES_USER: trading_user
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./docker/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U trading_user -d trading_bot"]
      interval: 30s
      timeout: 10s
      retries: 5

  api:
    build:
      context: .
      dockerfile: docker/Dockerfile.api
    environment:
      - DATABASE_URL=postgresql://trading_user:secure_password@postgres:5432/trading_bot
      - BYBIT_API_KEY=${BYBIT_API_KEY}
      - BYBIT_API_SECRET=${BYBIT_API_SECRET}
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data

  dashboard:
    build:
      context: .
      dockerfile: docker/Dockerfile.dashboard
    environment:
      - API_URL=http://api:8000
    ports:
      - "8501:8501"
    depends_on:
      - api
    volumes:
      - ./logs:/app/logs

  bot:
    build:
      context: .
      dockerfile: docker/Dockerfile.bot
    environment:
      - DATABASE_URL=postgresql://trading_user:secure_password@postgres:5432/trading_bot
      - BYBIT_API_KEY=${BYBIT_API_KEY}
      - BYBIT_API_SECRET=${BYBIT_API_SECRET}
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./docker/nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - api
      - dashboard

volumes:
  postgres_data:
```

### 3. Build e Deploy

```bash
# Configurar variáveis de ambiente
export BYBIT_API_KEY="sua_api_key"
export BYBIT_API_SECRET="seu_api_secret"

# Build das imagens
docker compose build

# Iniciar todos os serviços
docker compose up -d

# Verificar status
docker compose ps

# Ver logs
docker compose logs -f

# Parar serviços
docker compose down
```

### 4. Comandos Úteis Docker

```bash
# Rebuild específico
docker compose build api
docker compose up -d api

# Logs de serviço específico
docker compose logs -f api

# Executar comando em container
docker compose exec api bash

# Backup do banco
docker compose exec postgres pg_dump -U trading_user trading_bot > backup.sql

# Restaurar banco
docker compose exec -T postgres psql -U trading_user trading_bot < backup.sql

# Limpar volumes (CUIDADO!)
docker compose down -v
```

### 5. Configuração de Produção Docker

**docker-compose.prod.yml:**
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - internal
    # Não expor porta externamente

  api:
    build:
      context: .
      dockerfile: docker/Dockerfile.api
    environment:
      - DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/${DB_NAME}
      - SECRET_KEY=${SECRET_KEY}
      - BYBIT_API_KEY=${BYBIT_API_KEY}
      - BYBIT_API_SECRET=${BYBIT_API_SECRET}
    networks:
      - internal
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
    restart: unless-stopped

  dashboard:
    build:
      context: .
      dockerfile: docker/Dockerfile.dashboard
    environment:
      - API_URL=http://api:8000
    networks:
      - internal
    restart: unless-stopped

  bot:
    build:
      context: .
      dockerfile: docker/Dockerfile.bot
    environment:
      - DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/${DB_NAME}
      - BYBIT_API_KEY=${BYBIT_API_KEY}
      - BYBIT_API_SECRET=${BYBIT_API_SECRET}
    networks:
      - internal
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./docker/nginx/nginx.prod.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    networks:
      - internal
      - external
    restart: unless-stopped

  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./docker/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
    networks:
      - internal

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    volumes:
      - grafana_data:/var/lib/grafana
    networks:
      - internal

networks:
  internal:
    driver: bridge
  external:
    driver: bridge

volumes:
  postgres_data:
  grafana_data:
```

---

## 🌐 Deploy em Produção

### 1. Preparação do Servidor

```bash
# Atualizar sistema (Ubuntu/Debian)
sudo apt update && sudo apt upgrade -y

# Instalar dependências
sudo apt install -y \
    curl \
    git \
    nginx \
    postgresql \
    postgresql-contrib \
    python3 \
    python3-pip \
    python3-venv \
    supervisor \
    ufw \
    fail2ban

# Configurar firewall
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https
sudo ufw --force enable
```

### 2. Configuração do PostgreSQL

```bash
# Iniciar PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Criar usuário e banco
sudo -u postgres psql << 'EOF'
CREATE USER trading_user WITH PASSWORD 'senha_muito_segura';
CREATE DATABASE trading_bot OWNER trading_user;
GRANT ALL PRIVILEGES ON DATABASE trading_bot TO trading_user;
\q
EOF

# Configurar acesso
sudo nano /etc/postgresql/15/main/pg_hba.conf
# Adicionar linha:
# local   trading_bot     trading_user                    md5

# Reiniciar PostgreSQL
sudo systemctl restart postgresql
```

### 3. Deploy da Aplicação

```bash
# Criar usuário para aplicação
sudo useradd -m -s /bin/bash trading
sudo su - trading

# Clonar repositório
git clone https://github.com/seu-usuario/crypto-trading-mvp.git
cd crypto-trading-mvp

# Configurar ambiente Python
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
nano .env
```

**Configuração de produção `.env`:**
```env
# Database
DATABASE_URL=postgresql://trading_user:senha_muito_segura@localhost:5432/trading_bot

# Bybit API
BYBIT_API_KEY=sua_api_key_real
BYBIT_API_SECRET=seu_api_secret_real
BYBIT_TESTNET=false

# Security
SECRET_KEY=chave_secreta_super_longa_e_aleatoria_para_producao
ENCRYPTION_KEY=chave_de_32_bytes_para_criptografia

# Services
API_HOST=127.0.0.1
API_PORT=8000
STREAMLIT_PORT=8501

# Logging
LOG_LEVEL=WARNING
LOG_FILE=/home/trading/crypto-trading-mvp/logs/app.log
```

### 4. Configuração do Supervisor

```bash
# Criar configurações do Supervisor
sudo nano /etc/supervisor/conf.d/trading-api.conf
```

**trading-api.conf:**
```ini
[program:trading-api]
command=/home/trading/crypto-trading-mvp/venv/bin/python -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000
directory=/home/trading/crypto-trading-mvp
user=trading
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/home/trading/crypto-trading-mvp/logs/api.log
environment=PATH="/home/trading/crypto-trading-mvp/venv/bin"
```

**trading-dashboard.conf:**
```ini
[program:trading-dashboard]
command=/home/trading/crypto-trading-mvp/venv/bin/streamlit run src/dashboard/main.py --server.port 8501 --server.address 127.0.0.1
directory=/home/trading/crypto-trading-mvp
user=trading
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/home/trading/crypto-trading-mvp/logs/dashboard.log
environment=PATH="/home/trading/crypto-trading-mvp/venv/bin"
```

**trading-bot.conf:**
```ini
[program:trading-bot]
command=/home/trading/crypto-trading-mvp/venv/bin/python -m src.bot.worker
directory=/home/trading/crypto-trading-mvp
user=trading
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/home/trading/crypto-trading-mvp/logs/bot.log
environment=PATH="/home/trading/crypto-trading-mvp/venv/bin"
```

```bash
# Recarregar configurações
sudo supervisorctl reread
sudo supervisorctl update

# Iniciar serviços
sudo supervisorctl start trading-api
sudo supervisorctl start trading-dashboard
sudo supervisorctl start trading-bot

# Verificar status
sudo supervisorctl status
```

### 5. Configuração do Nginx

```bash
sudo nano /etc/nginx/sites-available/trading-bot
```

**Configuração Nginx:**
```nginx
server {
    listen 80;
    server_name seu-dominio.com www.seu-dominio.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name seu-dominio.com www.seu-dominio.com;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/seu-dominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/seu-dominio.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # Security Headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";
    
    # Dashboard (root)
    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 86400;
    }
    
    # API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Static files
    location /static/ {
        alias /home/trading/crypto-trading-mvp/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

```bash
# Ativar site
sudo ln -s /etc/nginx/sites-available/trading-bot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 6. Configuração SSL com Let's Encrypt

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx

# Obter certificado
sudo certbot --nginx -d seu-dominio.com -d www.seu-dominio.com

# Configurar renovação automática
sudo crontab -e
# Adicionar linha:
# 0 12 * * * /usr/bin/certbot renew --quiet
```

---

## ☁️ Deploy na AWS

### 1. Configuração da Infraestrutura

**Usando AWS CLI:**
```bash
# Configurar credenciais
aws configure

# Criar VPC
aws ec2 create-vpc --cidr-block 10.0.0.0/16 --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=trading-bot-vpc}]'

# Criar subnets
aws ec2 create-subnet --vpc-id vpc-xxxxxxxxx --cidr-block 10.0.1.0/24 --availability-zone us-east-1a

# Criar security group
aws ec2 create-security-group --group-name trading-bot-sg --description "Trading Bot Security Group" --vpc-id vpc-xxxxxxxxx
```

### 2. Deploy com EC2

```bash
# Lançar instância EC2
aws ec2 run-instances \
    --image-id ami-0c02fb55956c7d316 \
    --count 1 \
    --instance-type t3.medium \
    --key-name sua-chave \
    --security-group-ids sg-xxxxxxxxx \
    --subnet-id subnet-xxxxxxxxx \
    --user-data file://user-data.sh
```

**user-data.sh:**
```bash
#!/bin/bash
yum update -y
yum install -y docker git

# Instalar Docker Compose
curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Iniciar Docker
systemctl start docker
systemctl enable docker

# Clonar repositório
cd /opt
git clone https://github.com/seu-usuario/crypto-trading-mvp.git
cd crypto-trading-mvp

# Configurar variáveis de ambiente
cat > .env << 'EOF'
DATABASE_URL=postgresql://trading_user:senha_segura@postgres:5432/trading_bot
BYBIT_API_KEY=sua_api_key
BYBIT_API_SECRET=seu_api_secret
SECRET_KEY=chave_secreta_longa
EOF

# Deploy com Docker Compose
docker-compose -f docker-compose.prod.yml up -d
```

### 3. Deploy com ECS (Elastic Container Service)

**task-definition.json:**
```json
{
  "family": "trading-bot",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "api",
      "image": "seu-repo/trading-bot-api:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DATABASE_URL",
          "value": "postgresql://user:pass@rds-endpoint:5432/db"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/trading-bot",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "api"
        }
      }
    }
  ]
}
```

### 4. Deploy com RDS

```bash
# Criar subnet group
aws rds create-db-subnet-group \
    --db-subnet-group-name trading-bot-subnet-group \
    --db-subnet-group-description "Trading Bot DB Subnet Group" \
    --subnet-ids subnet-xxxxxxxxx subnet-yyyyyyyyy

# Criar instância RDS
aws rds create-db-instance \
    --db-instance-identifier trading-bot-db \
    --db-instance-class db.t3.micro \
    --engine postgres \
    --master-username trading_user \
    --master-user-password senha_muito_segura \
    --allocated-storage 20 \
    --db-subnet-group-name trading-bot-subnet-group \
    --vpc-security-group-ids sg-xxxxxxxxx
```

---

## 🔧 Deploy no Google Cloud

### 1. Configuração do Projeto

```bash
# Instalar gcloud CLI
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Configurar projeto
gcloud init
gcloud config set project seu-projeto-id
```

### 2. Deploy com Cloud Run

```bash
# Build da imagem
gcloud builds submit --tag gcr.io/seu-projeto-id/trading-bot-api

# Deploy no Cloud Run
gcloud run deploy trading-bot-api \
    --image gcr.io/seu-projeto-id/trading-bot-api \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --set-env-vars DATABASE_URL="postgresql://user:pass@host:5432/db"
```

### 3. Deploy com GKE (Google Kubernetes Engine)

```bash
# Criar cluster
gcloud container clusters create trading-bot-cluster \
    --zone us-central1-a \
    --num-nodes 3 \
    --machine-type e2-medium

# Obter credenciais
gcloud container clusters get-credentials trading-bot-cluster --zone us-central1-a

# Deploy com Kubernetes
kubectl apply -f k8s/
```

---

## ⚙️ Deploy com Kubernetes

### 1. Configurações Kubernetes

**namespace.yaml:**
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: trading-bot
```

**configmap.yaml:**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: trading-bot-config
  namespace: trading-bot
data:
  DATABASE_URL: "postgresql://trading_user:password@postgres:5432/trading_bot"
  API_HOST: "0.0.0.0"
  API_PORT: "8000"
```

**secret.yaml:**
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: trading-bot-secrets
  namespace: trading-bot
type: Opaque
data:
  BYBIT_API_KEY: <base64_encoded_key>
  BYBIT_API_SECRET: <base64_encoded_secret>
  SECRET_KEY: <base64_encoded_secret_key>
```

**postgres-deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: trading-bot
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15
        env:
        - name: POSTGRES_DB
          value: trading_bot
        - name: POSTGRES_USER
          value: trading_user
        - name: POSTGRES_PASSWORD
          value: password
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
      volumes:
      - name: postgres-storage
        persistentVolumeClaim:
          claimName: postgres-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: trading-bot
spec:
  selector:
    app: postgres
  ports:
  - port: 5432
    targetPort: 5432
```

**api-deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: trading-bot-api
  namespace: trading-bot
spec:
  replicas: 2
  selector:
    matchLabels:
      app: trading-bot-api
  template:
    metadata:
      labels:
        app: trading-bot-api
    spec:
      containers:
      - name: api
        image: trading-bot-api:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: trading-bot-config
        - secretRef:
            name: trading-bot-secrets
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: trading-bot-api-service
  namespace: trading-bot
spec:
  selector:
    app: trading-bot-api
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

### 2. Deploy dos Recursos

```bash
# Aplicar todas as configurações
kubectl apply -f k8s/

# Verificar status
kubectl get pods -n trading-bot
kubectl get services -n trading-bot

# Ver logs
kubectl logs -f deployment/trading-bot-api -n trading-bot

# Escalar aplicação
kubectl scale deployment trading-bot-api --replicas=5 -n trading-bot
```

---

## 📊 Monitoramento e Logs

### 1. Configuração do Prometheus

**prometheus.yml:**
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'trading-bot-api'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'

  - job_name: 'postgres'
    static_configs:
      - targets: ['localhost:9187']

  - job_name: 'node'
    static_configs:
      - targets: ['localhost:9100']
```

### 2. Configuração do Grafana

**Dashboard JSON para importar:**
```json
{
  "dashboard": {
    "title": "Trading Bot Metrics",
    "panels": [
      {
        "title": "API Requests",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      },
      {
        "title": "Active Trading Bots",
        "type": "stat",
        "targets": [
          {
            "expr": "trading_bots_active",
            "legendFormat": "Active Bots"
          }
        ]
      }
    ]
  }
}
```

### 3. Configuração de Logs

**logrotate configuration:**
```bash
sudo nano /etc/logrotate.d/trading-bot
```

```
/home/trading/crypto-trading-mvp/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 trading trading
    postrotate
        sudo supervisorctl restart trading-api trading-dashboard trading-bot
    endscript
}
```

### 4. Alertas com AlertManager

**alertmanager.yml:**
```yaml
global:
  smtp_smarthost: 'localhost:587'
  smtp_from: 'alerts@seu-dominio.com'

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'web.hook'

receivers:
- name: 'web.hook'
  email_configs:
  - to: 'admin@seu-dominio.com'
    subject: 'Trading Bot Alert: {{ .GroupLabels.alertname }}'
    body: |
      {{ range .Alerts }}
      Alert: {{ .Annotations.summary }}
      Description: {{ .Annotations.description }}
      {{ end }}
```

---

## 💾 Backup e Recuperação

### 1. Backup do Banco de Dados

```bash
# Script de backup automático
cat > backup_db.sh << 'EOF'
#!/bin/bash

BACKUP_DIR="/home/trading/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="trading_bot"
DB_USER="trading_user"

# Criar diretório se não existir
mkdir -p $BACKUP_DIR

# Backup do banco
pg_dump -h localhost -U $DB_USER -d $DB_NAME > $BACKUP_DIR/trading_bot_$DATE.sql

# Compactar backup
gzip $BACKUP_DIR/trading_bot_$DATE.sql

# Manter apenas últimos 30 backups
find $BACKUP_DIR -name "trading_bot_*.sql.gz" -mtime +30 -delete

echo "Backup completed: trading_bot_$DATE.sql.gz"
EOF

chmod +x backup_db.sh

# Agendar backup diário
crontab -e
# Adicionar linha:
# 0 2 * * * /home/trading/backup_db.sh
```

### 2. Backup de Arquivos

```bash
# Script de backup de arquivos
cat > backup_files.sh << 'EOF'
#!/bin/bash

BACKUP_DIR="/home/trading/backups"
DATE=$(date +%Y%m%d_%H%M%S)
SOURCE_DIR="/home/trading/crypto-trading-mvp"

# Backup de configurações e logs
tar -czf $BACKUP_DIR/files_$DATE.tar.gz \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    $SOURCE_DIR

# Upload para S3 (opcional)
# aws s3 cp $BACKUP_DIR/files_$DATE.tar.gz s3://seu-bucket/backups/

echo "File backup completed: files_$DATE.tar.gz"
EOF

chmod +x backup_files.sh
```

### 3. Restauração

```bash
# Restaurar banco de dados
gunzip -c trading_bot_20250115_020000.sql.gz | psql -h localhost -U trading_user -d trading_bot

# Restaurar arquivos
tar -xzf files_20250115_020000.tar.gz -C /home/trading/
```

---

## 🔒 Segurança em Produção

### 1. Configurações de Segurança

**Firewall (UFW):**
```bash
# Configuração restritiva
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

**Fail2Ban:**
```bash
# Configurar fail2ban
sudo nano /etc/fail2ban/jail.local
```

```ini
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log

[nginx-http-auth]
enabled = true
filter = nginx-http-auth
port = http,https
logpath = /var/log/nginx/error.log
```

### 2. Secrets Management

```bash
# Usar HashiCorp Vault (exemplo)
vault kv put secret/trading-bot \
    bybit_api_key="sua_api_key" \
    bybit_api_secret="seu_api_secret" \
    database_password="senha_db"

# Ou AWS Secrets Manager
aws secretsmanager create-secret \
    --name "trading-bot/api-keys" \
    --description "Trading Bot API Keys" \
    --secret-string '{"bybit_api_key":"key","bybit_api_secret":"secret"}'
```

### 3. SSL/TLS Hardening

**nginx SSL configuration:**
```nginx
# Configuração SSL robusta
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
ssl_prefer_server_ciphers off;
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 10m;
ssl_stapling on;
ssl_stapling_verify on;

# HSTS
add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;

# Security headers
add_header X-Frame-Options DENY always;
add_header X-Content-Type-Options nosniff always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
```

---

## 🔧 Troubleshooting

### Problemas Comuns

#### 1. Erro de Conexão com Banco
```bash
# Verificar status do PostgreSQL
sudo systemctl status postgresql

# Verificar logs
sudo tail -f /var/log/postgresql/postgresql-15-main.log

# Testar conexão
psql -h localhost -U trading_user -d trading_bot
```

#### 2. API não Responde
```bash
# Verificar processo
sudo supervisorctl status trading-api

# Ver logs
sudo supervisorctl tail -f trading-api

# Reiniciar serviço
sudo supervisorctl restart trading-api
```

#### 3. Dashboard não Carrega
```bash
# Verificar porta
netstat -tlnp | grep 8501

# Verificar logs do Streamlit
tail -f logs/dashboard.log

# Testar localmente
curl http://localhost:8501
```

#### 4. Bot não Executa Trades
```bash
# Verificar logs do bot
tail -f logs/bot.log

# Verificar configuração
python -c "
from src.bot.worker import TradingWorker
worker = TradingWorker()
print(worker.get_status())
"

# Testar conexão Bybit
python -c "
from src.bot.bybit_provider import BybitProvider
provider = BybitProvider('key', 'secret', testnet=True)
print('Connection OK')
"
```

### Scripts de Diagnóstico

```bash
# Script de diagnóstico completo
cat > diagnose.sh << 'EOF'
#!/bin/bash

echo "=== Trading Bot Diagnostics ==="
echo "Date: $(date)"
echo

echo "=== System Info ==="
uname -a
echo "Uptime: $(uptime)"
echo "Memory: $(free -h | grep Mem)"
echo "Disk: $(df -h / | tail -1)"
echo

echo "=== Services Status ==="
sudo supervisorctl status
echo

echo "=== Network ==="
netstat -tlnp | grep -E "(8000|8501|5432)"
echo

echo "=== Recent Logs ==="
echo "API Logs:"
tail -5 logs/api.log
echo
echo "Bot Logs:"
tail -5 logs/bot.log
echo
echo "Dashboard Logs:"
tail -5 logs/dashboard.log
echo

echo "=== Database ==="
psql -h localhost -U trading_user -d trading_bot -c "SELECT COUNT(*) FROM clients;"
echo

echo "=== End Diagnostics ==="
EOF

chmod +x diagnose.sh
```

---

## 📚 Recursos Adicionais

### Documentação Relacionada
- [API Documentation](API_DOCUMENTATION.md)
- [Strategy Guide](STRATEGY_GUIDE.md)
- [User Manual](USER_MANUAL.md)

### Links Úteis
- **Docker:** https://docs.docker.com/
- **Kubernetes:** https://kubernetes.io/docs/
- **AWS:** https://docs.aws.amazon.com/
- **Google Cloud:** https://cloud.google.com/docs/
- **Nginx:** https://nginx.org/en/docs/
- **PostgreSQL:** https://www.postgresql.org/docs/

### Suporte
- **GitHub Issues:** https://github.com/seu-repo/issues
- **Discord:** https://discord.gg/trading-bot
- **Email:** support@trading-bot.com

---

**Última atualização:** Janeiro 2025  
**Versão do guia:** 1.0.0

