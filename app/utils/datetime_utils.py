"""Slot generation and date parsing. Used by booking_service for available slots."""
from datetime import date, datetime, time, timedelta
from typing import Any

# Day name keys used in business.working_hours (e.g. "mon", "tue")
WEEKDAY_KEYS = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")


def weekday_key(d: date) -> str:
    """Return working_hours key for a date (mon..sun)."""
    # Monday=0 in isoweekday: mon=1..sun=7
    idx = d.isoweekday() - 1
    return WEEKDAY_KEYS[idx]


def parse_date_from_user(text: str) -> date | None:
    """Parse a date from user input (e.g. 'tonight', 'tomorrow', '2025-03-01'). Returns None if unparseable."""
    # Stub: implement with a small set of keywords and strptime. Do not assume locale.
    return None


def generate_slots_for_day(
    day: date,
    start_time: str,
    end_time: str,
    slot_duration_minutes: int,
) -> list[time]:
    """
    Generate all slot start times for one day between start_time and end_time.
    start_time/end_time are "HH:MM" or "HH:MM:SS". Excludes the slot that would extend past end_time.
    """
    # Stub: parse start_time/end_time, loop by slot_duration_minutes, append to list.
    return []


def slot_taken(slot_time: time, slot_duration_minutes: int, booked_slots: list[dict[str, Any]]) -> bool:
    """
    Return True if slot_time is overlapping with any booked slot.
    booked_slots: list of dicts with 'start' and 'end' time or datetime.
    """
    return False
