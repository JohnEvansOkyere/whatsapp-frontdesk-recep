"""All settings via pydantic-settings. Never hardcode credentials."""
from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # App
    SECRET_KEY: str = "change-me-in-production"
    ENVIRONMENT: str = "development"
    BASE_URL: str = "http://localhost:8000"

    # Telegram (testing)
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_WEBHOOK_URL: str = ""

    # WhatsApp (defaults; per-client credentials in DB)
    META_APP_ID: str = ""
    META_APP_SECRET: str = ""

    # Database
    NEON_DATABASE_URL: str = ""

    # AI — multi-provider (default groq per project choice)
    AI_PROVIDER: Literal["openai", "groq", "gemini"] = "groq"
    AI_MODEL: str = "llama-3.1-8b-instant"
    OPENAI_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    GOOGLE_AI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""  # alias for GOOGLE_AI_API_KEY

    # Google Calendar OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = ""

    @property
    def gemini_api_key(self) -> str:
        return self.GOOGLE_AI_API_KEY or self.GEMINI_API_KEY


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
