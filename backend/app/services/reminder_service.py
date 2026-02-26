"""APScheduler reminder scheduling. Schedule 24h and 1h before booking; cancel on booking cancel."""
from datetime import datetime, timedelta, time
from uuid import UUID

from app.core.config import settings
from app.core.scheduler import scheduler
from app.utils.message_templates import reminder_24h, reminder_1h


async def _send_reminder_24h(
    recipient_id: str,
    business_name: str,
    date_str: str,
    time_str: str,
    size_str: str,
    reference: str,
) -> None:
    from telegram import Bot
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    text = reminder_24h(business_name, date_str, time_str, size_str, reference)
    await bot.send_message(chat_id=int(recipient_id), text=text)


async def _send_reminder_1h(recipient_id: str, business_name: str) -> None:
    from telegram import Bot
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    text = reminder_1h(business_name)
    await bot.send_message(chat_id=int(recipient_id), text=text)


def schedule_reminders(
    booking_id: UUID,
    booking_date: str,
    booking_time: str,
    business_name: str,
    customer_recipient_id: str,
    reference: str,
    party_size: str,
) -> tuple[str | None, str | None]:
    """
    Schedule 24h and 1h before booking. Return (reminder_24h_job_id, reminder_1h_job_id).
    Uses AsyncIOScheduler; jobs run the async send functions.
    """
    try:
        day = datetime.strptime(booking_date, "%Y-%m-%d").date()
        parts = booking_time.replace(":", " ").split()
        h = int(parts[0]) if len(parts) > 0 else 0
        m = int(parts[1]) if len(parts) > 1 else 0
        s = int(parts[2]) if len(parts) > 2 else 0
        booking_dt = datetime.combine(day, time(h, m, s))
    except (ValueError, TypeError):
        return None, None

    run_24h = booking_dt - timedelta(hours=24)
    run_1h = booking_dt - timedelta(hours=1)
    now = datetime.now()
    date_str = booking_date
    time_str = booking_time if len(booking_time) >= 5 else f"{h:02d}:{m:02d}"

    job_id_24h = f"reminder_24h_{booking_id}"
    job_id_1h = f"reminder_1h_{booking_id}"
    rid_24h: str | None = None
    rid_1h: str | None = None

    if run_24h > now:
        scheduler.add_job(
            _send_reminder_24h,
            "date",
            run_date=run_24h,
            id=job_id_24h,
            args=[customer_recipient_id, business_name, date_str, time_str, party_size, reference],
            replace_existing=True,
        )
        rid_24h = job_id_24h
    if run_1h > now:
        scheduler.add_job(
            _send_reminder_1h,
            "date",
            run_date=run_1h,
            id=job_id_1h,
            args=[customer_recipient_id, business_name],
            replace_existing=True,
        )
        rid_1h = job_id_1h

    return rid_24h, rid_1h


def cancel_reminders(job_id_24h: str | None, job_id_1h: str | None) -> None:
    """Remove scheduled jobs by id."""
    if job_id_24h:
        try:
            scheduler.remove_job(job_id_24h)
        except Exception:
            pass
    if job_id_1h:
        try:
            scheduler.remove_job(job_id_1h)
        except Exception:
            pass
