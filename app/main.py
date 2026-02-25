"""FastAPI app entry point. Webhook registration is done externally (see CLAUDE Deployment)."""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import webhooks, appointments, businesses, onboarding, faqs
from app.core.database import init_db
from app.core.scheduler import scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: init DB, start scheduler. Shutdown: stop scheduler."""
    await init_db()
    if not scheduler.running:
        scheduler.start()
    yield
    if scheduler.running:
        scheduler.shutdown(wait=False)


app = FastAPI(title="Front Desk Bot API", lifespan=lifespan)
# Interactive API docs (no extra config): GET /docs (Swagger UI), GET /redoc (ReDoc)

app.include_router(webhooks.router)
app.include_router(appointments.router)
app.include_router(businesses.router)
app.include_router(onboarding.router)
app.include_router(faqs.router)


@app.get("/health")
async def health() -> dict[str, str]:
    """Liveness/readiness."""
    return {"status": "ok"}
