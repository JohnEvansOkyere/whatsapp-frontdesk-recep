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

    This function intentionally leaves DB details and mappings as TODOs.
    """

    # TODO: extract chat_id / user_id and message text safely from update
    # Example (not assuming exact schema):
    # chat_id = ...
    # text = ...

    # TODO: resolve business_id: UUID = ...
    # TODO: get/create customer_id: UUID = ...
    # TODO: build system_prompt string from business + FAQ + booking context
    # TODO: load last 20 messages from conversation_history and build `messages` list

    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    channel = TelegramChannel(bot=bot)

    # Placeholder values so the call shape is clear; real implementation must
    # replace these with actual IDs and message history.
    dummy_business_id = UUID(int=0)
    dummy_customer_id = UUID(int=0)
    dummy_recipient_id = "0"
    dummy_text = ""
    system_prompt = ""
    messages: list[dict[str, str]] = []

    await handle_incoming_message(
        channel=channel,
        recipient_id=dummy_recipient_id,
        business_id=dummy_business_id,
        customer_id=dummy_customer_id,
        text=dummy_text,
        system_prompt=system_prompt,
        messages=messages,
    )

