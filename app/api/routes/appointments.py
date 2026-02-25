"""Appointment CRUD endpoints. See CLAUDE FastAPI Endpoints."""
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db
from app.models.schemas.booking import BookingCreate, BookingResponse, BookingUpdate

router = APIRouter(prefix="/api/bookings", tags=["bookings"])


@router.get("", response_model=list[BookingResponse])
async def list_bookings(session: AsyncSession = Depends(get_db)) -> list:
    # TODO: query bookings (admin filter), return list
    return []


@router.post("", response_model=BookingResponse)
async def create_booking(
    body: BookingCreate,
    session: AsyncSession = Depends(get_db),
) -> dict:
    # TODO: call booking_service.create_booking
    return {}


@router.patch("/{booking_id}", response_model=BookingResponse)
async def reschedule_booking(
    booking_id: UUID,
    body: BookingUpdate,
    session: AsyncSession = Depends(get_db),
) -> dict:
    # TODO: load booking, update date/time, optionally reschedule calendar + reminders
    return {}


@router.delete("/{booking_id}")
async def cancel_booking(
    booking_id: UUID,
    session: AsyncSession = Depends(get_db),
) -> dict:
    # TODO: call booking_service.cancel_booking
    return {"status": "cancelled"}
