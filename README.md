# AI-Powered Mobile Network Intelligence Platform

## Folder structure

- `mobile_app/` Flutter client
- `backend/` FastAPI backend with JWT and analytics APIs
- `dashboard/` Plotly Dash app scaffold
- `ml_models/` ML training/inference modules
- `database/` PostgreSQL schema and setup

## Quick start

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

### Database

```bash
psql -U postgres -d network_intelligence -f database/schema/01_init.sql
```
