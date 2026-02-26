"""Google Calendar OAuth: connect-calendar, callback. See CLAUDE FastAPI Endpoints."""
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db

router = APIRouter(tags=["onboarding"])


@router.get("/api/businesses/{business_id}/connect-calendar")
async def connect_calendar(
    business_id: UUID,
    session: AsyncSession = Depends(get_db),
) -> dict:
    """Start OAuth flow; redirect to Google. Store state with business_id."""
    # TODO: build auth URL, redirect
    return {"message": "Redirect to Google OAuth"}


@router.get("/api/auth/google/callback")
async def google_callback(
    code: str | None = None,
    state: str | None = None,
    session: AsyncSession = Depends(get_db),
) -> dict:
    """Exchange code for tokens; store in business.google_credentials."""
    # TODO: exchange code, save credentials for business (from state)
    return {"message": "Calendar connected"}
