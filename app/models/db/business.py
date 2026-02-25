"""Business (restaurant/hostel) model."""
import enum
from typing import TYPE_CHECKING, Any

from sqlalchemy import Boolean, Enum, Integer, String
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.db.base import Base, TimestampMixin, UUIDMixin


class BusinessTypeEnum(str, enum.Enum):
    restaurant = "restaurant"
    hostel = "hostel"


class ActiveChannelEnum(str, enum.Enum):
    telegram = "telegram"
    whatsapp = "whatsapp"


if TYPE_CHECKING:
    from app.models.db.booking import Booking
    from app.models.db.faq import FAQ
    from app.models.db.service import Service
    from app.models.db.staff import Staff
    from app.models.db.support_session import SupportSession


class Business(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "businesses"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[BusinessTypeEnum] = mapped_column(
        Enum(BusinessTypeEnum),
        nullable=False,
    )
    telegram_group_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    google_calendar_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    google_credentials: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    working_hours: Mapped[dict[str, list[str]]] = mapped_column(JSON, nullable=False)
    slot_duration_minutes: Mapped[int] = mapped_column(Integer, default=30)
    timezone: Mapped[str] = mapped_column(String(64), default="Africa/Accra")
    location: Mapped[str | None] = mapped_column(String(512), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(64), nullable=True)
    active_channel: Mapped[ActiveChannelEnum] = mapped_column(
        Enum(ActiveChannelEnum),
        default=ActiveChannelEnum.telegram,
    )
    whatsapp_config: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    services: Mapped[list["Service"]] = relationship("Service", back_populates="business")
    staff: Mapped[list["Staff"]] = relationship("Staff", back_populates="business")
    bookings: Mapped[list["Booking"]] = relationship("Booking", back_populates="business")
    faqs: Mapped[list["FAQ"]] = relationship("FAQ", back_populates="business")
    support_sessions: Mapped[list["SupportSession"]] = relationship(
        "SupportSession", back_populates="business"
    )
