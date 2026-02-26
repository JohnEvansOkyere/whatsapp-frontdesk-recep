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
cd backend
pip install -r requirements.txt
```

Or with [uv](https://github.com/astral-sh/uv):

```bash
cd backend && uv sync
```

### 2. Environment

Copy the example env into the backend and fill in at least the database and (for Telegram) bot token:

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env`:

- **`NEON_DATABASE_URL`** — PostgreSQL connection string from [Neon](https://neon.tech) (required).
- **`TELEGRAM_BOT_TOKEN`** — From BotFather (for testing the Telegram channel).
- **`GROQ_API_KEY`** — If using default AI provider Groq ([console](https://console.groq.com)).

See `backend/.env.example` for all options (OpenAI, Gemini, WhatsApp, Google Calendar, etc.).

### 3. Database and migrations

Create a database in Neon, set `NEON_DATABASE_URL` in `backend/.env`, then run from the **backend** directory:

```bash
cd backend
alembic upgrade head
```

Full steps (creating the DB, connection string, troubleshooting): **[MIGRATIONS.md](MIGRATIONS.md)**.

### 4. Run the API server

From the **backend** directory:

```bash
cd backend
uvicorn app.main:app --reload
```

- API: `http://localhost:8000`
- Docs: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`

### 5. Telegram webhook (production) or polling (dev)

**Webhook (recommended for production):**

- Set `TELEGRAM_WEBHOOK_URL` in `backend/.env` to your public base URL (e.g. `https://your-domain.com`).
- Register the webhook: `POST /webhook/telegram/{business_id}` is the endpoint; your app must be reachable by Telegram.

**Polling (local dev):** from the backend directory:

```bash
cd backend
python -m app.bot.bot
```

(Ensure the webhook is not set for that bot, or Telegram will not deliver updates to polling.)

### 6. Dashboard (optional)

Web UI for creating businesses, managing services/FAQs, and viewing bookings:

```bash
cd dashboard
npm install
cp .env.local.example .env.local   # set NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
```

Open [http://localhost:3000](http://localhost:3000). See **dashboard/README.md** for details.

## Project layout

| Path | Purpose |
|------|--------|
| `backend/` | Python FastAPI app (run all backend commands from here) |
| `backend/app/main.py` | FastAPI app, lifespan, routers |
| `backend/app/api/routes/` | Webhooks (Telegram/WhatsApp), appointments, businesses, onboarding, FAQs |
| `backend/app/bot/` | Telegram entry, handlers (booking, appointments, FAQ, support), keyboards |
| `backend/app/channels/` | Abstract channel + Telegram/WhatsApp implementations |
| `backend/app/services/` | AI, booking, calendar, reminders, FAQ, customer, business, conversation |
| `backend/app/models/db/` | SQLAlchemy models; `schemas/` for Pydantic |
| `backend/app/core/` | Config, database (Neon async), scheduler |
| `backend/migrations/` | Alembic migrations |
| `dashboard/` | Next.js client dashboard (businesses, bookings, FAQs, services, settings) |

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

## Deploy on Render (free tier)

1. **Push the repo** to GitHub (or connect GitLab).

2. **Create a Web Service** on [Render](https://render.com): **Dashboard → New → Web Service**. Connect your repo and choose the branch.

3. **Configure (free tier — no Blueprint):**
   - **Root Directory:** `backend` (so all commands run from the backend folder).
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Plan:** Free (or Starter if you prefer always-on).

4. **Pre-Deploy (optional):** Under **Advanced**, add **Pre-Deploy Command:** `alembic upgrade head` so migrations run before each deploy.

6. **Set environment variables** in Render Dashboard → **Environment**:
   - **`NEON_DATABASE_URL`** (required) — Your Neon PostgreSQL connection string.
   - **`TELEGRAM_BOT_TOKEN`** — From [@BotFather](https://t.me/BotFather).
   - **`GROQ_API_KEY`** — If using default AI provider Groq.
   - **`ENVIRONMENT`** — Set to `production`.
   - Optional: `TELEGRAM_WEBHOOK_URL` (your Render URL, e.g. `https://your-service.onrender.com`), `SECRET_KEY`, `BASE_URL`, `OPENAI_API_KEY`, `GOOGLE_AI_API_KEY`.

7. **Deploy.** After the first successful deploy, note your service URL (e.g. `https://frontdesk-bot-api.onrender.com`).

8. **Set the Telegram webhook** (replace with your URL and `business_id`):
   ```bash
   curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=https://YOUR-RENDER-URL.onrender.com/webhook/telegram/YOUR_BUSINESS_UUID"
   ```

**Note:** On the free tier, the service may spin down after inactivity; the first request after idle can be slow. Use a paid plan for always-on or add an uptime ping.

## Docs

- **[docs/TELEGRAM_SETUP.md](docs/TELEGRAM_SETUP.md)** — Telegram bot token, webhook URL, setWebhook, and multi-tenant setup.
- **[MIGRATIONS.md](MIGRATIONS.md)** — How to run and create migrations, Neon setup.
- **[BUILD_LOG.md](BUILD_LOG.md)** — Changelog of implementation.
- **claude.md** — Full spec, schema, and quick commands.

## License

Private / unlicensed unless otherwise stated.
