"""Service / Room-type model."""
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.db.booking import Booking
    from app.models.db.business import Business


class Service(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "services"

    business_id: Mapped[UUID] = mapped_column(ForeignKey("businesses.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=60)
    price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    capacity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    image_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    max_occupancy: Mapped[int | None] = mapped_column(Integer, nullable=True)
    bed_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    amenities: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    base_price_per_night: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    room_count: Mapped[int | None] = mapped_column(Integer, nullable=True)

    business: Mapped["Business"] = relationship("Business", back_populates="services")
    bookings: Mapped[list["Booking"]] = relationship("Booking", back_populates="service")
