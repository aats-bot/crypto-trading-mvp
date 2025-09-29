# Docker Setup - Crypto Trading MVP

## Estrutura Criada

`
docker/
├── api/                 # Container da API FastAPI
├── dashboard/           # Container do Dashboard Streamlit
├── worker/              # Container do Worker (a criar)
├── database/            # Configurações do banco (a criar)
├── nginx/               # Reverse proxy (a criar)
└── scripts/             # Scripts de automação
`

## Como Usar

### 1. Configurar Ambiente
`powershell
# Copiar configurações de ambiente
copy .env.docker .env

# Editar .env com suas chaves reais
notepad .env
`

### 2. Construir Imagens
`powershell
# Executar script de build
.\docker\scripts\build.ps1

# Ou manualmente
docker-compose build
`

### 3. Iniciar Serviços
`powershell
# Iniciar todos os serviços
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar serviços
docker-compose down
`

## URLs dos Serviços

- **API:** http://localhost:8000
- **Dashboard:** http://localhost:8501
- **Docs API:** http://localhost:8000/docs

## Comandos Úteis

`powershell
# Ver status dos containers
docker-compose ps

# Executar comando em container
docker-compose exec api bash

# Ver logs específicos
docker-compose logs api
docker-compose logs dashboard

# Rebuild específico
docker-compose build api
docker-compose build dashboard
`

## Próximos Passos

1. ✅ Estrutura Docker criada
2. 🔄 Copiar Dockerfiles dos arquivos criados
3. 🔄 Organizar código na pasta app/
4. 🔄 Testar build e execução
5. 🔄 Configurar CI/CD
