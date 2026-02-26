# Front Desk Dashboard

Next.js dashboard for business owners to configure and monitor their front desk bot.

## Setup

```bash
cd dashboard
npm install
cp .env.local.example .env.local
```

Set `NEXT_PUBLIC_API_URL` in `.env.local` to your backend (e.g. `http://localhost:8000`).

## Run

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000). The API (FastAPI) must be running for the dashboard to load data.

## Build

```bash
npm run build
npm start
```

## Features

- **Businesses** — List, create, view. Copy business ID for webhook and API use.
- **Overview** — Business ID, upcoming bookings count, services and FAQs count, details.
- **Bookings** — Table of reservations (reference, date, time, party size, status).
- **FAQs** — Add, list, delete; import from CSV or TXT (Q:/A: format).
- **Services** — Add table types, room types, or bookable options (name, duration, price, capacity).
- **Settings** — Edit business name, working hours, timezone, location, phone, Telegram group ID.

All data is read and written via the FastAPI backend; no direct database access.
