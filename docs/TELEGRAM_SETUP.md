# Telegram configuration

How to configure the Telegram bot and webhook for the Front Desk app.

---

## Overview

- Each **business** has an optional **Telegram bot token** (or the app uses a global token from env).
- Updates are received via **webhook**: Telegram POSTs to your server; the path includes the **business ID**.
- You need: a bot token, a public URL for the app, a business in the DB, and one `setWebhook` call.

---

## 1. Create a bot and get the token

1. Open [@BotFather](https://t.me/BotFather) in Telegram.
2. Send `/newbot` and follow the prompts (name, username).
3. Copy the **token** BotFather returns (e.g. `123456789:ABCdefGHI...`).
4. **Keep it secret.** Use it only in environment variables and in the `setWebhook` URL; do not commit it.

---

## 2. Environment variables

Set these where the app runs (e.g. Render Dashboard → Environment, or local `backend/.env`).

| Variable | Required | Description |
|----------|----------|-------------|
| **TELEGRAM_BOT_TOKEN** | Yes (if business has no token) | Default bot token. Used when a business has no `telegram_bot_token` set. |
| **TELEGRAM_WEBHOOK_URL** | No | Base URL of your app (e.g. `https://your-app.onrender.com`). Optional; used if you build webhook URLs in code. |

**Per-business token (optional):** You can store a different token per business in the DB (`business.telegram_bot_token`). If set, that token is used for that business’s webhook instead of `TELEGRAM_BOT_TOKEN`.

---

## 3. Webhook URL format

The app expects Telegram to send updates to:

```
https://<YOUR_APP_BASE_URL>/webhook/telegram/<BUSINESS_ID>
```

- **&lt;YOUR_APP_BASE_URL&gt;** — Public URL of your deployment (e.g. `https://whatsapp-frontdesk-recep.onrender.com`).
- **&lt;BUSINESS_ID&gt;** — UUID of the business in your database (e.g. `fb4cae60-1df1-4643-aaf0-98a6262646f0`).

**Example:**  
`https://whatsapp-frontdesk-recep.onrender.com/webhook/telegram/fb4cae60-1df1-4643-aaf0-98a6262646f0`

---

## 4. Create a business (if needed)

You need at least one business with a known ID:

- **API:** `POST /api/businesses` with name, type (`restaurant` or `hostel`), working_hours, etc. The response includes `id` — that is your **business ID**.
- **API docs:** Open `https://<YOUR_APP_BASE_URL>/docs` and use **POST /api/businesses** with a valid body (see README for example JSON).

---

## 5. Register the webhook with Telegram

Tell Telegram to send updates to your URL. Run in a terminal (replace placeholders):

```bash
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=https://<YOUR_APP_BASE_URL>/webhook/telegram/<BUSINESS_ID>"
```

- **&lt;YOUR_BOT_TOKEN&gt;** — The token from BotFather (no angle brackets, no spaces).
- **&lt;YOUR_APP_BASE_URL&gt;** — Your app’s public host (no trailing slash).
- **&lt;BUSINESS_ID&gt;** — The business UUID from step 4.

**Example:**
```bash
curl "https://api.telegram.org/bot123456789:ABCdef/setWebhook?url=https://whatsapp-frontdesk-recep.onrender.com/webhook/telegram/fb4cae60-1df1-4643-aaf0-98a6262646f0"
```

**Success response:**  
`{"ok":true,"result":true,"description":"Webhook was set"}`

**Common errors:**
- **404 Not Found** — Bot token is wrong or revoked. Get a fresh token from @BotFather (or revoke and regenerate).
- **Bad Request** — Check that the URL is exactly right (HTTPS, no typos, correct business ID).

---

## 6. Verify

1. Open your bot in Telegram (search by bot username).
2. Send a message (e.g. “Hi” or “I want to book”).
3. The app receives the POST at `/webhook/telegram/<business_id>`, processes the update, and can reply.
4. On Render free tier, the first request after idle may be slow (cold start).

---

## 7. Multiple businesses (multi-tenant)

- Each business can have its own webhook URL: same base URL, different **business_id** in the path.
- Create each business via the API, get its `id`, then call `setWebhook` with that ID.
- If a business has **telegram_bot_token** set in the DB, the app uses that token for sending replies; otherwise it uses **TELEGRAM_BOT_TOKEN** from the environment.

---

## 8. Changing or removing the webhook

- **Set a new URL:** Call `setWebhook` again with the new URL (e.g. after moving to a new domain).
- **Remove webhook (e.g. switch to polling):**
  ```bash
  curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/deleteWebhook"
  ```
- **See current webhook:**
  ```bash
  curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo"
  ```

---

## Summary checklist

- [ ] Bot created in @BotFather; token copied.
- [ ] `TELEGRAM_BOT_TOKEN` set in Render (or in `.env` for local).
- [ ] App deployed and reachable at `https://<your-app>.onrender.com`.
- [ ] Business created via API; business **id** (UUID) noted.
- [ ] `setWebhook` called with `url=https://<your-app>/webhook/telegram/<business_id>`.
- [ ] Message sent to bot; reply received (after cold start if on free tier).
