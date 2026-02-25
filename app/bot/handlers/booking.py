"""Booking flow: show_available_slots, show_confirmation, on_booking_confirmed. See CLAUDE Booking Flow."""
from uuid import UUID

from app.bot.keyboards import confirm_booking_buttons
from app.channels.base import BaseChannel
from app.utils.message_templates import confirmation_body


async def show_available_slots(
    channel: BaseChannel,
    recipient_id: str,
    business_id: UUID,
    service_id: UUID,
    booking_date: str,
    party_size: int | None,
) -> None:
    """Get working hours, generate slots, exclude booked, send as buttons (max 8 per page)."""
    # TODO: load business, generate slots via datetime_utils, query bookings, send_buttons
    pass


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
