# WhatsApp/Telegram Restaurant & Hostel Front Desk Booking System
> Master reference file for all AI coding assistants.
> Read this fully before writing any code or making any changes.

---

## Quick Commands
- Run server: `uvicorn app.main:app --reload`
- Run migrations: `alembic upgrade head`
- Create migration: `alembic revision --autogenerate -m "description"`
- Install deps: `pip install -r requirements.txt`
- Run tests: `pytest`
- Run bot (polling mode for dev): `python -m app.bot.bot`

---

## Project Overview
A multi-tenant AI-powered front desk bot for restaurants and hostels.
Businesses get a WhatsApp or Telegram bot that:
- Handles table/room reservations naturally via AI conversation
- Answers FAQs 24/7 (hours, location, menu, pricing, policies)
- Manages bookings (view, reschedule, cancel)
- Sends automated reminders before appointments
- Escalates to human staff when needed
- Syncs bookings to Google Calendar

Built on Telegram for development and testing.
WhatsApp (Meta Cloud API) for production clients.
Same codebase, different channel layer.

---

## Stack
- Python 3.11+
- FastAPI
- python-telegram-bot v20+ (async only)
- SQLAlchemy async + Neon PostgreSQL
- **AI: Multi-provider** — OpenAI, Groq, Google Gemini (any available model per provider)
- APScheduler for reminders
- Google Calendar API for booking sync
- Meta Cloud API (WhatsApp) for production
- Alembic for DB migrations
- pydantic-settings for config
- httpx for all HTTP calls (never use requests)

---

## Project Structure
```
project/
├── app/
│   ├── main.py                  # FastAPI app entry point + webhook registration
│   ├── channels/
│   │   ├── base.py              # Abstract channel interface
│   │   ├── telegram.py          # Telegram implementation
│   │   └── whatsapp.py          # WhatsApp implementation (Meta Cloud API)
│   ├── bot/
│   │   ├── handlers/
│   │   │   ├── message_handler.py   # All incoming messages enter here
│   │   │   ├── booking.py           # Booking flow & slot display
│   │   │   ├── appointments.py      # View/reschedule/cancel
│   │   │   ├── faq.py               # FAQ handler
│   │   │   └── support.py           # Human handoff
│   │   ├── keyboards.py             # Buttons and inline keyboards
│   │   ├── states.py                # Conversation state constants
│   │   └── bot.py                   # Bot initialization
│   ├── api/
│   │   ├── routes/
│   │   │   ├── webhooks.py          # Telegram + WhatsApp webhook endpoints
│   │   │   ├── appointments.py      # Appointment CRUD endpoints
│   │   │   ├── businesses.py        # Business management endpoints
│   │   │   └── onboarding.py        # Google Calendar OAuth endpoints
│   │   └── dependencies.py          # DB session, auth dependencies
│   ├── services/
│   │   ├── ai_service.py            # OpenAI integration + intent detection
│   │   ├── booking_service.py       # Booking business logic
│   │   ├── calendar_service.py      # Google Calendar integration
│   │   ├── reminder_service.py      # APScheduler reminder scheduling
│   │   └── faq_service.py           # FAQ retrieval and matching
│   ├── models/
│   │   ├── db/
│   │   │   ├── business.py          # Business (restaurant/hostel) model
│   │   │   ├── customer.py          # Customer model
│   │   │   ├── booking.py           # Booking model
│   │   │   ├── service.py           # Service/room type model
│   │   │   ├── staff.py             # Staff/doctor model
│   │   │   ├── faq.py               # FAQ model
│   │   │   ├── support_session.py   # Support session model
│   │   │   └── conversation.py      # Conversation history model
│   │   └── schemas/
│   │       ├── booking.py
│   │       ├── business.py
│   │       └── customer.py
│   ├── core/
│   │   ├── config.py                # All settings via pydantic-settings
│   │   ├── database.py              # Neon async DB connection + session
│   │   └── scheduler.py             # APScheduler instance
│   └── utils/
│       ├── datetime_utils.py        # Slot generation, date parsing
│       └── message_templates.py     # All message strings in one place
├── migrations/                      # Alembic migration files
├── tests/
│   ├── test_booking.py
│   ├── test_ai_service.py
│   └── test_channels.py
├── CLAUDE.md
├── ARCHITECTURE.md
├── TODO.md
├── .env.example
├── requirements.txt
├── Procfile
└── README.md
```

