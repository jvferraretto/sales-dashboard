# Sales Dashboard — Mercado Livre + Shopee

Dashboard de vendas unificado para acompanhar pedidos e faturamento do Mercado Livre e da Shopee.

## Stack

- **Backend**: Python + FastAPI + SQLAlchemy + SQLite + APScheduler
- **Frontend**: Next.js 14 + Tailwind CSS + Recharts + SWR

## Pré-requisitos

- Python 3.11+
- Node.js 18+ e npm
- App registrado no [Portal de Desenvolvedores do Mercado Livre](https://developers.mercadolibre.com.br)
- App registrado no [Shopee Open Platform](https://open.shopee.com)

## Setup

### 1. Configure as variáveis de ambiente

```bash
cp .env.example .env
# Edite .env e preencha as credenciais das APIs
```

### 2. Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux
pip install -r requirements.txt
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

O banco `data/sales.db` é criado automaticamente.
Swagger UI disponível em: http://localhost:8000/docs

### 3. Frontend

```bash
# Em outro terminal
cd frontend
npm install
npm run dev
```

App disponível em: http://localhost:3000

### 4. Conectar as plataformas (uma vez)

1. Abra http://localhost:3000/settings
2. Clique **Conectar com Mercado Livre** → autorize → volta para Settings
3. Clique **Conectar com Shopee** → autorize → volta para Settings

### 5. Primeira sincronização

Abra o Dashboard e clique **Sync Agora**.

## Redirect URIs para registrar nos apps

| Plataforma | Redirect URI |
|-----------|-------------|
| Mercado Livre | `http://localhost:8000/auth/mercadolivre/callback` |
| Shopee | `http://localhost:8000/auth/shopee/callback` |

## Sincronização automática

Os pedidos são sincronizados automaticamente todos os dias às **02:00 UTC**.
Você pode disparar uma sincronização manual pelo botão **Sync Agora** no Dashboard.

## Estrutura do projeto

```
sales-dashboard/
├── backend/          # API FastAPI
│   ├── api/          # Rotas
│   ├── integrations/ # Clientes ML e Shopee
│   └── data/         # SQLite (gerado automaticamente)
└── frontend/         # Next.js
    └── src/
        ├── app/      # Páginas
        ├── components/
        └── lib/
```
