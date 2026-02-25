"""Conversation history model — last 20 messages per customer per business."""
import enum
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Enum, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.db.customer import Customer


class MessageRoleEnum(str, enum.Enum):
    user = "user"
    assistant = "assistant"


class ConversationMessage(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "conversation_history"

    customer_id: Mapped[UUID] = mapped_column(ForeignKey("customers.id"), nullable=False)
    business_id: Mapped[UUID] = mapped_column(ForeignKey("businesses.id"), nullable=False)
    role: Mapped[MessageRoleEnum] = mapped_column(Enum(MessageRoleEnum), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    customer: Mapped["Customer"] = relationship("Customer", back_populates="conversation_history")
