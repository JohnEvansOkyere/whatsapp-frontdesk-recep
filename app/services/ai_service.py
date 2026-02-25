"""AI service with multi-provider support (OpenAI, Groq, Gemini).

High-level skeleton only. All concrete behavior must follow CLAUDE.md.
"""
from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import httpx

from app.core.config import settings


class AIProviderName(str, enum.Enum):
    """Supported AI providers."""

    OPENAI = "openai"
    GROQ = "groq"
    GEMINI = "gemini"


class AIAction(str, enum.Enum):
    """Actions the AI can trigger (see CLAUDE.md)."""

    SHOW_SLOTS = "SHOW_SLOTS"
    SHOW_BOOKINGS = "SHOW_BOOKINGS"
    MANAGE_BOOKING = "MANAGE_BOOKING"
    HUMAN_HANDOFF = "HUMAN_HANDOFF"
    CONFIRM_BOOKING = "CONFIRM_BOOKING"


@dataclass
class AIResult:
    """Normalized AI result for handlers and services."""

    reply_text: str
    action: Optional[AIAction] = None
    data: Dict[str, Any] | None = None


class BaseProvider:
    """Abstract provider interface."""

    async def generate(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
    ) -> str:
        """Return raw assistant reply text.

        Concrete implementations must:
        - Call their provider's chat/completions API
        - Use `settings.AI_MODEL` as the model name
        - Respect the provided `system_prompt` and `messages`
        """

        msg = f"{self.__class__.__name__}.generate() not implemented"
        raise NotImplementedError(msg)


class GroqProvider(BaseProvider):
    """Groq implementation placeholder.

    Must call Groq's chat completion endpoint using httpx, never requests.
    """

    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model

    async def generate(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
    ) -> str:
        # High-level placeholder; actual HTTP call intentionally omitted.
        # Implementors should:
        # - POST to Groq's chat completions endpoint
        # - Pass self.model as the model name
        # - Include system_prompt and messages in the request body
        # - Return the assistant's text content
        msg = (
            "GroqProvider.generate is a high-level placeholder. "
            "Implement the actual httpx call to Groq's chat API."
        )
        raise NotImplementedError(msg)


class OpenAIProvider(BaseProvider):
    """OpenAI implementation placeholder."""

    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model


class GeminiProvider(BaseProvider):
    """Google Gemini implementation placeholder."""

    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model


def _get_provider() -> BaseProvider:
    """Instantiate provider based on settings.AI_PROVIDER.

    Does not assume any specific model name; uses settings.AI_MODEL as-is.
    """

    provider_name = settings.AI_PROVIDER
    model = settings.AI_MODEL

    if provider_name == AIProviderName.GROQ.value:
        if not settings.GROQ_API_KEY:
            raise RuntimeError("GROQ_API_KEY is not configured")
        return GroqProvider(api_key=settings.GROQ_API_KEY, model=model)

    if provider_name == AIProviderName.OPENAI.value:
        if not settings.OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY is not configured")
        return OpenAIProvider(api_key=settings.OPENAI_API_KEY, model=model)

    if provider_name == AIProviderName.GEMINI.value:
        api_key = settings.gemini_api_key
        if not api_key:
            raise RuntimeError("GOOGLE_AI_API_KEY / GEMINI_API_KEY is not configured")
        return GeminiProvider(api_key=api_key, model=model)

    raise RuntimeError(f"Unsupported AI_PROVIDER: {provider_name}")


def _parse_action_and_data(raw_text: str) -> tuple[Optional[AIAction], Dict[str, Any] | None]:
    """Parse ACTION tags from the model reply.

    High-level stub: callers must implement robust parsing that matches CLAUDE.md.
    For now, this function does NOT attempt to parse concrete payloads.
    """

    # Minimal, non-assuming implementation: no automatic parsing.
    return None, None


async def process_message(
    system_prompt: str,
    messages: List[Dict[str, str]],
) -> AIResult:
    """High-level AI entry point.

    This function is responsible only for:
    - Selecting the configured provider
    - Sending system_prompt + messages
    - Returning a normalized AIResult

    The full flow described in CLAUDE.md (loading conversation history,
    building booking context, trimming to 20 messages, etc.) should be
    implemented by the caller or a higher-level orchestrator.
    """

    provider = _get_provider()
    raw_text = await provider.generate(system_prompt=system_prompt, messages=messages)

    action, data = _parse_action_and_data(raw_text)

    return AIResult(reply_text=raw_text, action=action, data=data)

