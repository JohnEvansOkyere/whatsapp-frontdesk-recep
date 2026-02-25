# Build log — WhatsApp/Telegram Front Desk

Document every change and addition. Update this file whenever code or structure is added or modified.

---

## 2025-02-25

### Added

- **BUILD_LOG.md** — This file. All further work is logged here.

- **app/channels/**
  - `base.py` — Abstract `BaseChannel`: `send_message`, `send_buttons`, `send_list`, `send_typing`, `forward_to_group`.
  - `telegram.py` — `TelegramChannel(BaseChannel)`; methods raise NotImplementedError (wire via bot context).
  - `whatsapp.py` — `WhatsAppChannel(BaseChannel)`; takes `phone_number_id`, `access_token`; methods stubbed for Meta API.

- **app/utils/**
  - `message_templates.py` — All user-facing strings: `confirmation_body`, `new_booking_notification`, `support_request_notification`, `support_connected_to_customer`, `support_resolved_to_customer`, `reminder_24h`, `reminder_1h`, `connecting_support`.
  - `datetime_utils.py` — Stubs: `weekday_key`, `parse_date_from_user`, `generate_slots_for_day`, `slot_taken`.

- **app/api/**
  - `dependencies.py` — Re-exports `get_db` from `app.core.database`.
  - `routes/webhooks.py` — POST /webhook/telegram (calls `handle_telegram_update`), GET/POST /webhook/whatsapp (stubs).
  - `routes/appointments.py` — GET/POST /api/bookings, PATCH/DELETE /api/bookings/{id}.
  - `routes/businesses.py` — GET/POST /api/businesses, PATCH /api/businesses/{id}, GET /api/businesses/{id}/slots.
  - `routes/onboarding.py` — GET /api/businesses/{id}/connect-calendar, GET /api/auth/google/callback.
  - `routes/faqs.py` — POST/GET /api/businesses/{id}/faqs, DELETE /api/faqs/{id}.

- **app/main.py** — FastAPI app with lifespan (init_db, scheduler start/stop); includes webhooks, appointments, businesses, onboarding, faqs routers; GET /health.

- **app/models/schemas/**
  - `booking.py` — BookingCreate, BookingUpdate, BookingResponse.
  - `business.py` — BusinessCreate, BusinessUpdate, BusinessResponse.
  - `customer.py` — CustomerCreate, CustomerResponse.

- **app/bot/**
  - `states.py` — Constants: BOOKING_STATE_*.
  - `keyboards.py` — `slot_buttons`, `confirm_booking_buttons` (channel-agnostic).
  - `handlers/message_handler.py` — `handle_incoming_message` (calls ai_service.process_message, returns AIResult).
  - `handlers/booking.py` — `show_available_slots`, `show_confirmation`, `on_booking_confirmed` (stubs / partial).
  - `handlers/appointments.py` — `show_bookings`, `show_manage_options` (stubs).
  - `handlers/faq.py` — `reply_faq`.
  - `handlers/support.py` — `initiate_handoff` (sends to group + customer).
  - `bot.py` — Entry for `python -m app.bot.bot`; main() placeholder.
  - `telegram_entry.py` — `handle_telegram_update`: parses message, calls AI, sends reply; **dispatches on AIResult.action** to booking.show_available_slots, appointments.show_bookings/show_manage_options, support.initiate_handoff (CONFIRM_BOOKING left as pass). Helper `_uuid_from_data` for action payloads.

- **app/services/**
  - `booking_service.py` — `get_available_slots`, `create_booking`, `cancel_booking` (stubs).
  - `calendar_service.py` — `create_event` (stub).
  - `reminder_service.py` — `schedule_reminders`, `cancel_reminders` (cancel_reminders implemented).
  - `faq_service.py` — `get_faqs_for_business` (stub).

- **app/services/ai_service.py** — Multi-provider (OpenAI, Groq, Gemini), `process_message`, `AIAction`, `AIResult`; GroqProvider via httpx; **ACTION parsing**: `_parse_action_and_data` detects ACTION: SHOW_SLOTS, SHOW_BOOKINGS, MANAGE_BOOKING, HUMAN_HANDOFF, CONFIRM_BOOKING and optional payload `{...}` or key=val; reply_text returned is conversational part only (ACTION lines stripped).

- **.env.example** — All env vars from CLAUDE; AI_PROVIDER=groq, AI_MODEL=llama-3.1-8b-instant.

- **app/core/config.py** — Defaults set to AI_PROVIDER=groq, AI_MODEL=llama-3.1-8b-instant.

### Added (this session)

- **app/services/customer_service.py** — `get_or_create_customer_by_telegram(session, telegram_id, full_name)`.
- **app/services/business_service.py** — `get_first_active_business(session)`, `get_business_by_id(session, business_id)` with services/faqs/staff loaded.
- **app/services/conversation_service.py** — `get_recent_messages`, `add_message`, `trim_to_limit` (20 per customer/business).
- **app/services/support_service.py** — `get_active_support_session(session, customer_id, business_id)`.
- **app/utils/prompt_builder.py** — `build_system_prompt`, `format_services_for_prompt`, `format_staff_for_prompt`, `format_faqs_for_prompt`, `booking_context_from_state`.
- **app/bot/telegram_entry.py** — Full flow: resolve business (first active) + get/create customer; check active support session (forward to group and return); load last 20 messages; build CLAUDE system prompt; call AI; save user + assistant message and trim; dispatch actions with real business_id/customer_id and business.telegram_group_id/customer.full_name.
- **app/utils/datetime_utils.py** — `generate_slots_for_day`, `slot_taken`, `parse_date_from_user` implemented.
- **app/services/booking_service.py** — `get_available_slots` implemented (working_hours, slot generation, filter by existing confirmed bookings).
- **app/bot/handlers/booking.py** — `show_available_slots` calls `get_available_slots`, sends slot buttons via channel; accepts `session` and passes to service.
- **app/bot/keyboards.py** — Slot buttons set `action` to time string for callback_data.

### Added (booking completion)

- **booking_service.create_booking** — Race check, RST-/HST- reference, insert Booking (status=confirmed). **update_booking_reminder_jobs**, **cancel_booking** (cancel reminders, set status=cancelled).
- **reminder_service.schedule_reminders** — 24h and 1h before booking via AsyncIOScheduler; async jobs send Telegram reminder messages. **cancel_reminders** unchanged.
- **booking handler on_booking_confirmed** — Calls create_booking, schedule_reminders, update_booking_reminder_jobs, new_booking_notification to group, confirmation message to customer.
- **telegram_entry handle_telegram_callback** — Handles callback_query: slot time → save time to pending_booking, show_confirmation; confirm_booking → on_booking_confirmed, clear pending; cancel_booking → clear pending. **handle_telegram_update** routes callback_query to handle_telegram_callback; on SHOW_SLOTS saves pending_booking (service_id, booking_date, party_size) to customer.conversation_state before show_available_slots.

### Alembic migrations

- **alembic.ini** — Configured to defer `sqlalchemy.url` to `migrations/env.py` and `app.core.config.settings`.
- **migrations/env.py** — Uses `Settings.NEON_DATABASE_URL` (fallback `sqlite:///./alembic.db`) and `Base.metadata` for autogenerate; `compare_type=True`.
- **migrations/versions/8f69d917878c_initial_schema.py** — Initial schema for businesses, customers, services, staff, bookings, faqs, conversation_history, support_sessions (including `telegram_bot_token`). Fixed for PostgreSQL: `sa.Text()`/`sa.String()` in JSON/ARRAY, `server_default=sa.text('now()')`.
- **Neon setup**: Create a project and DB in [Neon](https://neon.tech), copy the connection string into `.env` as `NEON_DATABASE_URL`, then run `alembic upgrade head` to apply migrations.

### Pending (to implement)

- Implement OpenAI/Gemini HTTP calls in ai_service providers.
- Wire WhatsApp webhook body → message_handler.
- Implement calendar_service OAuth and create_event.
- Tests: test_booking, test_ai_service, test_channels.
- Procfile, README content.

---

*Last updated: 2025-02-25*
