"""Support session lookup. Handlers call this."""
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db import SupportSession as SupportSessionModel


async def get_active_support_session(
    session: AsyncSession,
    customer_id: UUID,
    business_id: UUID,
) -> SupportSessionModel | None:
    """Return active support session for this customer/business if any."""
    result = await session.execute(
        select(SupportSessionModel).where(
            SupportSessionModel.customer_id == customer_id,
            SupportSessionModel.business_id == business_id,
            SupportSessionModel.is_active.is_(True),
        ).limit(1)
    )
    return result.scalars().first()