---

## Database Schema

### businesses
```
id                    UUID PK
name                  str
type                  enum: restaurant, hostel
telegram_group_id     str          -- for staff notifications
google_calendar_id    str nullable
google_credentials    JSON nullable -- encrypted OAuth tokens
working_hours         JSON         -- {"mon": ["09:00", "21:00"], "tue": [...]}
slot_duration_minutes int default 30
timezone              str default "Africa/Accra"
location              str nullable
phone                 str nullable
active_channel        enum: telegram, whatsapp  default telegram
whatsapp_config       JSON         -- {phone_number_id, access_token, verify_token, is_active}
is_active             bool default true
created_at            timestamp
```

### services
```
id                    UUID PK
business_id           FK -> businesses
name                  str          -- "Table for 2", "Deluxe Room", "General Checkup"
description           str nullable
duration_minutes      int
price                 decimal nullable
capacity              int nullable -- for tables: how many people
is_active             bool default true
```

### staff
```
id                    UUID PK
business_id           FK -> businesses
name                  str
role                  str nullable -- "Waiter", "Receptionist", "Doctor"
telegram_id           str nullable -- so they can use /reply and /resolve
is_active             bool default true
```

### customers
```
id                    UUID PK
telegram_id           str nullable unique
whatsapp_number       str nullable unique
full_name             str nullable
phone_number          str nullable
conversation_state    JSON         -- current booking progress
created_at            timestamp
```

### bookings
```
id                    UUID PK
business_id           FK -> businesses
customer_id           FK -> customers
service_id            FK -> services
staff_id              FK -> staff nullable
booking_date          date
booking_time          time
party_size            int nullable  -- for restaurants
status                enum: pending, confirmed, cancelled, completed
google_event_id       str nullable
booking_reference     str unique   -- format: RST-YYYYMMDD-XXXX or HST-YYYYMMDD-XXXX
special_requests      str nullable
reminder_24h_job_id   str nullable -- APScheduler job id
reminder_1h_job_id    str nullable -- APScheduler job id
created_at            timestamp
```

### faqs
```
id                    UUID PK
business_id           FK -> businesses
question              str
answer                str
keywords              array of str
```

### conversation_history
```
id                    UUID PK
customer_id           FK -> customers
business_id           FK -> businesses
role                  enum: user, assistant
content               str
created_at            timestamp
-- Keep last 20 messages per customer per business
```

### support_sessions
```
id                    UUID PK
customer_id           FK -> customers
business_id           FK -> businesses
is_active             bool default true
started_at            timestamp
resolved_at           timestamp nullable
```

---

## Channel Architecture (CRITICAL - READ THIS)

All messaging must go through the abstract channel interface.
Never call Telegram or WhatsApp APIs directly from handlers or services.

### base.py interface must implement:
```python
async def send_message(recipient_id: str, text: str)
async def send_buttons(recipient_id: str, text: str, buttons: list[dict])
async def send_list(recipient_id: str, text: str, items: list[dict])
async def send_typing(recipient_id: str)
async def forward_to_group(group_id: str, text: str)
```

### Channel selection:
- Set per business in businesses.active_channel
- telegram.py — used for all development and testing
- whatsapp.py — activated per client when they provide Meta credentials
- Channel is instantiated in message_handler.py based on incoming webhook source

### WhatsApp config per business (stored in businesses.whatsapp_config):
```json
{
  "phone_number_id": "",
  "access_token": "",
  "verify_token": "",
  "is_active": false
}
```

When client onboards:
1. Client creates Meta Business Account
2. Client verifies their WhatsApp Business number
3. Client provides phone_number_id and access_token
4. Update their whatsapp_config in DB, set is_active: true
5. Set active_channel to whatsapp
6. Zero code changes needed

---

## AI Service — Multi-Provider Support

The AI service supports **multiple providers** so any available model can be used. Configure via settings; the same interface is used regardless of provider.

