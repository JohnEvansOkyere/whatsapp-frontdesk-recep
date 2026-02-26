"""Booking model."""
import enum
from datetime import date, time
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Date, Enum, ForeignKey, Integer, Numeric, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.db.business import Business
    from app.models.db.customer import Customer
    from app.models.db.service import Service
    from app.models.db.staff import Staff


class BookingStatusEnum(str, enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    cancelled = "cancelled"
    completed = "completed"
    no_show = "no_show"


class Booking(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "bookings"

    business_id: Mapped[UUID] = mapped_column(ForeignKey("businesses.id"), nullable=False)
    customer_id: Mapped[UUID] = mapped_column(ForeignKey("customers.id"), nullable=False)
    service_id: Mapped[UUID] = mapped_column(ForeignKey("services.id"), nullable=False)
    staff_id: Mapped[UUID | None] = mapped_column(ForeignKey("staff.id"), nullable=True)

    booking_date: Mapped[date] = mapped_column(Date, nullable=False)
    booking_time: Mapped[time] = mapped_column(Time, nullable=False)
    party_size: Mapped[int | None] = mapped_column(Integer, nullable=True)

    check_in_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    check_out_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    num_guests: Mapped[int | None] = mapped_column(Integer, nullable=True)
    num_nights: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    guest_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    guest_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    guest_phone: Mapped[str | None] = mapped_column(String(64), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[BookingStatusEnum] = mapped_column(
        Enum(BookingStatusEnum),
        nullable=False,
        default=BookingStatusEnum.pending,
    )
    google_event_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    booking_reference: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    special_requests: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    reminder_24h_job_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    reminder_1h_job_id: Mapped[str | None] = mapped_column(String(128), nullable=True)

    business: Mapped["Business"] = relationship("Business", back_populates="bookings")
    customer: Mapped["Customer"] = relationship("Customer", back_populates="bookings")
    service: Mapped["Service"] = relationship("Service", back_populates="bookings")
    staff: Mapped["Staff | None"] = relationship("Staff", back_populates="bookings")
