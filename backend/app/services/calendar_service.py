"""Google Calendar integration. create_event; OAuth via businesses.google_credentials."""
from uuid import UUID


async def create_event(
    business_id: UUID,
    service_name: str,
    customer_name: str,
    party_size: int | None,
    start_iso: str,
    end_iso: str,
    customer_phone: str,
    booking_reference: str,
    credentials: dict,
) -> str | None:
    """Create calendar event. Return google_event_id or None on failure."""
    # TODO: use google-api-python-client with credentials, insert event, return id
    return None
