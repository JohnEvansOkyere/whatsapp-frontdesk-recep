"""FAQ handler. AI answers from FAQ knowledge base; this module for any direct FAQ reply if needed."""
from app.channels.base import BaseChannel


async def reply_faq(
    channel: BaseChannel,
    recipient_id: str,
    text: str,
) -> None:
    """Send a single FAQ-style reply. Usually AI handles FAQ via system prompt."""
    await channel.send_message(recipient_id, text)
