"""Telegram entrypoint orchestration.

Resolves business + customer, loads conversation, builds system prompt, calls AI, saves history, dispatches actions.
"""
from __future__ import annotations

from typing import Any, Dict
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from telegram import Bot

from app.bot.handlers import appointments, booking, support
from app.bot.handlers.message_handler import handle_incoming_message
from app.channels.telegram import TelegramChannel
from app.core.config import settings
from app.models.db.conversation import MessageRoleEnum
from app.services.ai_service import AIAction
from app.services.business_service import get_business_by_id
from app.services.conversation_service import (
    add_message,
    get_recent_messages,
    trim_to_limit,
)
from app.services.customer_service import get_or_create_customer_by_telegram
from app.services.support_service import get_active_support_session
from app.utils.prompt_builder import (
    booking_context_from_state,
    build_system_prompt,
    format_faqs_for_prompt,
    format_services_for_prompt,
    format_staff_for_prompt,
)


def _uuid_from_data(data: Dict[str, Any], key: str) -> UUID:
    """Parse UUID from action payload; return nil UUID if missing/invalid."""
    val = data.get(key)
    if val is None:
        return UUID(int=0)
    if isinstance(val, UUID):
        return val
    try:
        return UUID(str(val))
    except (ValueError, TypeError):
        return UUID(int=0)


async def handle_telegram_callback(
    update: Dict[str, Any],
    session: AsyncSession,
    business_id: UUID,
) -> None:
    """Handle inline button callbacks: slot selection, confirm_booking, cancel_booking."""
    from sqlalchemy import select
    from app.models.db import Customer, Service

    cq = update.get("callback_query") or {}
    callback_id = cq.get("id")
    data = (cq.get("data") or "").strip()
    from_user = cq.get("from") or {}
    telegram_id = str(from_user.get("id", ""))
    msg = cq.get("message") or {}
    chat_id = msg.get("chat", {}).get("id")
    if not chat_id or not telegram_id:
        return

    business = await get_business_by_id(session, business_id)
    if not business:
        return

    token = business.telegram_bot_token or settings.TELEGRAM_BOT_TOKEN
    bot = Bot(token=token)
    channel = TelegramChannel(bot=bot)
    recipient_id = str(chat_id)
    try:
        await bot.answer_callback_query(callback_id)
    except Exception:
        pass

    # business already loaded above
    customer = await get_or_create_customer_by_telegram(session, telegram_id, None)
    state = dict(customer.conversation_state or {})
    pending = state.get("pending_booking") or {}

    if data == "cancel_booking":
        state["pending_booking"] = {}
        customer.conversation_state = state
        await channel.send_message(recipient_id, "Booking cancelled. Start over whenever you like.")
        return

    if data == "confirm_booking":
        if not pending.get("service_id") or not pending.get("time"):
            await channel.send_message(recipient_id, "No booking to confirm. Please pick a time first.")
            return
        service_id = pending.get("service_id")
        booking_date = pending.get("booking_date") or ""
        booking_time = pending.get("time", "")
        party_size = pending.get("party_size")
        special_requests = pending.get("special_requests")
        if isinstance(service_id, UUID):
            service_id = str(service_id)
        await booking.on_booking_confirmed(
            session,
            channel,
            recipient_id,
            business.id,
            customer.id,
            {
                "service_id": service_id,
                "booking_date": booking_date,
                "booking_time": booking_time,
                "party_size": party_size,
                "special_requests": special_requests,
            },
        )
        state["pending_booking"] = {}
        customer.conversation_state = state
        return

    if data.startswith("manage_cancel_"):
        try:
            bid = UUID(data.replace("manage_cancel_", "").strip())
        except (ValueError, AttributeError):
            await channel.send_message(recipient_id, "Invalid booking.")
            return
        from app.services.booking_service import cancel_booking
        cancelled = await cancel_booking(session, bid)
        if cancelled:
            await channel.send_message(recipient_id, "Your booking has been cancelled.")
        else:
            await channel.send_message(recipient_id, "Booking not found or could not be cancelled.")
        return

    if data.startswith("manage_reschedule_"):
        await channel.send_message(
            recipient_id,
            "Reply with the date you'd like (e.g. tomorrow or a specific date) and we'll show available times.",
        )
        return

    if data.startswith("manage_booking_"):
        try:
            bid = UUID(data.replace("manage_booking_", "").strip())
        except (ValueError, AttributeError):
            await channel.send_message(recipient_id, "Invalid booking.")
            return
        await appointments.show_manage_options(channel, recipient_id, bid, session=session)
        return

    # Assume data is a slot time (e.g. "19:00:00" or "19:00")
    if not pending.get("service_id") or not pending.get("booking_date"):
        await channel.send_message(recipient_id, "Please pick a time from the list above.")
        return
    pending["time"] = data
    state["pending_booking"] = pending
    customer.conversation_state = state

    service_id_val = pending.get("service_id")
    if isinstance(service_id_val, str):
        try:
            service_id_uuid = UUID(service_id_val)
        except ValueError:
            await channel.send_message(recipient_id, "Invalid selection. Please start again.")
            return
    else:
        service_id_uuid = service_id_val
    service_result = await session.execute(
        select(Service).where(Service.id == service_id_uuid, Service.business_id == business.id).limit(1)
    )
    service = service_result.scalars().first()
    service_name = service.name if service else "Service"
    price_str = f"{service.price}" if service and getattr(service, "price", None) is not None else "Pay at venue"
    await booking.show_confirmation(
        channel,
        recipient_id,
        business.name,
        service_name,
        party_size=pending.get("party_size"),
        formatted_date=pending.get("booking_date", ""),
        time_str=data,
        price_str=price_str,
        requests_str=pending.get("special_requests") or "None",
    )


