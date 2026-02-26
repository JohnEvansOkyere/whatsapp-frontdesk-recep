"""All incoming messages enter here. See CLAUDE Message Handler Flow."""
from uuid import UUID

from app.channels.base import BaseChannel
from app.services.ai_service import AIResult, process_message


async def handle_incoming_message(
    channel: BaseChannel,
    recipient_id: str,
    business_id: UUID,
    customer_id: UUID,
    text: str,
    system_prompt: str,
    messages: list[dict[str, str]],
) -> AIResult | None:
    """
    High-level entry: get AI result, then dispatch by action.
    Caller is responsible for: loading conversation history, building system_prompt, saving messages.
    Returns AIResult so caller can dispatch SHOW_SLOTS, SHOW_BOOKINGS, etc.
    """
    result = await process_message(system_prompt=system_prompt, messages=messages)
    # Caller sends result.reply_text via channel and dispatches result.action (booking, appointments, support).
    return result
