"""DB session and auth dependencies for FastAPI routes."""
from app.core.database import get_db

__all__ = ["get_db"]
