"""Business, service, and slot endpoints."""
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.dependencies import get_db
from app.models.db import Booking, Business, Service
from app.models.db.business import BusinessTypeEnum
from app.services import booking_service
from app.models.schemas.business import (
    BusinessCreate,
    BusinessDetailResponse,
    BusinessResponse,
    BusinessUpdate,
)
from app.models.schemas.service import ServiceCreate, ServiceResponse, ServiceUpdate

router = APIRouter(prefix="/api/businesses", tags=["businesses"])


def _to_decimal(val: Decimal | float | None) -> Decimal | None:
    if val is None:
        return None
    return Decimal(str(val)) if isinstance(val, float) else val


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
        raise HTTPException(status_code=400, detail="type must be 'restaurant', 'hostel', or 'hotel'")
    business = Business(
        name=body.name,
        type=business_type,
        telegram_bot_token=body.telegram_bot_token,
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
    update_data = body.model_dump(exclude_unset=True)
    if "type" in update_data:
        try:
            update_data["type"] = BusinessTypeEnum(update_data["type"])
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid type")
    for field, value in update_data.items():
        setattr(business, field, value)
    await session.flush()
    return business


@router.get("/{business_id}/slots")
async def get_slots(
    business_id: UUID,
    date: str = Query(..., description="YYYY-MM-DD"),
    service_id: UUID | None = Query(None),
    session: AsyncSession = Depends(get_db),
) -> dict:
    result = await session.execute(
        select(Business)
        .where(Business.id == business_id)
        .options(selectinload(Business.services))
        .limit(1)
    )
    business = result.scalars().first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    sid = service_id
    if not sid and business.services:
        sid = business.services[0].id
    if not sid:
        return {"slots": [], "service_id": None}
    slots = await booking_service.get_available_slots(session, business_id, sid, date)
    return {"slots": [{"label": s["label"], "time": s["time"]} for s in slots], "service_id": str(sid)}


# ── Services / Room Types ───────────────────────────────────────────────

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
    service = Service(
        business_id=business_id,
        name=body.name,
        description=body.description,
        duration_minutes=body.duration_minutes,
        price=_to_decimal(body.price),
        capacity=body.capacity,
        is_active=True,
        image_url=body.image_url,
        max_occupancy=body.max_occupancy,
        bed_type=body.bed_type,
        amenities=body.amenities,
        base_price_per_night=_to_decimal(body.base_price_per_night),
        room_count=body.room_count,
    )
    session.add(service)
    await session.flush()
    return service


@router.patch("/{business_id}/services/{service_id}", response_model=ServiceResponse)
async def update_service(
    business_id: UUID,
    service_id: UUID,
    body: ServiceUpdate,
    session: AsyncSession = Depends(get_db),
) -> Service:
    result = await session.execute(
        select(Service).where(Service.id == service_id, Service.business_id == business_id).limit(1)
    )
    service = result.scalars().first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    update_data = body.model_dump(exclude_unset=True)
    for field in ("price", "base_price_per_night"):
        if field in update_data:
            update_data[field] = _to_decimal(update_data[field])
    for field, value in update_data.items():
        setattr(service, field, value)
    await session.flush()
    return service


@router.delete("/{business_id}/services/{service_id}")
async def delete_service(
    business_id: UUID,
    service_id: UUID,
    session: AsyncSession = Depends(get_db),
) -> dict:
    result = await session.execute(
        select(Service).where(Service.id == service_id, Service.business_id == business_id).limit(1)
    )
    service = result.scalars().first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    await session.delete(service)
    await session.flush()
    return {"message": "deleted"}


# ── Bookings for a business ─────────────────────────────────────────────

@router.get("/{business_id}/bookings")
async def list_business_bookings(
    business_id: UUID,
    status: str | None = Query(None),
    session: AsyncSession = Depends(get_db),
) -> list[dict]:
    q = (
        select(Booking)
        .where(Booking.business_id == business_id)
        .options(selectinload(Booking.service), selectinload(Booking.customer))
        .order_by(Booking.created_at.desc())
    )
    if status:
        q = q.where(Booking.status == status)
    result = await session.execute(q)
    bookings = result.scalars().all()
    return [
        {
            "id": str(b.id),
            "booking_reference": b.booking_reference,
            "booking_date": b.booking_date.isoformat(),
            "booking_time": b.booking_time.isoformat() if b.booking_time else None,
            "check_in_date": b.check_in_date.isoformat() if b.check_in_date else None,
            "check_out_date": b.check_out_date.isoformat() if b.check_out_date else None,
            "num_guests": b.num_guests,
            "num_nights": b.num_nights,
            "total_price": str(b.total_price) if b.total_price else None,
            "guest_name": b.guest_name or (b.customer.full_name if b.customer else None),
            "guest_phone": b.guest_phone or (b.customer.phone_number if b.customer else None),
            "party_size": b.party_size,
            "status": b.status.value,
            "service_name": b.service.name if b.service else None,
            "special_requests": b.special_requests,
            "notes": b.notes,
            "created_at": b.created_at.isoformat() if b.created_at else None,
        }
        for b in bookings
    ]
