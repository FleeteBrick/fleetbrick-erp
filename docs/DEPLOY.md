# 🚀 Guia de Deploy - Fleet&Brick ERP

## Pré-requisitos
- Docker e Docker Compose
- Conta Supabase (ou PostgreSQL próprio)
- Conta Asaas (Sandbox e Produção)
- Conta Resend
- Domínio próprio (opcional para MVP)

## Passo a Passo

### 1. Configurar Variáveis de Ambiente
```bash
cp .env.example .env
# Edite .env com todas as credenciais
```

### 2. Subir Banco de Dados
```bash
# Via Supabase (recomendado)
# Ou via Docker local:
docker run -d --name postgres   -e POSTGRES_PASSWORD=senha   -e POSTGRES_DB=fleetbrick   -p 5432:5432 postgres:15

# Executar migrations
psql $DATABASE_URL -f database/001_schema.sql
psql $DATABASE_URL -f database/002_rls.sql
psql $DATABASE_URL -f database/003_functions.sql
psql $DATABASE_URL -f database/004_seed.sql
psql $DATABASE_URL -f database/005_support_module.sql
```

### 3. Deploy do Backend
```bash
cd backend
pip install -r requirements.txt

# Desenvolvimento
uvicorn main:app --reload

# Produção
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 4. Deploy do Frontend
```bash
cd frontend
npm install
npm run build
npm start
```

### 5. Configurar Webhooks
- Asaas: Configurar webhook para `/webhooks/asaas`
- Resend: Configurar webhook para `/webhooks/resend`

### 6. SSL e Domínio (Produção)
```bash
# Usar Cloudflare ou Let's Encrypt
certbot --nginx -d app.fleetbrick.com
```

## Monitoramento
- Logs: `docker-compose logs -f`
- Health Check: `GET /health`
- Métricas: Implementar Prometheus + Grafana
