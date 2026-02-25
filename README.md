# WhatsApp/Telegram Front Desk

Multi-tenant AI-powered front desk bot for **restaurants** and **hostels**. Each business gets a Telegram or WhatsApp bot that handles reservations, FAQs, reminders, and human handoff.

## Features

- **Natural-language booking** — Customers book tables or rooms via conversation (AI intent + slot selection).
- **24/7 FAQs** — Hours, location, menu, pricing, policies (configurable per business).
- **Booking management** — View, reschedule, cancel appointments; automated 24h and 1h reminders.
- **Human handoff** — Escalate to staff when needed; support sessions tracked.
- **Multi-tenant** — Per-business Telegram bot tokens; same codebase for Telegram (dev) and WhatsApp (production).
- **AI multi-provider** — OpenAI, Groq, or Google Gemini (default: Groq with `llama-3.1-8b-instant`).

## Stack

- **Python 3.11+**, FastAPI, SQLAlchemy (async) + **Neon PostgreSQL**
- **python-telegram-bot** v20+ (async), Meta Cloud API (WhatsApp)
- **Alembic** for migrations, **APScheduler** for reminders, **pydantic-settings** for config
- **httpx** for all HTTP (no `requests`)

## Prerequisites

- Python 3.11+
- A [Neon](https://neon.tech) PostgreSQL database
- For Telegram: a bot token from [@BotFather](https://t.me/BotFather). For production WhatsApp: Meta app credentials.

## Quick start

### 1. Clone and install

```bash
git clone <repo-url>
cd whatsapp-frontdesk-recep
pip install -r requirements.txt
```

Or with [uv](https://github.com/astral-sh/uv):

```bash
uv sync
```

### 2. Environment

Copy the example env and fill in at least the database and (for Telegram) bot token:

```bash
cp .env.example .env
```

Edit `.env`:

- **`NEON_DATABASE_URL`** — PostgreSQL connection string from [Neon](https://neon.tech) (required).
- **`TELEGRAM_BOT_TOKEN`** — From BotFather (for testing the Telegram channel).
- **`GROQ_API_KEY`** — If using default AI provider Groq ([console](https://console.groq.com)).

See `.env.example` for all options (OpenAI, Gemini, WhatsApp, Google Calendar, etc.).

### 3. Database and migrations

Create a database in Neon, set `NEON_DATABASE_URL` in `.env`, then run:

```bash
alembic upgrade head
```

Full steps (creating the DB, connection string, troubleshooting): **[MIGRATIONS.md](MIGRATIONS.md)**.

### 4. Run the API server

```bash
uvicorn app.main:app --reload
```

- API: `http://localhost:8000`
- Docs: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`

### 5. Telegram webhook (production) or polling (dev)

**Webhook (recommended for production):**

- Set `TELEGRAM_WEBHOOK_URL` in `.env` to your public base URL (e.g. `https://your-domain.com`).
- Register the webhook: `POST /webhook/telegram/{business_id}` is the endpoint; your app must be reachable by Telegram.

**Polling (local dev):**

```bash
python -m app.bot.bot
```

(Ensure the webhook is not set for that bot, or Telegram will not deliver updates to polling.)

## Project layout

| Path | Purpose |
|------|--------|
| `app/main.py` | FastAPI app, lifespan, routers |
| `app/api/routes/` | Webhooks (Telegram/WhatsApp), appointments, businesses, onboarding, FAQs |
| `app/bot/` | Telegram entry, handlers (booking, appointments, FAQ, support), keyboards |
| `app/channels/` | Abstract channel + Telegram/WhatsApp implementations |
| `app/services/` | AI, booking, calendar, reminders, FAQ, customer, business, conversation |
| `app/models/db/` | SQLAlchemy models; `schemas/` for Pydantic |
| `app/core/` | Config, database (Neon async), scheduler |
| `migrations/` | Alembic migrations |

Detailed structure and schema: **claude.md** (master reference for contributors).

## Uploading FAQs

Businesses can manage FAQs via the API:

- **Add one** — `POST /api/businesses/{business_id}/faqs` with JSON `{"question": "...", "answer": "...", "keywords": ["..."]}`.
- **List** — `GET /api/businesses/{business_id}/faqs`.
- **Delete** — `DELETE /api/faqs/{faq_id}`.
- **Bulk import** — `POST /api/businesses/{business_id}/faqs/import`:
  - **JSON**: body `{"faqs": [{"question": "...", "answer": "...", "keywords": []}, ...]}`.
  - **File**: upload a **CSV** (columns `question`, `answer`, `keywords`) or a **TXT** with Q/A blocks:

    ```
    Q: What are your opening hours?
    A: We are open 9am to 9pm every day.
    K: hours, opening, time

    Q: Do you take reservations?
    A: Yes, you can book via this bot or call us.
    ```

Use the API docs at `/docs` to try these (e.g. upload a `.txt` or `.csv` file for import).

## Docs

- **[MIGRATIONS.md](MIGRATIONS.md)** — How to run and create migrations, Neon setup.
- **[BUILD_LOG.md](BUILD_LOG.md)** — Changelog of implementation.
- **claude.md** — Full spec, schema, and quick commands.

## License

Private / unlicensed unless otherwise stated.
