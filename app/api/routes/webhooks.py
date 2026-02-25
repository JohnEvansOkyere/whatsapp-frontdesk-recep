"""Telegram and WhatsApp webhook endpoints. No business logic — delegate to services."""
from fastapi import APIRouter, Request, Response

router = APIRouter(prefix="/webhook", tags=["webhooks"])


@router.post("/telegram")
async def telegram_webhook(request: Request) -> Response:
    """Receive Telegram updates. Body format: Telegram Update object. Delegate to message_handler."""
    # TODO: parse body, resolve business, get/create customer, call message_handler flow
    return Response(status_code=200)


@router.get("/whatsapp")
async def whatsapp_verify(request: Request) -> Response:
    """Meta verification challenge: echo hub.mode, hub.verify_token, hub.challenge."""
    # TODO: verify token from query params, return hub.challenge
    return Response(status_code=200)


@router.post("/whatsapp")
async def whatsapp_webhook(request: Request) -> Response:
    """Receive WhatsApp messages from Meta. Delegate to message_handler."""
    # TODO: parse body, resolve business from phone_number_id, get/create customer, call message_handler
    return Response(status_code=200)
