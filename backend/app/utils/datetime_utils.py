"""Slot generation and date parsing. Used by booking_service for available slots."""
from datetime import date, datetime, time, timedelta
from typing import Any

# Day name keys used in business.working_hours (e.g. "mon", "tue")
WEEKDAY_KEYS = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")


def weekday_key(d: date) -> str:
    """Return working_hours key for a date (mon..sun)."""
    idx = d.isoweekday() - 1
    return WEEKDAY_KEYS[idx]


def parse_date_from_user(text: str) -> date | None:
    """Parse a date from user input (e.g. 'tonight', 'tomorrow', '2025-03-01'). Returns None if unparseable."""
    text = (text or "").strip().lower()
    today = date.today()
    if text in ("today",):
        return today
    if text in ("tomorrow",):
        return today + timedelta(days=1)
    if text in ("tonight",):
        return today
    # ISO or common formats
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def _parse_time(s: str) -> time | None:
    """Parse 'HH:MM' or 'HH:MM:SS' to time."""
    if not s:
        return None
    for fmt in ("%H:%M", "%H:%M:%S"):
        try:
            return datetime.strptime(s.strip(), fmt).time()
        except ValueError:
            continue
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
    start = _parse_time(start_time)
    end = _parse_time(end_time)
    if start is None or end is None or slot_duration_minutes <= 0:
        return []
    slots: list[time] = []
    delta = timedelta(minutes=slot_duration_minutes)
    start_dt = datetime.combine(day, start)
    end_dt = datetime.combine(day, end)
    current = start_dt
    while current + delta <= end_dt:
        slots.append(current.time())
        current += delta
    return slots


def slot_taken(slot_time: time, slot_duration_minutes: int, booked_slots: list[dict[str, Any]]) -> bool:
    """
    Return True if slot_time is overlapping with any booked slot.
    booked_slots: list of dicts with 'booking_time' (time) and 'duration_minutes' (int).
    """
    slot_start = datetime.combine(date.today(), slot_time)
    slot_end = slot_start + timedelta(minutes=slot_duration_minutes)
    for b in booked_slots:
        bt = b.get("booking_time")
        dur = b.get("duration_minutes") or 0
        if bt is None:
            continue
        if isinstance(bt, time):
            b_start = datetime.combine(date.today(), bt)
        else:
            continue
        b_end = b_start + timedelta(minutes=dur)
        if slot_start < b_end and slot_end > b_start:
            return True
    return False
