"""Booking business logic. Handlers and routes call this; no DB in handlers."""
import random
import string
from datetime import date, time as time_type
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.db import Booking, Business, Service
from app.models.db.business import BusinessTypeEnum
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


def _generate_booking_reference(business_type: BusinessTypeEnum, day: date) -> str:
    """RST-YYYYMMDD-XXXX or HST-YYYYMMDD-XXXX with XXXX = 4 random alphanumeric."""
    prefix = "RST-" if business_type == BusinessTypeEnum.restaurant else "HST-"
    date_str = day.strftime("%Y%m%d")
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"{prefix}{date_str}-{suffix}"


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
    try:
        day = date.fromisoformat(booking_date)
    except ValueError:
        return {}
    if ":" in booking_time:
        parts = booking_time.strip().split(":")
        h = int(parts[0]) if len(parts) > 0 else 0
        m = int(parts[1]) if len(parts) > 1 else 0
        s = int(parts[2]) if len(parts) > 2 else 0
        t = time_type(h, m, s)
    else:
        t = time_type(0, 0, 0)

    business_result = await session.execute(
        select(Business).where(Business.id == business_id).limit(1)
    )
    business = business_result.scalars().first()
    if not business:
        return {}

    service_result = await session.execute(
        select(Service).where(Service.id == service_id, Service.business_id == business_id).limit(1)
    )
    service = service_result.scalars().first()
    duration = service.duration_minutes if service else 30

    # Race check: slot still free
    existing = await session.execute(
        select(Booking).where(
            Booking.business_id == business_id,
            Booking.booking_date == day,
            Booking.status == BookingStatusEnum.confirmed,
        ).options(selectinload(Booking.service))
    )
    booked_list = [
        {"booking_time": b.booking_time, "duration_minutes": b.service.duration_minutes if b.service else duration}
        for b in existing.scalars().all()
    ]
    if slot_taken(t, duration, booked_list):
        return {}

    ref = _generate_booking_reference(business.type, day)
    booking = Booking(
        business_id=business_id,
        customer_id=customer_id,
        service_id=service_id,
        booking_date=day,
        booking_time=t,
        party_size=party_size,
        status=BookingStatusEnum.confirmed,
        booking_reference=ref,
        special_requests=special_requests,
    )
    session.add(booking)
    await session.flush()
    return {
        "id": str(booking.id),
        "booking_reference": booking.booking_reference,
        "booking_date": booking_date,
        "booking_time": t.isoformat(),
        "service_id": str(service_id),
        "party_size": party_size,
    }


async def update_booking_reminder_jobs(
    session: AsyncSession,
    booking_id: UUID,
    reminder_24h_job_id: str | None,
    reminder_1h_job_id: str | None,
) -> None:
    """Store APScheduler job ids on the booking for later cancellation."""
    result = await session.execute(select(Booking).where(Booking.id == booking_id).limit(1))
    b = result.scalars().first()
    if b:
        b.reminder_24h_job_id = reminder_24h_job_id
        b.reminder_1h_job_id = reminder_1h_job_id
        await session.flush()


async def cancel_booking(session: AsyncSession, booking_id: UUID) -> bool:
    """Set status=cancelled, remove reminder jobs. Return True if found and cancelled."""
    from app.services.reminder_service import cancel_reminders
    result = await session.execute(select(Booking).where(Booking.id == booking_id).limit(1))
    b = result.scalars().first()
    if not b:
        return False
    cancel_reminders(b.reminder_24h_job_id, b.reminder_1h_job_id)
    b.status = BookingStatusEnum.cancelled
    await session.flush()
    return True


async def get_bookings_for_customer(
    session: AsyncSession,
    customer_id: UUID,
    business_id: UUID,
    *,
    upcoming_only: bool = True,
) -> list[dict]:
    """List bookings for a customer at a business. Default: upcoming confirmed only."""
    from datetime import date

    q = (
        select(Booking)
        .where(
            Booking.customer_id == customer_id,
            Booking.business_id == business_id,
            Booking.status == BookingStatusEnum.confirmed,
        )
        .options(selectinload(Booking.service))
        .order_by(Booking.booking_date, Booking.booking_time)
    )
    result = await session.execute(q)
    bookings = result.scalars().all()
    if upcoming_only:
        today = date.today()
        bookings = [b for b in bookings if b.booking_date >= today]
    return [
        {
            "id": str(b.id),
            "booking_reference": b.booking_reference,
            "booking_date": b.booking_date.isoformat(),
            "booking_time": b.booking_time.isoformat() if hasattr(b.booking_time, "isoformat") else str(b.booking_time),
            "service_name": b.service.name if b.service else "—",
        }
        for b in bookings
    ]


async def get_booking(session: AsyncSession, booking_id: UUID) -> dict | None:
    """Load one booking by id with service; return dict or None."""
    result = await session.execute(
        select(Booking)
        .where(Booking.id == booking_id)
        .options(selectinload(Booking.service))
        .limit(1)
    )
    b = result.scalars().first()
    if not b:
        return None
    return {
        "id": str(b.id),
        "booking_reference": b.booking_reference,
        "booking_date": b.booking_date.isoformat(),
        "booking_time": b.booking_time.isoformat() if hasattr(b.booking_time, "isoformat") else str(b.booking_time),
        "service_name": b.service.name if b.service else "—",
        "status": b.status.value,
    }


async def reschedule_booking(
    session: AsyncSession,
    booking_id: UUID,
    new_date: date,
    new_time: time_type,
) -> dict | None:
    """Update booking date/time, cancel old reminders, schedule new ones. Return booking dict or None."""
    from app.services.reminder_service import cancel_reminders, schedule_reminders

    result = await session.execute(
        select(Booking)
        .where(Booking.id == booking_id, Booking.status == BookingStatusEnum.confirmed)
        .options(
            selectinload(Booking.service),
            selectinload(Booking.customer),
            selectinload(Booking.business),
        )
        .limit(1)
    )
    b = result.scalars().first()
    if not b or not b.business or not b.customer:
        return None
    cancel_reminders(b.reminder_24h_job_id, b.reminder_1h_job_id)
    b.booking_date = new_date
    b.booking_time = new_time
    await session.flush()

    time_str = new_time.isoformat() if hasattr(new_time, "isoformat") else str(new_time)
    rid_24h, rid_1h = schedule_reminders(
        b.id,
        new_date.isoformat(),
        time_str,
        b.business.name,
        b.customer.telegram_id or "",
        b.booking_reference,
        str(b.party_size or ""),
    )
    await update_booking_reminder_jobs(session, b.id, rid_24h, rid_1h)
    return await get_booking(session, booking_id)
