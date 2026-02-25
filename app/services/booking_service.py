"""Booking business logic. Handlers and routes call this; no DB in handlers."""
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession


async def get_available_slots(
    session: AsyncSession,
    business_id: UUID,
    service_id: UUID,
    booking_date: str,
) -> list[dict]:
    """Return list of available slot dicts (start time, label, etc.) for the day."""
    # TODO: load business working_hours, slot_duration_minutes; generate slots; query bookings; filter.
    return []


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
