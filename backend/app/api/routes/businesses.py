"""Business management and slots. See CLAUDE FastAPI Endpoints."""
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db
from app.models.db import Business, Service
from app.models.db.business import BusinessTypeEnum
from app.models.schemas.business import (
    BusinessCreate,
    BusinessDetailResponse,
    BusinessResponse,
    BusinessUpdate,
)
from app.models.schemas.service import ServiceCreate, ServiceResponse

router = APIRouter(prefix="/api/businesses", tags=["businesses"])


@router.get("", response_model=list[BusinessResponse])
async def list_businesses(session: AsyncSession = Depends(get_db)) -> list[Business]:
    result = await session.execute(select(Business).order_by(Business.name))
    return list(result.scalars().all())


@router.post("", response_model=BusinessResponse)
async def create_business(
    body: BusinessCreate,
    session: AsyncSession = Depends(get_db),
) -> Business:
    try:
        business_type = BusinessTypeEnum(body.type)
    except ValueError:
        raise HTTPException(status_code=400, detail="type must be 'restaurant' or 'hostel'")
    business = Business(
        name=body.name,
        type=business_type,
        telegram_group_id=body.telegram_group_id,
        working_hours=body.working_hours,
        slot_duration_minutes=body.slot_duration_minutes,
        timezone=body.timezone,
        location=body.location,
        phone=body.phone,
        is_active=True,
    )
    session.add(business)
    await session.flush()
    return business


@router.get("/{business_id}", response_model=BusinessDetailResponse)
async def get_business(
    business_id: UUID,
    session: AsyncSession = Depends(get_db),
) -> Business:
    result = await session.execute(select(Business).where(Business.id == business_id).limit(1))
    business = result.scalars().first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    return business


@router.patch("/{business_id}", response_model=BusinessResponse)
async def update_business(
    business_id: UUID,
    body: BusinessUpdate,
    session: AsyncSession = Depends(get_db),
) -> Business:
    result = await session.execute(select(Business).where(Business.id == business_id).limit(1))
    business = result.scalars().first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    if body.name is not None:
        business.name = body.name
    if body.telegram_group_id is not None:
        business.telegram_group_id = body.telegram_group_id
    if body.working_hours is not None:
        business.working_hours = body.working_hours
    if body.slot_duration_minutes is not None:
        business.slot_duration_minutes = body.slot_duration_minutes
    if body.timezone is not None:
        business.timezone = body.timezone
    if body.location is not None:
        business.location = body.location
    if body.phone is not None:
        business.phone = body.phone
    await session.flush()
    return business


@router.get("/{business_id}/slots")
async def get_slots(
    business_id: UUID,
    date: str = Query(..., description="YYYY-MM-DD"),
    session: AsyncSession = Depends(get_db),
) -> dict:
    # TODO: call booking_service.get_available_slots (or equivalent) for date
    return {"slots": []}


@router.get("/{business_id}/services", response_model=list[ServiceResponse])
async def list_services(
    business_id: UUID,
    session: AsyncSession = Depends(get_db),
) -> list[Service]:
    result = await session.execute(
        select(Service).where(Service.business_id == business_id).order_by(Service.name)
    )
    return list(result.scalars().all())


@router.post("/{business_id}/services", response_model=ServiceResponse)
async def create_service(
    business_id: UUID,
    body: ServiceCreate,
    session: AsyncSession = Depends(get_db),
) -> Service:
    result = await session.execute(select(Business).where(Business.id == business_id).limit(1))
    if not result.scalars().first():
        raise HTTPException(status_code=404, detail="Business not found")
    price = body.price
    if price is not None and isinstance(price, float):
        price = Decimal(str(price))
    service = Service(
        business_id=business_id,
        name=body.name,
        description=body.description,
        duration_minutes=body.duration_minutes,
        price=price,
        capacity=body.capacity,
        is_active=True,
    )
    session.add(service)
    await session.flush()
    return service
