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

## Seed demo data (restaurant)

To add realistic restaurant services (table types) and FAQs to a business:

```bash
python -m scripts.seed_restaurant
```

Uses the first restaurant in the DB. To target a specific business:

```bash
python -m scripts.seed_restaurant --business-id YOUR_UUID
```

Adds: Table for 2/4/6, Private dining; FAQs for hours, location, reservations, parking, dietary options, payment, dress code, events, kids, WiFi. If the business has no location set, also sets working hours (Tue–Sun 12:00–22:00) and a sample address/phone.
