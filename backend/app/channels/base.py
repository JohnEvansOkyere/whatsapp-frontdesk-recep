"""Abstract channel interface. All messaging goes through this — never call Telegram/WhatsApp APIs directly from handlers or services."""
from abc import ABC, abstractmethod
from typing import Any


class BaseChannel(ABC):
    """Interface that Telegram and WhatsApp implementations must implement."""

    @abstractmethod
    async def send_message(self, recipient_id: str, text: str) -> None:
        """Send a plain text message to the recipient."""
        ...

    @abstractmethod
    async def send_buttons(self, recipient_id: str, text: str, buttons: list[dict[str, Any]]) -> None:
        """Send a message with inline/reply buttons. Button shape is channel-specific."""
        ...

    @abstractmethod
    async def send_list(self, recipient_id: str, text: str, items: list[dict[str, Any]]) -> None:
        """Send a message with a list (e.g. slot options, services). Item shape is channel-specific."""
        ...

    @abstractmethod
    async def send_typing(self, recipient_id: str) -> None:
        """Show typing indicator to the recipient."""
        ...

    @abstractmethod
    async def forward_to_group(self, group_id: str, text: str) -> None:
        """Forward a message to the business Telegram group (e.g. support notifications)."""
        ...