### Supported providers and models (examples — use any model the provider offers)
- **OpenAI**: `gpt-4o`, `gpt-4o-mini`, `gpt-4-turbo`, etc. — set `OPENAI_API_KEY`
- **Groq**: `llama-3.1-70b-versatile`, `llama-3.1-8b-instant`, `mixtral-8x7b-32768`, etc. — set `GROQ_API_KEY`
- **Google Gemini**: `gemini-1.5-pro`, `gemini-1.5-flash`, `gemini-2.0-flash`, etc. — set `GOOGLE_AI_API_KEY` (or `GEMINI_API_KEY`)

### Configuration (core/config.py)
- `AI_PROVIDER`: `openai` | `groq` | `gemini` (default: `openai`)
- `AI_MODEL`: model name for the chosen provider (e.g. `gpt-4o-mini`, `llama-3.1-8b-instant`, `gemini-1.5-flash`)
- Provider-specific API keys from env (see Environment Variables)

### Implementation (services/ai_service.py)
- Single entry point: `process_message(...)` — same for all providers
- Internal provider adapters: call the correct API (OpenAI, Groq, or Gemini) based on `AI_PROVIDER`
- Same request/response shape: messages in, text + optional ACTION tags out
- If the configured provider or model is unavailable, log and fall back to another provider/model if configured, or return a graceful error

### Rules
- Never hardcode a single provider; always use the configured provider and model
- Any model string supported by the selected provider is valid for `AI_MODEL`
- Keep provider-specific code behind adapters so adding new providers is straightforward

---

## AI Service Architecture

Every incoming message passes through ai_service.py first.

### Dynamic system prompt built per business:
```
You are a friendly AI assistant for {business_name}, a {business_type}.
You help customers make reservations, answer questions, and connect with staff.

BUSINESS INFORMATION:
- Working hours: {working_hours}
- Location: {location}
- Phone: {phone}
- Services/Options: {list_of_services_with_prices}
- Staff: {list_of_staff}

FAQ KNOWLEDGE BASE:
{all_faqs_as_qa_pairs}

YOUR BEHAVIOR:
- Be warm, friendly, and concise
- Respond in the same language the customer writes in
- Never make up information not in the above data
- If unsure, offer to connect with staff
- When customer wants to book: collect service, date, time, party size naturally
- When you have enough info to show available slots respond with ACTION: SHOW_SLOTS
- When customer wants to see their bookings respond with ACTION: SHOW_BOOKINGS
- When customer wants to cancel or reschedule respond with ACTION: MANAGE_BOOKING
- When customer needs human support respond with ACTION: HUMAN_HANDOFF
- For everything else reply conversationally

CURRENT BOOKING CONTEXT:
{booking_context}
```

### Actions AI can return:
```
ACTION: SHOW_SLOTS {service_id, date, party_size}
ACTION: SHOW_BOOKINGS
ACTION: MANAGE_BOOKING {booking_id}
ACTION: HUMAN_HANDOFF
ACTION: CONFIRM_BOOKING {service_id, staff_id, date, time, party_size}
```

### Flow:
1. Load last 20 messages from conversation_history
2. Build system prompt with live business data from DB
3. Send to configured AI provider (OpenAI, Groq, or Gemini) using configured model
4. Parse response for ACTION tags
5. Return (ai_reply, action, extracted_data)
6. Save both messages to conversation_history
7. Trim history to 20 messages after saving

---

## Message Handler Flow
```
Incoming message
      ↓
Get or create customer
      ↓
Active support session? → YES → Forward to business Telegram group
      ↓ NO
Pass to ai_service.process_message()
      ↓
Parse action from AI response
      ↓
No action       → send AI reply as text
SHOW_SLOTS      → booking.show_available_slots()
SHOW_BOOKINGS   → appointments.show_bookings()
MANAGE_BOOKING  → appointments.show_manage_options()
HUMAN_HANDOFF   → support.initiate_handoff()
CONFIRM_BOOKING → booking.show_confirmation()
```

---

## Booking Flow

### show_available_slots(customer, service_id, date, party_size):
1. Get business working hours for that day
2. Generate all possible slots based on slot_duration_minutes
3. Query bookings table for already booked slots on that date
4. Filter out unavailable slots
5. Display as buttons — max 8 per page with pagination:
   [9:00 AM] [9:30 AM] [10:00 AM]
   [2:00 PM] [3:00 PM] [4:30 PM]
   [📅 Different date] [⬅ More slots]

