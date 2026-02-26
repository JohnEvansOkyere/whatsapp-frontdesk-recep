"""View, reschedule, cancel bookings. See CLAUDE Message Handler Flow — SHOW_BOOKINGS, MANAGE_BOOKING."""
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.channels.base import BaseChannel
from app.services.booking_service import get_booking, get_bookings_for_customer


async def show_bookings(
    channel: BaseChannel,
    recipient_id: str,
    customer_id: UUID,
    business_id: UUID,
    *,
    session: AsyncSession,
) -> None:
    """List customer's upcoming bookings; send as list or message with buttons."""
    bookings = await get_bookings_for_customer(
        session, customer_id, business_id, upcoming_only=True
    )
    if not bookings:
        await channel.send_message(
            recipient_id,
            "You don't have any upcoming bookings. Say 'I'd like to book' to make a reservation.",
        )
        return
    intro = "Here are your upcoming bookings. Tap one to reschedule or cancel."
    items = [
        {
            "label": f"{b['booking_reference']} — {b['booking_date']} {b['booking_time'][:5]} — {b['service_name']}",
            "action": f"manage_booking_{b['id']}",
        }
        for b in bookings
    ]
    await channel.send_list(recipient_id, intro, items)


async def show_manage_options(
    channel: BaseChannel,
    recipient_id: str,
    booking_id: UUID,
    *,
    session: AsyncSession,
) -> None:
    """Show reschedule / cancel options for one booking."""
    booking = await get_booking(session, booking_id)
    if not booking:
        await channel.send_message(recipient_id, "Booking not found.")
        return
    text = (
        f"Booking {booking['booking_reference']} — {booking['booking_date']} at {booking['booking_time'][:5]} "
        f"({booking['service_name']}). What would you like to do?"
    )
    buttons = [
        {"label": "🔄 Reschedule", "action": f"manage_reschedule_{booking_id}"},
        {"label": "❌ Cancel booking", "action": f"manage_cancel_{booking_id}"},
    ]
    await channel.send_buttons(recipient_id, text, buttons)