async def handle_telegram_update(
    update: Dict[str, Any],
    session: AsyncSession,
    business_id: UUID,
) -> None:
    """Process a Telegram Update end-to-end: message or callback_query."""

    if update.get("callback_query"):
        await handle_telegram_callback(update, session, business_id)
        return

    message = update.get("message") or update.get("edited_message") or {}
    chat = message.get("chat") or {}
    chat_id = chat.get("id")
    text = message.get("text") or ""

    if chat_id is None or not text:
        return

    business = await get_business_by_id(session, business_id)
    if not business:
        bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        channel = TelegramChannel(bot=bot)
        await channel.send_message(str(chat_id), "No business configured yet. Please try again later.")
        return

    token = business.telegram_bot_token or settings.TELEGRAM_BOT_TOKEN
    bot = Bot(token=token)
    channel = TelegramChannel(bot=bot)
    recipient_id = str(chat_id)
    telegram_id = str(chat_id)
    from_user = message.get("from") or {}
    full_name = from_user.get("first_name") or from_user.get("last_name") or None

    customer = await get_or_create_customer_by_telegram(session, telegram_id, full_name)
    business_id = business.id
    customer_id = customer.id

    active_session = await get_active_support_session(session, customer_id, business_id)
    if active_session and business.telegram_group_id:
        await channel.forward_to_group(
            business.telegram_group_id,
            f"Customer ({customer.full_name or 'Guest'}): {text}",
        )
        return

    history = await get_recent_messages(session, customer_id, business_id)
    messages = history + [{"role": "user", "content": text}]

    system_prompt = build_system_prompt(
        business_name=business.name,
        business_type=business.type.value,
        working_hours=business.working_hours,
        location=business.location,
        phone=business.phone,
        services_text=format_services_for_prompt(business.services),
        staff_text=format_staff_for_prompt(business.staff),
        faq_text=format_faqs_for_prompt(business.faqs),
        booking_context=booking_context_from_state(customer.conversation_state),
    )

    result = await handle_incoming_message(
        channel=channel,
        recipient_id=recipient_id,
        business_id=business_id,
        customer_id=customer_id,
        text=text,
        system_prompt=system_prompt,
        messages=messages,
    )

    if result:
        if result.reply_text:
            await channel.send_message(recipient_id, result.reply_text)

        await add_message(session, customer_id, business_id, MessageRoleEnum.user, text)
        await add_message(session, customer_id, business_id, MessageRoleEnum.assistant, result.reply_text or "")
        await trim_to_limit(session, customer_id, business_id)

        data = result.data or {}
        group_id = business.telegram_group_id or "0"
        customer_name = customer.full_name or "Customer"

        if result.action == AIAction.SHOW_SLOTS:
            party_size = data.get("party_size")
            if party_size is not None and not isinstance(party_size, int):
                try:
                    party_size = int(party_size)
                except (ValueError, TypeError):
                    party_size = None
            service_id = _uuid_from_data(data, "service_id")
            if (not service_id or service_id.int == 0) and business.services:
                service_id = business.services[0].id
            booking_date = data.get("date") or data.get("booking_date") or ""
            if service_id and service_id.int:
                customer.conversation_state = {
                    **(customer.conversation_state or {}),
                    "pending_booking": {
                        "service_id": str(service_id),
                        "booking_date": booking_date,
                        "party_size": party_size,
                    },
                }
            await booking.show_available_slots(
                channel,
                recipient_id,
                business_id,
                service_id,
                booking_date,
                party_size,
                session=session,
            )
        elif result.action == AIAction.SHOW_BOOKINGS:
            await appointments.show_bookings(
                channel, recipient_id, customer_id, business_id, session=session
            )
        elif result.action == AIAction.MANAGE_BOOKING:
            await appointments.show_manage_options(
                channel, recipient_id, _uuid_from_data(data, "booking_id"), session=session
            )
        elif result.action == AIAction.HUMAN_HANDOFF:
            await support.initiate_handoff(
                channel,
                recipient_id,
                group_id=group_id,
                customer_id=customer_id,
                customer_name=customer_name,
                last_message=text,
            )
        elif result.action == AIAction.CONFIRM_BOOKING:
            pass