### show_confirmation(customer, booking_data):
```
Please confirm your booking ✅

🏢 {business_name}
🍽️ {service_name}
👥 Party size: {party_size}        ← restaurants only
📅 Date: {formatted_date}
⏰ Time: {time}
💰 Price: {price or "Pay at venue"}
📝 Special requests: {requests or "None"}

[✅ Confirm Booking] [❌ Cancel]
```

### on_booking_confirmed:
1. Re-check slot is still available (race condition protection)
2. If slot taken: apologize, show fresh slots
3. If new customer: ask name and phone before confirming
4. Save booking to DB with status=confirmed
5. Generate reference: RST-YYYYMMDD-XXXX (restaurant) or HST-YYYYMMDD-XXXX (hostel)
6. Create Google Calendar event
7. Notify business Telegram group:
```
   📅 New Booking!
   Customer: {name} ({phone})
   Service: {service}
   Date: {date} at {time}
   Party: {size}
   Ref: {reference}
   Special requests: {requests or none}
```
8. Send confirmation to customer
9. Schedule reminders via APScheduler

---

## Conversation Examples

### Restaurant booking:
```
Customer: "hi"
Bot: "Hey! 👋 Welcome to Baobab Kitchen.
     How can I help you today?"

Customer: "I want to reserve a table for tonight"
Bot: "Perfect! How many people will be dining?"

Customer: "4 people, around 7pm"
Bot: "Great! Here are available slots for tonight 🍽️"
     [6:30 PM] [7:00 PM] [7:30 PM] [8:00 PM]

Customer: *clicks 7:00 PM*
Bot: Shows confirmation with [✅ Confirm] [❌ Cancel]
```

### Hostel booking:
```
Customer: "do you have rooms available this weekend?"
Bot: "Hi there! 👋 Let me check for you.
     What type of room are you looking for?"
     [🛏️ Dorm Bed] [🚪 Private Room] [👨‍👩‍👧 Family Room]

Customer: *clicks Private Room*
Bot: "How many nights, starting which date?"

Customer: "2 nights from Saturday"
Bot: Shows available slots/rooms as buttons
```

### FAQ:
```
Customer: "what time do you close?"
Bot: AI reads working_hours from DB and answers directly

Customer: "is parking available?"
Bot: AI checks FAQ knowledge base and answers

Customer: "do you have vegan options?"
Bot: AI answers from FAQ or says it will check with staff
```

### Support handoff:
```
Customer: "I need to speak to someone"
Bot: "Connecting you with our team now 💬
     Someone will be with you shortly!"
→ Notifies business Telegram group
→ All subsequent messages forwarded to group
```

---

## Support Handoff

### initiate_handoff(customer, business):
1. Create active support_session in DB
2. Notify business Telegram group:
```
   💬 Support Request!
   From: {customer_name}
   Last message: {last_message}
   Reply: /reply {customer_id} {your message}
   Close: /resolve {customer_id}
```
3. Tell customer: "You're connected! Our team will reply shortly 🙏"

### While session active:
- All customer messages forwarded to Telegram group automatically
- Staff replies with: /reply {customer_id} {message}
- Bot delivers reply to customer seamlessly
- Staff closes with: /resolve {customer_id}
- Customer gets: "Glad we could help! Is there anything else? 😊"

---

## Reminders

On booking confirmed schedule two APScheduler jobs:

24hr before:
```
⏰ Reminder: You have a reservation tomorrow!

🏢 {business_name}
📅 {date} at {time}
👥 Party of {size}
Ref: {reference}

Need to change anything? Just message us here!
```

1hr before:
```
⏰ Your reservation is in 1 hour at {business_name}.
See you soon! 🎉
```

On cancellation: delete both APScheduler jobs using stored job IDs.

---

## Google Calendar Integration

### create_event:
- Title: "{service} - {customer_name} (x{party_size})"
- Description: "Customer: {name}\nPhone: {phone}\nRef: {ref}\nBooked via AI Bot"
- Start: booking datetime
- End: start + service.duration_minutes
- Returns google_event_id saved to booking

### OAuth flow:
- Business connects once via GET /api/businesses/{id}/connect-calendar
- Store refresh token in businesses.google_credentials
- Auto-refresh on expiry

---

