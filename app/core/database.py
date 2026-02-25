"""Neon async DB connection + session. Never use sync SQLAlchemy."""
from collections.abc import AsyncGenerator
from urllib.parse import parse_qs, urlparse, urlunparse

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.models.db.base import Base

# PostgreSQL (Neon) only. Use async driver (asyncpg) for create_async_engine.
database_url = (settings.NEON_DATABASE_URL or "").strip().strip('"').strip("'")
if not database_url:
    raise RuntimeError("NEON_DATABASE_URL is required. Set it in .env with your Neon PostgreSQL connection string.")
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql+asyncpg://", 1)
elif database_url.startswith("postgresql://") and "+asyncpg" not in database_url:
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

# asyncpg does not support psycopg2-style query params (sslmode, channel_binding, etc.).
# Strip the entire query string so SQLAlchemy does not pass them to asyncpg.connect().
parsed = urlparse(database_url)
if parsed.query:
    qs = parse_qs(parsed.query, keep_blank_values=True)
    need_ssl = "sslmode" in qs or "ssl" in qs
    database_url = urlunparse(parsed._replace(query=""))
else:
    need_ssl = False
# Neon requires SSL.
connect_args = {}
if need_ssl or "neon.tech" in database_url:
    connect_args["ssl"] = True

engine = create_async_engine(
    database_url,
    echo=settings.ENVIRONMENT == "development",
    connect_args=connect_args,
)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
