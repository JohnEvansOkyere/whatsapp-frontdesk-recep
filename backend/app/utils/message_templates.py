"""All user-facing message strings. No hardcoded strings in handlers or services."""


def confirmation_body(
    business_name: str,
    service_name: str,
    party_size: int | None,
    formatted_date: str,
    time_str: str,
    price_str: str,
    requests_str: str,
) -> str:
    guests_line = f"\nGuests: {party_size}" if party_size is not None else ""
    return (
        f"Please confirm your reservation:\n\n"
        f"{business_name}\n"
        f"Room: {service_name}{guests_line}\n"
        f"Date: {formatted_date}\n"
        f"Time: {time_str}\n"
        f"Rate: {price_str}\n"
        f"Special requests: {requests_str}\n\n"
        f"[Confirm Booking] [Cancel]"
    )


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
    party_line = f"\nGuests: {size}" if size else ""
    return (
        f"New Reservation\n"
        f"Guest: {name} ({phone})\n"
        f"Room: {service}\n"
        f"Date: {date} at {time}{party_line}\n"
        f"Ref: {reference}\n"
        f"Requests: {requests or 'none'}"
    )


def support_request_notification(customer_name: str, last_message: str, customer_id: str) -> str:
    return (
        f"Support Request\n"
        f"From: {customer_name}\n"
        f"Last message: {last_message}\n"
        f"Reply: /reply {customer_id} {{your message}}\n"
        f"Close: /resolve {customer_id}"
    )


def support_connected_to_customer() -> str:
    return "You're now connected with our front desk team. Someone will reply shortly."


def support_resolved_to_customer() -> str:
    return "Glad we could help! Is there anything else you need?"


def reminder_24h(business_name: str, date: str, time: str, size: str, reference: str) -> str:
    return (
        f"Reminder: You have a reservation tomorrow!\n\n"
        f"{business_name}\n"
        f"{date} at {time}\n"
        f"Party of {size}\n"
        f"Ref: {reference}\n\n"
        f"Need to change anything? Just message us here."
    )


def reminder_1h(business_name: str) -> str:
    return f"Your reservation at {business_name} is in 1 hour. See you soon!"


def connecting_support() -> str:
    return "Connecting you with the front desk now. Someone will be with you shortly."
