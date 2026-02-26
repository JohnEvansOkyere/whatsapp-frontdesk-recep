"""Buttons and inline keyboards. Return channel-agnostic structures; channel layer maps to Telegram/WhatsApp format."""
from typing import Any


def slot_buttons(slots: list[dict[str, Any]], page: int = 0, per_page: int = 8) -> list[dict[str, Any]]:
    """Build list of slot buttons (max per_page). Include 'Different date' and 'More slots' as needed."""
    start = page * per_page
    chunk = slots[start : start + per_page]
    buttons = [
        {"label": s.get("label", str(s)), "action": s.get("time", s.get("label", "")), "payload": s}
        for s in chunk
    ]
    if start + per_page < len(slots):
        buttons.append({"label": "⬅ More slots", "action": "more_slots", "page": page + 1})
    buttons.append({"label": "📅 Different date", "action": "different_date"})
    return buttons


def confirm_booking_buttons() -> list[dict[str, Any]]:
    """Confirm / Cancel for booking confirmation."""
    return [
        {"label": "✅ Confirm Booking", "action": "confirm_booking"},
        {"label": "❌ Cancel", "action": "cancel_booking"},
    ]
