"""Telegram and WhatsApp webhook endpoints. No business logic — delegate to bot/services."""
from typing import Any, Dict
from uuid import UUID

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db
from app.bot.telegram_entry import handle_telegram_update

router = APIRouter(prefix="/webhook", tags=["webhooks"])


@router.post("/telegram/{business_id}")
async def telegram_webhook(
    business_id: UUID,
    request: Request,
    session: AsyncSession = Depends(get_db),
) -> Response:
    """Receive Telegram updates for a specific business. Body: Telegram Update object."""

    update: Dict[str, Any] = await request.json()
    # Orchestrate using the business identified in the path.
    await handle_telegram_update(update, session, business_id)
    return Response(status_code=200)


@router.get("/whatsapp")
async def whatsapp_verify(request: Request) -> Response:
    """Meta verification challenge: echo hub.mode, hub.verify_token, hub.challenge."""
    # TODO: verify token from query params, return hub.challenge
    return Response(status_code=200)


@router.post("/whatsapp")
async def whatsapp_webhook(
    request: Request,
    session: AsyncSession = Depends(get_db),
) -> Response:
    """Receive WhatsApp messages from Meta. Delegate to message_handler."""
    # TODO: parse body, resolve business from phone_number_id, get/create customer, call message_handler
    _ = await request.json()
    return Response(status_code=200)
