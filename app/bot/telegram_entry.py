"""Telegram entrypoint orchestration.

High-level flow only; concrete DB queries and mappings are left as TODOs.
"""
from __future__ import annotations

from typing import Any, Dict
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from telegram import Bot

from app.bot.handlers.message_handler import handle_incoming_message
from app.channels.telegram import TelegramChannel
from app.core.config import settings


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
        # Nothing to do (e.g. non-text message); ignore for now.
        return

    # TODO: resolve business_id: UUID = ...
    # TODO: get/create customer_id: UUID = ...
    # TODO: build full system_prompt string from business + FAQ + booking context
    # TODO: load last 20 messages from conversation_history and build `messages` list

    # Minimal prompt for early development; replace with full CLAUDE prompt later.
    system_prompt = "You are a helpful front desk assistant. Answer briefly."
    messages: list[dict[str, str]] = [{"role": "user", "content": text}]

    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    channel = TelegramChannel(bot=bot)

    # Placeholder IDs until proper multi-tenant mapping and customer lookup are implemented.
    dummy_business_id = UUID(int=0)
    dummy_customer_id = UUID(int=0)

    result = await handle_incoming_message(
        channel=channel,
        recipient_id=str(chat_id),
        business_id=dummy_business_id,
        customer_id=dummy_customer_id,
        text=text,
        system_prompt=system_prompt,
        messages=messages,
    )

    if result and result.reply_text:
        await channel.send_message(str(chat_id), result.reply_text)

