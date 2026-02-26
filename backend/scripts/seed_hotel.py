#!/usr/bin/env python3
"""Seed a hotel business with realistic Accra hotel data.

Usage (from backend/):
    python -m scripts.seed_hotel [business_id]

If business_id is omitted, the first business is used and converted to type=hotel.
"""
import asyncio
import os
import sys
from decimal import Decimal
from uuid import UUID

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
os.chdir(os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_maker as async_session
from app.models.db import Business, Service, FAQ
from app.models.db.business import BusinessTypeEnum


ROOM_TYPES = [
    {
        "name": "Standard Room",
        "description": "Comfortable room with modern amenities, perfect for business travelers. Features a work desk, complimentary WiFi, and a flat-screen TV.",
        "bed_type": "Queen",
        "max_occupancy": 2,
        "base_price_per_night": Decimal("450.00"),
        "room_count": 30,
        "amenities": ["WiFi", "TV", "Air Conditioning", "Safe", "Room Service"],
        "image_url": "https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=800",
    },
    {
        "name": "Deluxe Room",
        "description": "Spacious room with city views, premium bedding, and an upgraded bathroom with rain shower. Includes complimentary breakfast.",
        "bed_type": "King",
        "max_occupancy": 2,
        "base_price_per_night": Decimal("750.00"),
        "room_count": 20,
        "amenities": ["WiFi", "TV", "Air Conditioning", "Mini Bar", "Safe", "Room Service", "Breakfast", "City View"],
        "image_url": "https://images.unsplash.com/photo-1590490360182-c33d57733427?w=800",
    },
    {
        "name": "Executive Suite",
        "description": "Elegant suite with a separate living area, dining space, and panoramic views of Accra. Includes executive lounge access and airport shuttle.",
        "bed_type": "King",
        "max_occupancy": 3,
        "base_price_per_night": Decimal("1200.00"),
        "room_count": 10,
        "amenities": ["WiFi", "TV", "Air Conditioning", "Mini Bar", "Safe", "Room Service", "Breakfast", "City View", "Balcony", "Spa Access", "Airport Shuttle", "Laundry"],
        "image_url": "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=800",
    },
    {
        "name": "Family Room",
        "description": "Perfect for families, featuring two double beds, extra space, and a children-friendly setup. Complimentary breakfast for all guests.",
        "bed_type": "Double",
        "max_occupancy": 4,
        "base_price_per_night": Decimal("900.00"),
        "room_count": 15,
        "amenities": ["WiFi", "TV", "Air Conditioning", "Safe", "Room Service", "Breakfast", "Parking"],
        "image_url": "https://images.unsplash.com/photo-1596394516093-501ba68a0ba6?w=800",
    },
    {
        "name": "Presidential Suite",
        "description": "The pinnacle of luxury. Private terrace, jacuzzi, personal butler service, and breathtaking views of the Gulf of Guinea. For the most discerning guests.",
        "bed_type": "King",
        "max_occupancy": 4,
        "base_price_per_night": Decimal("3500.00"),
        "room_count": 2,
        "amenities": ["WiFi", "TV", "Air Conditioning", "Mini Bar", "Safe", "Room Service", "Breakfast", "Sea View", "Balcony", "Spa Access", "Airport Shuttle", "Laundry", "Gym", "Pool", "Parking"],
        "image_url": "https://images.unsplash.com/photo-1578683010236-d716f9a3f461?w=800",
    },
    {
        "name": "Twin Room",
        "description": "Ideal for colleagues or friends traveling together. Two single beds with all standard amenities and a comfortable workspace.",
        "bed_type": "Twin",
        "max_occupancy": 2,
        "base_price_per_night": Decimal("500.00"),
        "room_count": 15,
        "amenities": ["WiFi", "TV", "Air Conditioning", "Safe", "Room Service"],
        "image_url": "https://images.unsplash.com/photo-1595576508898-0ad5c879a061?w=800",
    },
]

HOTEL_FAQS = [
    {
        "question": "What are the check-in and check-out times?",
        "answer": "Check-in is from 2:00 PM and check-out is by 12:00 PM (noon). Early check-in and late check-out may be available upon request, subject to availability. Please contact the front desk.",
        "keywords": ["check-in", "check-out", "time"],
    },
    {
        "question": "Is breakfast included in the room rate?",
        "answer": "Complimentary breakfast is included with Deluxe Room, Executive Suite, Family Room, and Presidential Suite bookings. Standard and Twin Room guests can add breakfast for GHS 85 per person per day.",
        "keywords": ["breakfast", "included", "meal"],
    },
    {
        "question": "Do you have airport shuttle service?",
        "answer": "Yes, we offer airport shuttle service from Kotoka International Airport. It is complimentary for Executive Suite and Presidential Suite guests. For other room types, the shuttle is available for GHS 150 per trip. Please book at least 24 hours in advance.",
        "keywords": ["airport", "shuttle", "transfer", "pickup"],
    },
    {
        "question": "Is there a swimming pool?",
        "answer": "Yes, we have an outdoor infinity pool with a poolside bar, open daily from 7:00 AM to 9:00 PM. Pool towels are provided complimentary.",
        "keywords": ["pool", "swimming", "swim"],
    },
    {
        "question": "Do you have a gym or fitness center?",
        "answer": "Our fully equipped fitness center is open 24 hours for all hotel guests. It features cardio machines, free weights, and yoga mats.",
        "keywords": ["gym", "fitness", "exercise", "workout"],
    },
    {
        "question": "Is WiFi available?",
        "answer": "Complimentary high-speed WiFi is available throughout the hotel, including all rooms, the lobby, restaurant, and pool area.",
        "keywords": ["wifi", "internet", "connection"],
    },
    {
        "question": "Do you have parking?",
        "answer": "Yes, we offer complimentary on-site parking for hotel guests. Valet parking is also available for GHS 50 per day.",
        "keywords": ["parking", "car", "valet"],
    },
    {
        "question": "What is your cancellation policy?",
        "answer": "Free cancellation up to 48 hours before check-in. Cancellations within 48 hours will be charged one night's rate. No-shows will be charged the full booking amount.",
        "keywords": ["cancel", "cancellation", "refund", "policy"],
    },
    {
        "question": "Do you have a restaurant?",
        "answer": "Yes, our on-site restaurant serves local Ghanaian and international cuisine. Breakfast is served 6:30 AM - 10:30 AM, lunch 12:00 PM - 3:00 PM, and dinner 6:30 PM - 10:30 PM. Room service is available 24 hours.",
        "keywords": ["restaurant", "food", "dining", "eat", "menu"],
    },
    {
        "question": "Do you have a spa?",
        "answer": "Our wellness spa offers a range of treatments including massages, facials, and body treatments. Spa access is complimentary for Executive Suite and Presidential Suite guests. Other guests can book treatments starting from GHS 200.",
        "keywords": ["spa", "massage", "wellness", "treatment"],
    },
    {
        "question": "Can I host events or meetings at the hotel?",
        "answer": "Yes, we have conference rooms and event spaces that can accommodate 10 to 300 guests. Our events team can help plan corporate meetings, weddings, and private events. Please contact us for details and pricing.",
        "keywords": ["event", "meeting", "conference", "wedding", "venue"],
    },
    {
        "question": "Where is the hotel located?",
        "answer": "We are located in the heart of Accra, on the prestigious Oxford Street in Osu, just 20 minutes from Kotoka International Airport and close to major business and entertainment districts.",
        "keywords": ["location", "address", "where", "directions"],
    },
]


async def seed(session: AsyncSession, business_id: UUID | None = None) -> None:
    if business_id:
        result = await session.execute(select(Business).where(Business.id == business_id).limit(1))
    else:
        result = await session.execute(select(Business).limit(1))
    business = result.scalars().first()
    if not business:
        print("No business found. Create one first via the dashboard.")
        return

    # Update business to hotel type with proper details
    business.type = BusinessTypeEnum.hotel
    business.name = business.name if business.name != "JEOCO" else "Golden Tulip Accra"
    business.location = business.location or "Oxford Street, Osu, Accra, Ghana"
    business.phone = business.phone or "+233 30 274 5555"
    business.working_hours = {
        "mon": ["00:00", "23:59"], "tue": ["00:00", "23:59"],
        "wed": ["00:00", "23:59"], "thu": ["00:00", "23:59"],
        "fri": ["00:00", "23:59"], "sat": ["00:00", "23:59"],
        "sun": ["00:00", "23:59"],
    }

    # Remove existing services for this business
    existing_services = await session.execute(
        select(Service).where(Service.business_id == business.id)
    )
    for svc in existing_services.scalars().all():
        await session.delete(svc)
    await session.flush()

    # Add room types
    for rt in ROOM_TYPES:
        service = Service(
            business_id=business.id,
            name=rt["name"],
            description=rt["description"],
            duration_minutes=60,
            price=rt["base_price_per_night"],
            capacity=rt["max_occupancy"],
            is_active=True,
            image_url=rt["image_url"],
            max_occupancy=rt["max_occupancy"],
            bed_type=rt["bed_type"],
            amenities=rt["amenities"],
            base_price_per_night=rt["base_price_per_night"],
            room_count=rt["room_count"],
        )
        session.add(service)
    print(f"  Added {len(ROOM_TYPES)} room types")

    # Remove existing FAQs and add hotel FAQs
    existing_faqs = await session.execute(
        select(FAQ).where(FAQ.business_id == business.id)
    )
    for faq in existing_faqs.scalars().all():
        await session.delete(faq)
    await session.flush()

    for fq in HOTEL_FAQS:
        faq = FAQ(
            business_id=business.id,
            question=fq["question"],
            answer=fq["answer"],
            keywords=fq["keywords"],
        )
        session.add(faq)
    print(f"  Added {len(HOTEL_FAQS)} FAQs")

    await session.flush()
    print(f"  Business '{business.name}' updated to hotel type")
    print("  Done!")


async def main() -> None:
    bid = UUID(sys.argv[1]) if len(sys.argv) > 1 else None
    async with async_session() as session:
        await seed(session, bid)
        await session.commit()


if __name__ == "__main__":
    asyncio.run(main())
