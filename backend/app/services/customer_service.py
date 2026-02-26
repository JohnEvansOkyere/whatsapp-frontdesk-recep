"""Customer lookup and get-or-create. Handlers call this; no DB in handlers."""
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db import Customer


async def get_or_create_customer_by_telegram(
    session: AsyncSession,
    telegram_id: str,
    full_name: str | None = None,
) -> Customer:
    """Get existing customer by telegram_id or create one. Returns the customer."""
    result = await session.execute(
        select(Customer).where(Customer.telegram_id == telegram_id).limit(1)
    )
    customer = result.scalars().first()
    if customer is not None:
        if full_name and not customer.full_name:
            customer.full_name = full_name
        return customer
    customer = Customer(telegram_id=telegram_id, full_name=full_name)
    session.add(customer)
    await session.flush()
    return customer
