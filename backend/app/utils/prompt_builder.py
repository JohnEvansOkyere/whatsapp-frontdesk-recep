"""Build AI system prompt from business data (CLAUDE.md). No hardcoded strings for user-facing copy."""
from typing import Any

# Business has: name, type, working_hours, location, phone, services (list), faqs (list), staff (list)


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
    """Single system prompt for the AI per CLAUDE.md."""
    loc = location or "Not specified"
    ph = phone or "Not specified"
    return f"""You are a friendly AI assistant for {business_name}, a {business_type}.
You help customers make reservations, answer questions, and connect with staff.

BUSINESS INFORMATION:
- Working hours: {working_hours}
- Location: {loc}
- Phone: {ph}
- Services/Options: {services_text}
- Staff: {staff_text}

FAQ KNOWLEDGE BASE:
{faq_text}

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
{booking_context}
"""


def format_services_for_prompt(services: list[Any]) -> str:
    """Turn list of Service models into text for prompt."""
    if not services:
        return "None listed"
    lines = []
    for s in services:
        price = f" — {s.price}" if getattr(s, "price", None) else ""
        cap = f" (up to {s.capacity} people)" if getattr(s, "capacity", None) else ""
        lines.append(f"- {s.name}{cap}{price}")
    return "\n".join(lines)


def format_staff_for_prompt(staff: list[Any]) -> str:
    """Turn list of Staff models into text for prompt."""
    if not staff:
        return "None listed"
    return ", ".join(f"{s.name}" + (f" ({s.role})" if getattr(s, "role", None) else "") for s in staff)


def format_faqs_for_prompt(faqs: list[Any]) -> str:
    """Turn list of FAQ models into Q&A text for prompt."""
    if not faqs:
        return "None"
    lines = []
    for f in faqs:
        q = getattr(f, "question", "")
        a = getattr(f, "answer", "")
        lines.append(f"Q: {q}\nA: {a}")
    return "\n\n".join(lines)


def booking_context_from_state(state: dict[str, Any] | None) -> str:
    """Format customer conversation_state for CURRENT BOOKING CONTEXT."""
    if not state:
        return "None"
    return str(state)
