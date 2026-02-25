"""FAQ endpoints. See CLAUDE FastAPI Endpoints."""
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db

router = APIRouter(tags=["faqs"])


class FAQCreate(BaseModel):
    question: str
    answer: str
    keywords: list[str] = []


@router.post("/api/businesses/{business_id}/faqs")
async def add_faq(
    business_id: UUID,
    body: FAQCreate,
    session: AsyncSession = Depends(get_db),
) -> dict:
    # TODO: insert FAQ for business_id
    return {"message": "FAQ added"}


@router.get("/api/businesses/{business_id}/faqs")
async def list_faqs(
    business_id: UUID,
    session: AsyncSession = Depends(get_db),
) -> list:
    # TODO: query faqs by business_id
    return []


@router.delete("/api/faqs/{faq_id}")
async def delete_faq(
    faq_id: UUID,
    session: AsyncSession = Depends(get_db),
) -> dict:
    # TODO: delete FAQ by id
    return {"message": "FAQ deleted"}
