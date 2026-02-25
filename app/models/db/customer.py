"""Customer model."""
from typing import TYPE_CHECKING, Any

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.db.booking import Booking
    from app.models.db.conversation import ConversationMessage
    from app.models.db.support_session import SupportSession


class Customer(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "customers"

    telegram_id: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True)
    whatsapp_number: Mapped[str | None] = mapped_column(String(32), unique=True, nullable=True)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone_number: Mapped[str | None] = mapped_column(String(32), nullable=True)
    conversation_state: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    bookings: Mapped[list["Booking"]] = relationship("Booking", back_populates="customer")
    conversation_history: Mapped[list["ConversationMessage"]] = relationship(
        "ConversationMessage", back_populates="customer"
    )
    support_sessions: Mapped[list["SupportSession"]] = relationship(
        "SupportSession", back_populates="customer"
    )
