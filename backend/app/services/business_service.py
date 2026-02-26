"""Business lookup. For dev: first active business; later map by bot/phone_number_id."""
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.db import Business


async def get_first_active_business(session: AsyncSession) -> Business | None:
    """Return the first active business (for single-tenant/dev). Later: resolve by bot token or whatsapp phone_number_id."""
    result = await session.execute(
        select(Business)
        .where(Business.is_active.is_(True))
        .options(selectinload(Business.services), selectinload(Business.faqs), selectinload(Business.staff))
        .limit(1)
    )
    return result.scalars().first()


async def get_business_by_id(session: AsyncSession, business_id: UUID) -> Business | None:
    """Load business with services, faqs, staff for prompt building."""
    result = await session.execute(
        select(Business)
        .where(Business.id == business_id, Business.is_active.is_(True))
        .options(selectinload(Business.services), selectinload(Business.faqs), selectinload(Business.staff))
        .limit(1)
    )
    return result.scalars().first()
