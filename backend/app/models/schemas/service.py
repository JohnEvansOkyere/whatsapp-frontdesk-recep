"""Service / Room-type API schemas."""
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ServiceCreate(BaseModel):
    name: str
    description: str | None = None
    duration_minutes: int = 60
    price: Decimal | float | None = None
    capacity: int | None = None
    image_url: str | None = None
    max_occupancy: int | None = None
    bed_type: str | None = None
    amenities: list[str] | None = None
    base_price_per_night: Decimal | float | None = None
    room_count: int | None = None


class ServiceUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    duration_minutes: int | None = None
    price: Decimal | float | None = None
    capacity: int | None = None
    is_active: bool | None = None
    image_url: str | None = None
    max_occupancy: int | None = None
    bed_type: str | None = None
    amenities: list[str] | None = None
    base_price_per_night: Decimal | float | None = None
    room_count: int | None = None


class ServiceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    business_id: UUID
    name: str
    description: str | None
    duration_minutes: int
    price: Decimal | None
    capacity: int | None
    is_active: bool
    image_url: str | None
    max_occupancy: int | None
    bed_type: str | None
    amenities: list[str] | None
    base_price_per_night: Decimal | None
    room_count: int | None
