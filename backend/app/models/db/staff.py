"""Staff/doctor model."""
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.db.base import Base, UUIDMixin

if TYPE_CHECKING:
    from app.models.db.booking import Booking
    from app.models.db.business import Business


class Staff(Base, UUIDMixin):
    __tablename__ = "staff"

    business_id: Mapped[UUID] = mapped_column(ForeignKey("businesses.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str | None] = mapped_column(String(128), nullable=True)
    telegram_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    business: Mapped["Business"] = relationship("Business", back_populates="staff")
    bookings: Mapped[list["Booking"]] = relationship("Booking", back_populates="staff")
