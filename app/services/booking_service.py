"""Booking business logic. Handlers and routes call this; no DB in handlers."""
from datetime import date, time as time_type
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.db import Booking, Business, Service
from app.models.db.booking import BookingStatusEnum
from app.utils.datetime_utils import (
    generate_slots_for_day,
    slot_taken,
    weekday_key,
)


async def get_available_slots(
    session: AsyncSession,
    business_id: UUID,
    service_id: UUID,
    booking_date: str,
) -> list[dict]:
    """Return list of available slot dicts with 'label' and 'time' for the day."""
    try:
        day = date.fromisoformat(booking_date)
    except ValueError:
        return []

    result = await session.execute(
        select(Business)
        .where(Business.id == business_id)
        .options(selectinload(Business.services))
        .limit(1)
    )
    business = result.scalars().first()
    if not business:
        return []

    service_result = await session.execute(
        select(Service).where(Service.id == service_id, Service.business_id == business_id).limit(1)
    )
    service = service_result.scalars().first()
    duration = service.duration_minutes if service else 30

    key = weekday_key(day)
    hours = business.working_hours.get(key) if isinstance(business.working_hours, dict) else None
    if not hours or len(hours) < 2:
        return []
    start_str, end_str = hours[0], hours[1]
    slot_duration = business.slot_duration_minutes or 30

    all_slots = generate_slots_for_day(day, start_str, end_str, slot_duration)
    if not all_slots:
        return []

    bookings_result = await session.execute(
        select(Booking)
        .where(
            Booking.business_id == business_id,
            Booking.booking_date == day,
            Booking.status == BookingStatusEnum.confirmed,
        )
        .options(selectinload(Booking.service))
    )
    booked = bookings_result.scalars().all()
    booked_list = [
        {"booking_time": b.booking_time, "duration_minutes": b.service.duration_minutes if b.service else duration}
        for b in booked
    ]

    available = []
    for t in all_slots:
        if not slot_taken(t, duration, booked_list):
            label = t.strftime("%I:%M %p").lstrip("0")
            available.append({"label": label, "time": t.isoformat(), "payload": {"time": t.isoformat()}})
    return available


async def create_booking(
    session: AsyncSession,
    business_id: UUID,
    customer_id: UUID,
    service_id: UUID,
    booking_date: str,
    booking_time: str,
    party_size: int | None,
    special_requests: str | None,
) -> dict:
    """Create booking (status=confirmed), generate reference, return booking dict. Re-check slot free."""
    # TODO: race check, insert booking, generate RST-/HST- reference, return booking
    return {}


async def cancel_booking(session: AsyncSession, booking_id: UUID) -> bool:
    """Set status=cancelled, remove reminder jobs. Return True if found and cancelled."""
    # TODO: load booking, update status, delete APScheduler jobs by reminder_24h_job_id, reminder_1h_job_id
    return False
