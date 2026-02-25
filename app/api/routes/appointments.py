"""Appointment CRUD endpoints. See CLAUDE FastAPI Endpoints."""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db
from app.models.db import Booking
from app.models.db.booking import BookingStatusEnum
from app.models.schemas.booking import BookingCreate, BookingResponse, BookingUpdate
from app.services import booking_service

router = APIRouter(prefix="/api/bookings", tags=["bookings"])


@router.get("", response_model=list[BookingResponse])
async def list_bookings(
    session: AsyncSession = Depends(get_db),
    business_id: UUID | None = None,
    customer_id: UUID | None = None,
) -> list[Booking]:
    """List confirmed bookings, optionally filtered by business_id and/or customer_id."""
    q = (
        select(Booking)
        .where(Booking.status == BookingStatusEnum.confirmed)
        .order_by(Booking.booking_date, Booking.booking_time)
    )
    if business_id is not None:
        q = q.where(Booking.business_id == business_id)
    if customer_id is not None:
        q = q.where(Booking.customer_id == customer_id)
    result = await session.execute(q)
    return list(result.scalars().all())


@router.post("", response_model=BookingResponse)
async def create_booking(
    body: BookingCreate,
    session: AsyncSession = Depends(get_db),
) -> Booking:
    """Create a new booking (confirmed). Returns the created booking or 400 if slot taken."""
    data = await booking_service.create_booking(
        session,
        business_id=body.business_id,
        customer_id=body.customer_id,
        service_id=body.service_id,
        booking_date=body.booking_date.isoformat(),
        booking_time=body.booking_time.isoformat(),
        party_size=body.party_size,
        special_requests=body.special_requests,
    )
    if not data:
        raise HTTPException(status_code=400, detail="Slot not available or invalid request")
    result = await session.execute(
        select(Booking).where(Booking.id == UUID(data["id"])).limit(1)
    )
    booking = result.scalar_one_or_none()
    if not booking:
        raise HTTPException(status_code=500, detail="Booking created but could not be loaded")
    return booking


@router.patch("/{booking_id}", response_model=BookingResponse)
async def reschedule_booking(
    booking_id: UUID,
    body: BookingUpdate,
    session: AsyncSession = Depends(get_db),
) -> Booking:
    """Reschedule an existing booking (date and/or time). Updates reminders."""
    if body.booking_date is None and body.booking_time is None:
        raise HTTPException(status_code=400, detail="Provide booking_date and/or booking_time")
    result = await session.execute(
        select(Booking).where(Booking.id == booking_id).limit(1)
    )
    booking = result.scalar_one_or_none()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    from datetime import date, time

    new_date = body.booking_date if body.booking_date is not None else booking.booking_date
    new_time = body.booking_time if body.booking_time is not None else booking.booking_time
    updated = await booking_service.reschedule_booking(
        session, booking_id, new_date, new_time
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Booking not found or could not be rescheduled")
    result2 = await session.execute(
        select(Booking).where(Booking.id == booking_id).limit(1)
    )
    out = result2.scalars().first()
    if not out:
        raise HTTPException(status_code=500, detail="Booking not found after reschedule")
    return out


@router.delete("/{booking_id}")
async def cancel_booking(
    booking_id: UUID,
    session: AsyncSession = Depends(get_db),
) -> dict:
    """Cancel a booking. Returns status."""
    cancelled = await booking_service.cancel_booking(session, booking_id)
    if not cancelled:
        raise HTTPException(status_code=404, detail="Booking not found or already cancelled")
    return {"status": "cancelled"}
