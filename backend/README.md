# Front Desk API (backend)

FastAPI app for the WhatsApp/Telegram front desk bot. Run all commands from this directory.

## Setup

```bash
cp .env.example .env
# Edit .env: NEON_DATABASE_URL, TELEGRAM_BOT_TOKEN, GROQ_API_KEY (or other AI keys)
pip install -r requirements.txt
alembic upgrade head
```

## Run

```bash
uvicorn app.main:app --reload
```

API: http://localhost:8000  
Docs: http://localhost:8000/docs

## Migrations

```bash
alembic upgrade head
alembic revision --autogenerate -m "description"
```

See repo root **MIGRATIONS.md** for full guide.
