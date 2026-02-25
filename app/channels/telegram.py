"""Telegram channel implementation. Used for development and testing."""
from typing import Any

from app.channels.base import BaseChannel


class TelegramChannel(BaseChannel):
    """Telegram implementation of BaseChannel. Uses python-telegram-bot; actual send calls are wired by the bot layer."""

    async def send_message(self, recipient_id: str, text: str) -> None:
        # Handlers/bot pass this to the Telegram API (via bot instance). No direct API call here per CLAUDE.
        raise NotImplementedError("TelegramChannel.send_message: wire via bot application context")

    async def send_buttons(
        self, recipient_id: str, text: str, buttons: list[dict[str, Any]]
    ) -> None:
        raise NotImplementedError("TelegramChannel.send_buttons: wire via bot application context")

    async def send_list(
        self, recipient_id: str, text: str, items: list[dict[str, Any]]
    ) -> None:
        raise NotImplementedError("TelegramChannel.send_list: wire via bot application context")

    async def send_typing(self, recipient_id: str) -> None:
        raise NotImplementedError("TelegramChannel.send_typing: wire via bot application context")

    async def forward_to_group(self, group_id: str, text: str) -> None:
        raise NotImplementedError("TelegramChannel.forward_to_group: wire via bot application context")
