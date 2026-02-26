"""Support session model."""
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.db.base import Base, UUIDMixin

if TYPE_CHECKING:
    from app.models.db.business import Business
    from app.models.db.customer import Customer


class SupportSession(Base, UUIDMixin):
    __tablename__ = "support_sessions"

    customer_id: Mapped[UUID] = mapped_column(ForeignKey("customers.id"), nullable=False)
    business_id: Mapped[UUID] = mapped_column(ForeignKey("businesses.id"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    customer: Mapped["Customer"] = relationship("Customer", back_populates="support_sessions")
    business: Mapped["Business"] = relationship("Business", back_populates="support_sessions")
