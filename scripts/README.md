# Scripts do Projeto

Este diretorio contem scripts auxiliares para CI/CD e operacoes do projeto.

## Estrutura

- **ci/** - Scripts de Continuous Integration
- **deploy/** - Scripts de deployment
- **quality/** - Scripts de verificacao de qualidade

## Scripts Disponiveis

### CI Scripts
- lint.sh - Executa linting do codigo
- test.sh - Executa testes
- build.sh - Constroi images Docker
- security-scan.sh - Executa scanning de seguranca

### Deploy Scripts
- deploy.sh - Script principal de deployment
- rollback.sh - Rollback para versao anterior
- health-check.sh - Verifica saude do sistema
- notify.sh - Envia notificacoes

### Quality Scripts
- check-coverage.sh - Verifica cobertura de testes
- check-complexity.sh - Verifica complexidade do codigo
- generate-report.sh - Gera relatorios de qualidade
