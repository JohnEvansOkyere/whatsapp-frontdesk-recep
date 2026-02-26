"""Customer API schemas."""
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CustomerCreate(BaseModel):
    """Create customer (e.g. from webhook)."""

    telegram_id: str | None = None
    whatsapp_number: str | None = None
    full_name: str | None = None
    phone_number: str | None = None


class CustomerResponse(BaseModel):
    """Customer in API response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    telegram_id: str | None
    whatsapp_number: str | None
    full_name: str | None
    phone_number: str | None
