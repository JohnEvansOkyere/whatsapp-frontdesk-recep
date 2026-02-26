"""WhatsApp channel implementation (Meta Cloud API). Credentials per business in DB."""
from typing import Any

from app.channels.base import BaseChannel


class WhatsAppChannel(BaseChannel):
    """WhatsApp (Meta Cloud API) implementation. Uses business-specific whatsapp_config from DB."""

    def __init__(
        self,
        phone_number_id: str,
        access_token: str,
    ) -> None:
        self.phone_number_id = phone_number_id
        self.access_token = access_token

    async def send_message(self, recipient_id: str, text: str) -> None:
        # POST to Meta Cloud API; use httpx. Implement when wiring webhook.
        raise NotImplementedError("WhatsAppChannel.send_message: implement Meta API call with httpx")

    async def send_buttons(
        self, recipient_id: str, text: str, buttons: list[dict[str, Any]]
    ) -> None:
        raise NotImplementedError("WhatsAppChannel.send_buttons: implement Meta API call with httpx")

    async def send_list(
        self, recipient_id: str, text: str, items: list[dict[str, Any]]
    ) -> None:
        raise NotImplementedError("WhatsAppChannel.send_list: implement Meta API call with httpx")

    async def send_typing(self, recipient_id: str) -> None:
        # Meta may not support typing; no-op or map to available feature.
        pass

    async def forward_to_group(self, group_id: str, text: str) -> None:
        # WhatsApp business: forward to internal group or equivalent; define per product.
        raise NotImplementedError("WhatsAppChannel.forward_to_group: define behavior for WhatsApp")
