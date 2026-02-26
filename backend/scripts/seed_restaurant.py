"""
Seed a restaurant business with realistic services and FAQs.
Run from backend directory: python -m scripts.seed_restaurant
Uses the first restaurant business in the DB, or the first business if none is type=restaurant.
"""
import asyncio
import os
import sys
from uuid import UUID

# Ensure backend is on path and .env is loaded from backend/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_maker
from app.models.db import Business, Service
from app.models.db.business import BusinessTypeEnum
from app.services import faq_service


RESTAURANT_SERVICES = [
    {
        "name": "Table for 2",
        "description": "Intimate table for two. Perfect for a quiet dinner or lunch.",
        "duration_minutes": 90,
        "price": None,
        "capacity": 2,
    },
    {
        "name": "Table for 4",
        "description": "Table for four guests. Ideal for small groups and families.",
        "duration_minutes": 90,
        "price": None,
        "capacity": 4,
    },
    {
        "name": "Table for 6",
        "description": "Spacious table for six. Great for celebrations or group dinners.",
        "duration_minutes": 120,
        "price": None,
        "capacity": 6,
    },
    {
        "name": "Private dining",
        "description": "Private room for up to 12 guests. Minimum spend may apply; ideal for events.",
        "duration_minutes": 180,
        "price": None,
        "capacity": 12,
    },
]

RESTAURANT_FAQS = [
    {
        "question": "What are your opening hours?",
        "answer": "We are open Tuesday to Sunday. Lunch: 12:00 to 15:00. Dinner: 18:00 to 22:00. We are closed on Mondays.",
        "keywords": ["hours", "opening", "close", "time", "when"],
    },
    {
        "question": "Where are you located?",
        "answer": "We are at 12 Osu Avenue, Accra, near the Oxford Street junction. Look for our sign next to the blue gate.",
        "keywords": ["address", "location", "find", "directions", "where"],
    },
    {
        "question": "Do you take reservations?",
        "answer": "Yes. You can book a table through this chat, by phone, or via our website. We recommend reserving for weekend dinners.",
        "keywords": ["reservation", "book", "table", "reserve"],
    },
    {
        "question": "Is there parking?",
        "answer": "Yes. We have a small private lot; street parking is also available nearby. We can reserve a spot for guests with limited mobility if you let us know in advance.",
        "keywords": ["parking", "car", "park"],
    },
    {
        "question": "Do you have vegetarian or vegan options?",
        "answer": "Yes. We have several vegetarian dishes and can adapt many plates to be vegan. Tell your server or mention it when you book.",
        "keywords": ["vegetarian", "vegan", "plant-based", "diet"],
    },
    {
        "question": "Can you accommodate allergies or dietary restrictions?",
        "answer": "Yes. Please tell us when you book or when you arrive. Our kitchen can avoid nuts, gluten, dairy, and other allergens where possible.",
        "keywords": ["allergy", "gluten", "nuts", "dairy", "dietary", "halal", "kosher"],
    },
    {
        "question": "What payment methods do you accept?",
        "answer": "We accept cash (GHS), mobile money (MTN and Vodafone), and major credit and debit cards.",
        "keywords": ["payment", "pay", "card", "cash", "mobile money"],
    },
    {
        "question": "Is there a dress code?",
        "answer": "Smart casual. We ask that guests avoid sportswear and flip-flops in the evening. Shorts and sandals are fine at lunch.",
        "keywords": ["dress", "code", "clothing", "attire"],
    },
    {
        "question": "Do you do private events or large groups?",
        "answer": "Yes. We have a private dining room for up to 12 guests and can arrange set menus and drinks for groups. Contact us to discuss dates and options.",
        "keywords": ["private", "event", "party", "group", "celebration", "birthday"],
    },
    {
        "question": "Can I bring my children?",
        "answer": "Yes, children are welcome. We have high chairs and a short kids’ menu. For dinner after 19:00 we’d suggest older children, as the room is quieter.",
        "keywords": ["children", "kids", "family", "child"],
    },
    {
        "question": "Do you have WiFi?",
        "answer": "Yes. Free WiFi is available for guests. Ask your server for the password.",
        "keywords": ["wifi", "internet", "wi-fi"],
    },
]


async def seed_restaurant(business_id: UUID | None = None) -> None:
    async with async_session_maker() as session:
        business = await _get_business(session, business_id)
        if not business:
            print("No business found. Create one in the dashboard or via API first.")
            return

        print(f"Seeding restaurant: {business.name} (id: {business.id})")

        # Services
        existing_services = await _get_services(session, business.id)
        if existing_services:
            print(f"  Skipping services: {len(existing_services)} already exist.")
        else:
            for s in RESTAURANT_SERVICES:
                service = Service(
                    business_id=business.id,
                    name=s["name"],
                    description=s.get("description"),
                    duration_minutes=s["duration_minutes"],
                    price=s.get("price"),
                    capacity=s.get("capacity"),
                    is_active=True,
                )
                session.add(service)
            await session.flush()
            print(f"  Added {len(RESTAURANT_SERVICES)} services (table types).")

        # FAQs
        existing_faqs = await _count_faqs(session, business.id)
        if existing_faqs > 0:
            print(f"  Skipping FAQs: {existing_faqs} already exist.")
        else:
            await faq_service.add_faqs_bulk(session, business.id, RESTAURANT_FAQS)
            print(f"  Added {len(RESTAURANT_FAQS)} FAQs.")

        # Optional: set realistic working hours and location if not already set
        if not business.location or business.location.strip() == "":
            business.location = "12 Osu Avenue, Accra (near Oxford Street)"
            business.phone = business.phone or "+233 24 123 4567"
            # One [open, close] pair per day; slot logic uses first two. Tue–Sun 12:00–22:00.
            business.working_hours = {
                "mon": [],  # closed
                "tue": ["12:00", "22:00"],
                "wed": ["12:00", "22:00"],
                "thu": ["12:00", "22:00"],
                "fri": ["12:00", "22:00"],
                "sat": ["12:00", "22:00"],
                "sun": ["12:00", "22:00"],
            }
            await session.flush()
            print("  Updated business: location, phone, working hours (Tue–Sun 12:00–22:00).")

        await session.commit()
    print("Done.")


async def _get_business(session: AsyncSession, business_id: UUID | None) -> Business | None:
    if business_id:
        r = await session.execute(select(Business).where(Business.id == business_id).limit(1))
        return r.scalar_one_or_none()
    r = await session.execute(
        select(Business).where(Business.type == BusinessTypeEnum.restaurant).order_by(Business.name).limit(1)
    )
    business = r.scalar_one_or_none()
    if business:
        return business
    r = await session.execute(select(Business).order_by(Business.name).limit(1))
    return r.scalar_one_or_none()


async def _get_services(session: AsyncSession, business_id: UUID) -> list[Service]:
    r = await session.execute(select(Service).where(Service.business_id == business_id))
    return list(r.scalars().all())


async def _count_faqs(session: AsyncSession, business_id: UUID) -> int:
    from app.models.db.faq import FAQ
    r = await session.execute(select(FAQ).where(FAQ.business_id == business_id))
    return len(r.scalars().all())


def main() -> None:
    import argparse
    p = argparse.ArgumentParser(description="Seed a restaurant with services and FAQs")
    p.add_argument("--business-id", type=str, help="UUID of the business (default: first restaurant)")
    args = p.parse_args()
    bid = UUID(args.business_id) if args.business_id else None
    asyncio.run(seed_restaurant(bid))


if __name__ == "__main__":
    main()
