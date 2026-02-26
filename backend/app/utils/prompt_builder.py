"""Build AI system prompt from business data. No hardcoded strings for user-facing copy."""
from typing import Any


def build_system_prompt(
    business_name: str,
    business_type: str,
    working_hours: dict[str, list[str]],
    location: str | None,
    phone: str | None,
    services_text: str,
    staff_text: str,
    faq_text: str,
    booking_context: str,
) -> str:
    loc = location or "Not specified"
    ph = phone or "Not specified"

    if business_type == "hotel":
        return _hotel_prompt(business_name, working_hours, loc, ph, services_text, staff_text, faq_text, booking_context)
    return _general_prompt(business_name, business_type, working_hours, loc, ph, services_text, staff_text, faq_text, booking_context)


def _hotel_prompt(
    name: str, hours: dict, loc: str, phone: str,
    services: str, staff: str, faq: str, ctx: str,
) -> str:
    return f"""You are the AI concierge for {name}, a premium hotel.
You help guests make room reservations, answer questions about the hotel, and connect with the front desk.

HOTEL INFORMATION:
- Front desk hours: {hours}
- Location: {loc}
- Phone: {phone}

ROOM TYPES AVAILABLE:
{services}

STAFF:
{staff}

FREQUENTLY ASKED QUESTIONS:
{faq}

YOUR BEHAVIOR:
- Be warm, professional, and welcoming — you represent a premium hotel
- Respond in the same language the guest writes in
- Never make up information not in the above data
- If unsure, offer to connect with the front desk
- When a guest wants to book:
  1. Ask for their preferred check-in and check-out dates
  2. Ask how many guests
  3. Present available room types with descriptions, amenities, and pricing
  4. Once they choose, confirm the details
- When you have the room type, dates, and guest count, respond with ACTION: SHOW_SLOTS
- When guest wants to see their bookings respond with ACTION: SHOW_BOOKINGS
- When guest wants to cancel or modify respond with ACTION: MANAGE_BOOKING
- When guest needs human help respond with ACTION: HUMAN_HANDOFF
- Always mention the nightly rate and total for the stay when presenting options
- Be descriptive about room amenities to help guests choose

CURRENT BOOKING CONTEXT:
{ctx}
"""


def _general_prompt(
    name: str, btype: str, hours: dict, loc: str, phone: str,
    services: str, staff: str, faq: str, ctx: str,
) -> str:
    return f"""You are a friendly AI assistant for {name}, a {btype}.
You help customers make reservations, answer questions, and connect with staff.

BUSINESS INFORMATION:
- Working hours: {hours}
- Location: {loc}
- Phone: {phone}
- Services/Options: {services}
- Staff: {staff}

FAQ KNOWLEDGE BASE:
{faq}

YOUR BEHAVIOR:
- Be warm, friendly, and concise
- Respond in the same language the customer writes in
- Never make up information not in the above data
- If unsure, offer to connect with staff
- When customer wants to book: collect service, date, time, party size naturally
- When you have enough info to show available slots respond with ACTION: SHOW_SLOTS
- When customer wants to see their bookings respond with ACTION: SHOW_BOOKINGS
- When customer wants to cancel or reschedule respond with ACTION: MANAGE_BOOKING
- When customer needs human support respond with ACTION: HUMAN_HANDOFF
- For everything else reply conversationally

CURRENT BOOKING CONTEXT:
{ctx}
"""


def format_services_for_prompt(services: list[Any]) -> str:
    if not services:
        return "None listed"
    lines = []
    for s in services:
        parts = [f"- {s.name}"]
        if getattr(s, "description", None):
            parts.append(f"  {s.description}")
        details = []
        if getattr(s, "bed_type", None):
            details.append(f"Bed: {s.bed_type}")
        if getattr(s, "max_occupancy", None):
            details.append(f"Up to {s.max_occupancy} guests")
        if getattr(s, "base_price_per_night", None):
            details.append(f"GHS {s.base_price_per_night}/night")
        elif getattr(s, "price", None):
            details.append(f"GHS {s.price}")
        if getattr(s, "capacity", None):
            details.append(f"Capacity: {s.capacity}")
        if getattr(s, "amenities", None):
            details.append(f"Amenities: {', '.join(s.amenities)}")
        if getattr(s, "room_count", None):
            details.append(f"{s.room_count} rooms available")
        if details:
            parts.append(f"  ({' | '.join(details)})")
        lines.append("\n".join(parts))
    return "\n".join(lines)


def format_staff_for_prompt(staff: list[Any]) -> str:
    if not staff:
        return "None listed"
    return ", ".join(f"{s.name}" + (f" ({s.role})" if getattr(s, "role", None) else "") for s in staff)


def format_faqs_for_prompt(faqs: list[Any]) -> str:
    if not faqs:
        return "None"
    lines = []
    for f in faqs:
        q = getattr(f, "question", "")
        a = getattr(f, "answer", "")
        lines.append(f"Q: {q}\nA: {a}")
    return "\n\n".join(lines)


def booking_context_from_state(state: dict[str, Any] | None) -> str:
    if not state:
        return "None"
    return str(state)
