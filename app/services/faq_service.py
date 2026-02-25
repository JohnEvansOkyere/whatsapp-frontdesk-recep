"""FAQ retrieval and matching. Used to build AI system prompt and optionally direct reply."""
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession


async def get_faqs_for_business(session: AsyncSession, business_id: UUID) -> list[dict]:
    """Return list of {question, answer, keywords} for business. Used in system prompt."""
    # TODO: query faqs by business_id, return list of dicts
    return []