## FastAPI Endpoints
```
POST   /webhook/telegram                         Telegram webhook
POST   /webhook/whatsapp                         WhatsApp webhook (Meta)
GET    /webhook/whatsapp                         WhatsApp verification challenge

GET    /api/bookings                             List bookings (admin)
POST   /api/bookings                             Create booking
PATCH  /api/bookings/{id}                        Reschedule
DELETE /api/bookings/{id}                        Cancel

GET    /api/businesses                           List businesses
POST   /api/businesses                           Register new business
PATCH  /api/businesses/{id}                      Update business
GET    /api/businesses/{id}/slots?date=YYYY-MM-DD Available slots

GET    /api/businesses/{id}/connect-calendar     Start OAuth
GET    /api/auth/google/callback                 OAuth callback

POST   /api/businesses/{id}/faqs                 Add FAQ
GET    /api/businesses/{id}/faqs                 List FAQs
DELETE /api/faqs/{id}                            Delete FAQ
```

---

## Environment Variables (.env.example)
```
# App
SECRET_KEY=
ENVIRONMENT=development
BASE_URL=

# Telegram (testing)
TELEGRAM_BOT_TOKEN=
TELEGRAM_WEBHOOK_URL=

# WhatsApp (production - per client, stored in DB)
# These are defaults, actual credentials stored per business in DB
META_APP_ID=
META_APP_SECRET=

# Database
NEON_DATABASE_URL=

# AI — Multi-provider (set the one you use; AI_PROVIDER + AI_MODEL choose which is active)
AI_PROVIDER=openai
AI_MODEL=gpt-4o-mini
OPENAI_API_KEY=

GROQ_API_KEY=

GOOGLE_AI_API_KEY=
# or GEMINI_API_KEY=  (same key, either name supported)

# Google Calendar
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REDIRECT_URI=
```

---

## Coding Rules (NEVER BREAK THESE)

- All functions must be async
- Never use sync SQLAlchemy — always use async session
- Never call Telegram or WhatsApp APIs directly from handlers or services
- Always go through app/channels/base.py interface
- Never hardcode strings — all messages go in utils/message_templates.py
- Never hardcode credentials — always use settings from core/config.py
- Use UUID for all primary keys
- Use Pydantic schemas for all API request/response validation
- Service layer handles all business logic
- Handlers and routes only call services — no DB queries in handlers
- All DB models in app/models/db/
- All Pydantic schemas in app/models/schemas/
- Use httpx for all HTTP calls, never use requests library
- Use Python type hints everywhere
- Log errors with customer_id and business_id for context
- After editing a service, check the handler that calls it

---

## What NOT to Do

- Don't use Flask patterns — this is FastAPI
- Don't mix bot logic with API route logic
- Don't store WhatsApp credentials in .env — store per business in DB
- Don't use synchronous DB calls anywhere
- Don't put business logic in handlers
- Don't skip race condition check on final booking confirmation
- Don't use unofficial WhatsApp APIs (number ban risk)
- Don't use requests library — use httpx

---

## Multi-tenant Notes

- Every bot interaction is scoped to a business_id
- System prompt is built dynamically per business from DB
- Each business has its own WhatsApp credentials in DB
- One deployment serves all businesses
- Telegram used for testing any business
- WhatsApp activated per business when client is onboarded

---

## Testing Strategy

- Use Telegram bot for all development and testing
- Test all booking flows end to end in Telegram first
- WhatsApp channel should be a thin wrapper — if Telegram works, WhatsApp works
- Test race conditions: simulate two bookings for same slot simultaneously
- Test AI fallback: if the configured AI provider fails, bot should fall back gracefully to button menu (or optional secondary provider if configured)

---

## Deployment

- Host on Railway or Render
- Set Telegram webhook: POST https://api.telegram.org/bot{token}/setWebhook
- Set WhatsApp webhook in Meta Developer Console pointing to /webhook/whatsapp
- Neon DB handles connection pooling — no need for PgBouncer at MVP stage
- Use Render's cron or APScheduler for reminders

---

## Business Types Supported

### Restaurant
- Service = table size ("Table for 2", "Table for 4", "Private Dining")
- booking_reference prefix: RST-
- Extra fields: party_size, special_requests
- Typical slot duration: 90 minutes

### Hostel / Hotel
- Service = room type ("Dorm Bed", "Private Room", "Family Room")
- booking_reference prefix: HST-
- Extra fields: number of nights, check-in date, check-out date
- Typical slot duration: 1440 minutes (full day)