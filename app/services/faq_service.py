"""FAQ retrieval and matching. Used to build AI system prompt and optionally direct reply."""
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db import FAQ


async def get_faqs_for_business(session: AsyncSession, business_id: UUID) -> list[dict]:
    """Return list of {question, answer, keywords} for business. Used in system prompt."""
    result = await session.execute(
        select(FAQ).where(FAQ.business_id == business_id).order_by(FAQ.question)
    )
    faqs = result.scalars().all()
    return [
        {
            "question": f.question,
            "answer": f.answer,
            "keywords": list(f.keywords) if f.keywords else [],
        }
        for f in faqs
    ]


async def add_faq(
    session: AsyncSession,
    business_id: UUID,
    question: str,
    answer: str,
    keywords: list[str] | None = None,
) -> dict:
    """Create one FAQ for a business. Returns {id, question, answer, keywords}."""
    faq = FAQ(
        business_id=business_id,
        question=question[:512],
        answer=answer,
        keywords=keywords or [],
    )
    session.add(faq)
    await session.flush()
    return {
        "id": str(faq.id),
        "question": faq.question,
        "answer": faq.answer,
        "keywords": list(faq.keywords) if faq.keywords else [],
    }


async def add_faqs_bulk(
    session: AsyncSession,
    business_id: UUID,
    items: list[dict],
) -> list[dict]:
    """Create multiple FAQs. Each item: {question, answer, keywords (optional)}. Returns list of created {id, question, answer, keywords}."""
    created = []
    for item in items:
        q = (item.get("question") or "").strip()
        a = (item.get("answer") or "").strip()
        if not q or not a:
            continue
        kw = item.get("keywords")
        if isinstance(kw, list):
            keywords = [str(k).strip() for k in kw if k]
        else:
            keywords = []
        faq = FAQ(
            business_id=business_id,
            question=q[:512],
            answer=a,
            keywords=keywords,
        )
        session.add(faq)
        await session.flush()
        created.append({
            "id": str(faq.id),
            "question": faq.question,
            "answer": faq.answer,
            "keywords": list(faq.keywords) if faq.keywords else [],
        })
    return created


async def delete_faq(session: AsyncSession, faq_id: UUID) -> bool:
    """Delete FAQ by id. Returns True if deleted."""
    result = await session.execute(select(FAQ).where(FAQ.id == faq_id).limit(1))
    faq = result.scalars().first()
    if not faq:
        return False
    await session.delete(faq)
    await session.flush()
    return True
