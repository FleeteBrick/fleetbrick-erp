# 🏗️ Fleet&Brick ERP

SaaS B2B2C unificado para gestão de frotas e propriedades imobiliárias com inteligência artificial autônoma.

## 🎯 Visão
Unificar em uma única plataforma a gestão logística e imobiliária, eliminando planilhas e papel através de automação inteligente.

## 🏛️ Arquitetura Multi-Nível
- **Nível 1:** Super Admin (Dono do SaaS)
- **Nível 2:** Tenant Admin (Cliente B2B)
- **Nível 3:** End-User (Motorista/Inquilino)

## 🛠️ Stack Tecnológica
| Camada | Tecnologia |
|--------|-----------|
| Banco de Dados | Supabase (PostgreSQL + RLS) |
| Backend | Python FastAPI |
| Frontend | Next.js + Tailwind CSS |
| Pagamentos | Asaas (API + Webhooks) |
| E-mail | Resend |
| IA | OpenClaw Framework + MCP |

## 🚀 Deploy Rápido

```bash
# 1. Clone
git clone https://github.com/seu-usuario/fleetbrick-erp.git
cd fleetbrick-erp

# 2. Configure variáveis de ambiente
cp .env.example .env
# Edite .env com suas credenciais

# 3. Suba a infraestrutura
docker-compose up -d

# 4. Execute as migrations
psql $DATABASE_URL -f database/001_schema.sql
psql $DATABASE_URL -f database/002_rls.sql
psql $DATABASE_URL -f database/003_functions.sql
psql $DATABASE_URL -f database/004_seed.sql
psql $DATABASE_URL -f database/005_support_module.sql

# 5. Inicie o backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# 6. Inicie o frontend (outro terminal)
cd frontend
npm install
npm run dev
```

## 📧 Contato
- E-mail do sistema: fleetebrick@gmail.com
- Suporte: Via dashboard Super Admin → Central de Suporte

## 📄 Licença
Proprietário - Fleet&Brick Tecnologia Ltda.
