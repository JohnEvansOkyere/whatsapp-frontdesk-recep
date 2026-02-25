"""Human handoff: initiate_handoff, forward messages, /reply, /resolve. See CLAUDE Support Handoff."""
from uuid import UUID

from app.channels.base import BaseChannel
from app.utils.message_templates import support_connected_to_customer, support_request_notification


async def initiate_handoff(
    channel: BaseChannel,
    recipient_id: str,
    group_id: str,
    customer_id: UUID,
    customer_name: str,
    last_message: str,
) -> None:
    """Create support_session in DB, notify group, tell customer they're connected."""
    # TODO: create support_session, then:
    await channel.forward_to_group(
        group_id,
        support_request_notification(customer_name, last_message, str(customer_id)),
    )
    await channel.send_message(recipient_id, support_connected_to_customer())
