"""Service API schemas."""
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ServiceCreate(BaseModel):
    """Create a service (table type, room type, etc.)."""

    name: str
    description: str | None = None
    duration_minutes: int
    price: Decimal | float | None = None
    capacity: int | None = None


class ServiceUpdate(BaseModel):
    """Partial update."""

    name: str | None = None
    description: str | None = None
    duration_minutes: int | None = None
    price: Decimal | float | None = None
    capacity: int | None = None
    is_active: bool | None = None


class ServiceResponse(BaseModel):
    """Service in API response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    business_id: UUID
    name: str
    description: str | None
    duration_minutes: int
    price: Decimal | None
    capacity: int | None
    is_active: bool
