"""Booking API schemas."""
from datetime import date, time
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class BookingCreate(BaseModel):
    """Create booking request."""

    business_id: UUID
    customer_id: UUID
    service_id: UUID
    staff_id: UUID | None = None
    booking_date: date
    booking_time: time
    party_size: int | None = None
    special_requests: str | None = None


class BookingUpdate(BaseModel):
    """Reschedule: new date/time."""

    booking_date: date | None = None
    booking_time: time | None = None


class BookingResponse(BaseModel):
    """Booking in API response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    business_id: UUID
    customer_id: UUID
    service_id: UUID
    staff_id: UUID | None
    booking_date: date
    booking_time: time
    party_size: int | None
    status: str
    booking_reference: str
    special_requests: str | None
