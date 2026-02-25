"""Business management and slots. See CLAUDE FastAPI Endpoints."""
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db
from app.models.schemas.business import BusinessCreate, BusinessResponse, BusinessUpdate

router = APIRouter(prefix="/api/businesses", tags=["businesses"])


@router.get("", response_model=list[BusinessResponse])
async def list_businesses(session: AsyncSession = Depends(get_db)) -> list:
    # TODO: query businesses, return list
    return []


@router.post("", response_model=BusinessResponse)
async def create_business(
    body: BusinessCreate,
    session: AsyncSession = Depends(get_db),
) -> dict:
    # TODO: create business from body
    return {}


@router.patch("/{business_id}", response_model=BusinessResponse)
async def update_business(
    business_id: UUID,
    body: BusinessUpdate,
    session: AsyncSession = Depends(get_db),
) -> dict:
    # TODO: load and update business
    return {}


@router.get("/{business_id}/slots")
async def get_slots(
    business_id: UUID,
    date: str = Query(..., description="YYYY-MM-DD"),
    session: AsyncSession = Depends(get_db),
) -> dict:
    # TODO: call booking_service.get_available_slots (or equivalent) for date
    return {"slots": []}
