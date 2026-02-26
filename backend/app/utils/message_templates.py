"""All user-facing message strings. No hardcoded strings in handlers or services — use keys or format from here."""
from typing import Any


def confirmation_body(
    business_name: str,
    service_name: str,
    party_size: int | None,
    formatted_date: str,
    time_str: str,
    price_str: str,
    requests_str: str,
) -> str:
    """Booking confirmation text (see CLAUDE show_confirmation)."""
    party_line = f"👥 Party size: {party_size}" if party_size is not None else ""
    return f"""Please confirm your booking ✅

🏢 {business_name}
🍽️ {service_name}
{party_line}
📅 Date: {formatted_date}
⏰ Time: {time_str}
💰 Price: {price_str}
📝 Special requests: {requests_str}

[✅ Confirm Booking] [❌ Cancel]"""


def new_booking_notification(
    name: str,
    phone: str,
    service: str,
    date: str,
    time: str,
    size: str | None,
    reference: str,
    requests: str,
) -> str:
    """Notify business Telegram group of new booking (see CLAUDE on_booking_confirmed)."""
    party_line = f"Party: {size}" if size else ""
    return f"""📅 New Booking!
Customer: {name} ({phone})
Service: {service}
Date: {date} at {time}
{party_line}
Ref: {reference}
Special requests: {requests or 'none'}"""


def support_request_notification(customer_name: str, last_message: str, customer_id: str) -> str:
    """Notify group for support handoff (see CLAUDE initiate_handoff)."""
    return f"""💬 Support Request!
From: {customer_name}
Last message: {last_message}
Reply: /reply {customer_id} {{your message}}
Close: /resolve {customer_id}"""


def support_connected_to_customer() -> str:
    """Tell customer they are connected to staff."""
    return "You're connected! Our team will reply shortly 🙏"


def support_resolved_to_customer() -> str:
    """After staff closes with /resolve."""
    return "Glad we could help! Is there anything else? 😊"


def reminder_24h(business_name: str, date: str, time: str, size: str, reference: str) -> str:
    """24h before booking (see CLAUDE Reminders)."""
    return f"""⏰ Reminder: You have a reservation tomorrow!

🏢 {business_name}
📅 {date} at {time}
👥 Party of {size}
Ref: {reference}

Need to change anything? Just message us here!"""


def reminder_1h(business_name: str) -> str:
    """1h before booking."""
    return f"⏰ Your reservation is in 1 hour at {business_name}.\nSee you soon! 🎉"


def connecting_support() -> str:
    """When initiating human handoff."""
    return "Connecting you with our team now 💬\nSomeone will be with you shortly!"
