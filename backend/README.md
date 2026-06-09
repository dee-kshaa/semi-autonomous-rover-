# Backend (FastAPI)

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Set a strong `SECRET_KEY` before production deployment and set `ENVIRONMENT=production`.

## API docs

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Key endpoints

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/users/me`
- `POST /api/v1/signals/ingest`
- `GET /api/v1/analytics/summary`
- `GET /api/v1/analytics/trend`
- `GET /api/v1/analytics/heatmap`
- `GET /api/v1/analytics/operator-comparison`
