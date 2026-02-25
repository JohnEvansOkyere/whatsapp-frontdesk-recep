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
from app.services.business_service import get_first_active_business
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


async def handle_telegram_update(update: Dict[str, Any], session: AsyncSession) -> None:
    """Process a Telegram Update end-to-end.

    Responsibilities (per CLAUDE Message Handler Flow):
    - Get or create customer from Telegram user/chat
    - Resolve business_id for this bot/chat
    - Check active support_session; if active, forward to group and return
    - Load last 20 messages + build system prompt from DB
    - Call ai_service.process_message via handle_incoming_message
    - Dispatch actions (SHOW_SLOTS, SHOW_BOOKINGS, etc.) via booking/appointments/support handlers

    This function intentionally leaves DB details and mappings as TODOs, but
    provides a minimal working loop for development.
    """

    # Extract chat_id and text from a basic message update.
    # More update types (callbacks, edited messages) can be added later.
    message = update.get("message") or update.get("edited_message") or {}
    chat = message.get("chat") or {}
    chat_id = chat.get("id")
    text = message.get("text") or ""

    if chat_id is None or not text:
        return

    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    channel = TelegramChannel(bot=bot)
    recipient_id = str(chat_id)
    telegram_id = str(chat_id)
    from_user = message.get("from") or {}
    full_name = from_user.get("first_name") or from_user.get("last_name") or None

    business = await get_first_active_business(session)
    if not business:
        await channel.send_message(recipient_id, "No business configured yet. Please try again later.")
        return

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
            await booking.show_available_slots(
                channel,
                recipient_id,
                business_id,
                _uuid_from_data(data, "service_id"),
                data.get("date") or "",
                party_size,
                session=session,
            )
        elif result.action == AIAction.SHOW_BOOKINGS:
            await appointments.show_bookings(
                channel, recipient_id, customer_id, business_id
            )
        elif result.action == AIAction.MANAGE_BOOKING:
            await appointments.show_manage_options(
                channel, recipient_id, _uuid_from_data(data, "booking_id")
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

