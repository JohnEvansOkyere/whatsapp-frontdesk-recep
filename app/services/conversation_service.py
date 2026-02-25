"""Conversation history: load last N messages, add message, trim to 20 per customer/business."""
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db import ConversationMessage
from app.models.db.conversation import MessageRoleEnum

HISTORY_LIMIT = 20


async def get_recent_messages(
    session: AsyncSession,
    customer_id: UUID,
    business_id: UUID,
    limit: int = HISTORY_LIMIT,
) -> list[dict[str, str]]:
    """Return last `limit` messages as list of {"role": "user"|"assistant", "content": str} in chronological order."""
    result = await session.execute(
        select(ConversationMessage)
        .where(
            ConversationMessage.customer_id == customer_id,
            ConversationMessage.business_id == business_id,
        )
        .order_by(ConversationMessage.created_at.desc())
        .limit(limit)
    )
    rows = list(result.scalars().all())
    rows.reverse()
    return [{"role": m.role.value, "content": m.content} for m in rows]


async def add_message(
    session: AsyncSession,
    customer_id: UUID,
    business_id: UUID,
    role: MessageRoleEnum,
    content: str,
) -> None:
    """Append one message to conversation_history."""
    msg = ConversationMessage(
        customer_id=customer_id,
        business_id=business_id,
        role=role,
        content=content,
    )
    session.add(msg)
    await session.flush()


async def trim_to_limit(
    session: AsyncSession,
    customer_id: UUID,
    business_id: UUID,
    limit: int = HISTORY_LIMIT,
) -> None:
    """Keep only the most recent `limit` messages; delete older ones."""
    # Subquery: ids of messages we want to keep (most recent `limit`)
    subq = (
        select(ConversationMessage.id)
        .where(
            ConversationMessage.customer_id == customer_id,
            ConversationMessage.business_id == business_id,
        )
        .order_by(ConversationMessage.created_at.desc())
        .limit(limit)
    )
    # Delete rows not in that set (same customer_id, business_id, id not in subq)
    await session.execute(
        delete(ConversationMessage).where(
            ConversationMessage.customer_id == customer_id,
            ConversationMessage.business_id == business_id,
            ConversationMessage.id.not_in(subq),
        )
    )
