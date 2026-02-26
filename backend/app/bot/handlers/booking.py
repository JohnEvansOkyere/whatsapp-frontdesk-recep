"""Booking flow: show_available_slots, show_confirmation, on_booking_confirmed. See CLAUDE Booking Flow."""
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.bot.keyboards import confirm_booking_buttons, slot_buttons
from app.channels.base import BaseChannel
from app.models.db import Business, Customer, Service
from app.services.booking_service import (
    create_booking,
    get_available_slots,
    update_booking_reminder_jobs,
)
from app.services.reminder_service import schedule_reminders
from app.utils.message_templates import confirmation_body, new_booking_notification


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
    session: AsyncSession,
    channel: BaseChannel,
    recipient_id: str,
    business_id: UUID,
    customer_id: UUID,
    pending_booking: dict,
) -> None:
    """Re-check slot, save booking, schedule reminders, notify group, send confirmation."""
    service_id = pending_booking.get("service_id")
    booking_date = pending_booking.get("booking_date") or ""
    booking_time = pending_booking.get("booking_time") or ""
    party_size = pending_booking.get("party_size")
    special_requests = pending_booking.get("special_requests")
    if not service_id or not booking_date or not booking_time:
        await channel.send_message(recipient_id, "Booking data missing. Please start again.")
        return
    if isinstance(service_id, str):
        service_id = UUID(service_id)

    created = await create_booking(
        session,
        business_id=business_id,
        customer_id=customer_id,
        service_id=service_id,
        booking_date=booking_date,
        booking_time=booking_time,
        party_size=party_size,
        special_requests=special_requests,
    )
    if not created:
        await channel.send_message(recipient_id, "That slot was just taken. Please pick another time.")
        return

    ref = created.get("booking_reference", "")
    bid = created.get("id")
    if bid:
        booking_uuid = UUID(bid)
    else:
        booking_uuid = None

    business_result = await session.execute(
        select(Business).where(Business.id == business_id).options(selectinload(Business.services)).limit(1)
    )
    business = business_result.scalars().first()
    customer_result = await session.execute(select(Customer).where(Customer.id == customer_id).limit(1))
    customer = customer_result.scalars().first()
    service_result = await session.execute(
        select(Service).where(Service.id == service_id).limit(1)
    )
    service = service_result.scalars().first()

    business_name = business.name if business else "Business"
    customer_name = customer.full_name or "Guest" if customer else "Guest"
    customer_phone = customer.phone_number or "" if customer else ""
    service_name = service.name if service else "Service"
    size_str = str(party_size) if party_size is not None else ""

    job_24h, job_1h = schedule_reminders(
        booking_id=booking_uuid or UUID(int=0),
        booking_date=booking_date,
        booking_time=booking_time,
        business_name=business_name,
        customer_recipient_id=recipient_id,
        reference=ref,
        party_size=size_str,
    )
    if booking_uuid:
        await update_booking_reminder_jobs(session, booking_uuid, job_24h, job_1h)

    if business and business.telegram_group_id:
        await channel.forward_to_group(
            business.telegram_group_id,
            new_booking_notification(
                name=customer_name,
                phone=customer_phone,
                service=service_name,
                date=booking_date,
                time=booking_time,
                size=size_str or None,
                reference=ref,
                requests=special_requests or "",
            ),
        )

    await channel.send_message(
        recipient_id,
        f"✅ Booked! Your reference is {ref}. We'll send you a reminder before your appointment.",
    )
