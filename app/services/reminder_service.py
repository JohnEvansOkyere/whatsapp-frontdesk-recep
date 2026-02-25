"""APScheduler reminder scheduling. Schedule 24h and 1h before booking; cancel on booking cancel."""
from uuid import UUID

from app.core.scheduler import scheduler


def schedule_reminders(
    booking_id: UUID,
    booking_date: str,
    booking_time: str,
    business_name: str,
    customer_recipient_id: str,
    channel_send_message_fn,
    reference: str,
    party_size: str,
) -> tuple[str | None, str | None]:
    """
    Schedule 24h and 1h jobs. Return (reminder_24h_job_id, reminder_1h_job_id).
    channel_send_message_fn(recipient_id, text) is called by the job.
    """
    # TODO: compute run times, scheduler.add_job for each, return job ids
    return None, None


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
