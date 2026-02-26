"""Business API schemas."""
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class BusinessCreate(BaseModel):
    name: str
    type: str  # restaurant | hostel | hotel
    telegram_bot_token: str | None = None
    telegram_group_id: str | None = None
    working_hours: dict[str, list[str]]
    slot_duration_minutes: int = 30
    timezone: str = "Africa/Accra"
    location: str | None = None
    phone: str | None = None


class BusinessUpdate(BaseModel):
    name: str | None = None
    type: str | None = None
    telegram_bot_token: str | None = None
    telegram_group_id: str | None = None
    working_hours: dict[str, list[str]] | None = None
    slot_duration_minutes: int | None = None
    timezone: str | None = None
    location: str | None = None
    phone: str | None = None


class BusinessResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    type: str
    telegram_group_id: str | None
    active_channel: str
    is_active: bool


class BusinessDetailResponse(BusinessResponse):
    working_hours: dict[str, list[str]]
    slot_duration_minutes: int
    timezone: str
    location: str | None
    phone: str | None
    telegram_bot_token: str | None = None
