"""APScheduler instance for reminders (24h and 1h before booking)."""
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()
