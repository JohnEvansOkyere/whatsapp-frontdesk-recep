"""View, reschedule, cancel bookings. See CLAUDE Message Handler Flow — SHOW_BOOKINGS, MANAGE_BOOKING."""
from uuid import UUID

from app.channels.base import BaseChannel


async def show_bookings(
    channel: BaseChannel,
    recipient_id: str,
    customer_id: UUID,
    business_id: UUID,
) -> None:
    """List customer's upcoming bookings; send as list or buttons."""
    # TODO: query bookings by customer_id + business_id, format, send_list/send_buttons
    pass


async def show_manage_options(
    channel: BaseChannel,
    recipient_id: str,
    booking_id: UUID,
) -> None:
    """Show reschedule / cancel options for one booking."""
    # TODO: load booking, send buttons for reschedule / cancel
    pass
