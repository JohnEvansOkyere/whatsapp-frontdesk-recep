"""Booking flow: show_available_slots, show_confirmation, on_booking_confirmed. See CLAUDE Booking Flow."""
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards import confirm_booking_buttons, slot_buttons
from app.channels.base import BaseChannel
from app.services.booking_service import get_available_slots
from app.utils.message_templates import confirmation_body


async def show_available_slots(
    channel: BaseChannel,
    recipient_id: str,
    business_id: UUID,
    service_id: UUID,
    booking_date: str,
    party_size: int | None,
    session: AsyncSession | None = None,
) -> None:
    """Get working hours, generate slots, exclude booked, send as buttons (max 8 per page)."""
    if not session:
        return
    slots = await get_available_slots(session, business_id, service_id, booking_date)
    if not slots:
        await channel.send_message(recipient_id, "No available slots for that date. Try another day?")
        return
    buttons = slot_buttons(slots, page=0, per_page=8)
    text = f"Available slots for {booking_date}:\n\nPick a time:"
    await channel.send_buttons(recipient_id, text, buttons)


async def show_confirmation(
    channel: BaseChannel,
    recipient_id: str,
    business_name: str,
    service_name: str,
    party_size: int | None,
    formatted_date: str,
    time_str: str,
    price_str: str,
    requests_str: str,
) -> None:
    """Send confirmation text and Confirm/Cancel buttons."""
    text = confirmation_body(
        business_name=business_name,
        service_name=service_name,
        party_size=party_size,
        formatted_date=formatted_date,
        time_str=time_str,
        price_str=price_str,
        requests_str=requests_str,
    )
    buttons = confirm_booking_buttons()
    await channel.send_buttons(recipient_id, text, buttons)


async def on_booking_confirmed(
    channel: BaseChannel,
    recipient_id: str,
    business_id: UUID,
    booking_data: dict,
) -> None:
    """Re-check slot, save booking, create calendar event, notify group, schedule reminders."""
    # TODO: implement full CLAUDE on_booking_confirmed steps
    pass
