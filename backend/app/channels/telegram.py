"""Telegram channel implementation. Used for development and testing (high-level via python-telegram-bot)."""
from typing import Any

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ChatAction

from app.channels.base import BaseChannel
from app.core.config import settings


class TelegramChannel(BaseChannel):
    """Telegram implementation of BaseChannel using python-telegram-bot's Bot."""

    def __init__(self, bot: Bot | None = None) -> None:
        # Create a Bot on demand if not injected (webhook mode).
        self._bot = bot or Bot(token=settings.TELEGRAM_BOT_TOKEN)

    @property
    def bot(self) -> Bot:
        return self._bot

    async def send_message(self, recipient_id: str, text: str) -> None:
        """Send a plain text message."""
        await self.bot.send_message(chat_id=int(recipient_id), text=text)

    async def send_buttons(
        self, recipient_id: str, text: str, buttons: list[dict[str, Any]]
    ) -> None:
        """Send a message with inline keyboard built from button dicts."""
        keyboard: list[list[InlineKeyboardButton]] = []
        for b in buttons:
            label = b.get("label", "")
            callback_data = b.get("action") or b.get("payload") or label
            keyboard.append([InlineKeyboardButton(label, callback_data=str(callback_data))])

        markup = InlineKeyboardMarkup(keyboard) if keyboard else None
        await self.bot.send_message(chat_id=int(recipient_id), text=text, reply_markup=markup)

    async def send_list(
        self, recipient_id: str, text: str, items: list[dict[str, Any]]
    ) -> None:
        """Render list items as one button per row (same as send_buttons)."""
        buttons = [
            {"label": item.get("label", str(item)), "action": item.get("action") or item}
            for item in items
        ]
        await self.send_buttons(recipient_id, text, buttons)

    async def send_typing(self, recipient_id: str) -> None:
        """Show typing indicator."""
        await self.bot.send_chat_action(chat_id=int(recipient_id), action=ChatAction.TYPING)

    async def forward_to_group(self, group_id: str, text: str) -> None:
        """Send message to staff Telegram group."""
        await self.bot.send_message(chat_id=int(group_id), text=text)
