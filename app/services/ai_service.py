"""AI service with multi-provider support (OpenAI, Groq, Gemini).

High-level skeleton only. All concrete behavior must follow CLAUDE.md.
"""
from __future__ import annotations

import enum
import re
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
    """Groq implementation using OpenAI-compatible chat completions API.

    Endpoint: POST https://api.groq.com/openai/v1/chat/completions
    Docs: console.groq.com/docs
    """

    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model

    async def generate(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
    ) -> str:
        """Call Groq chat completions and return assistant text."""

        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        groq_messages: list[dict[str, str]] = [
            {"role": "system", "content": system_prompt},
            *messages,
        ]

        payload: dict[str, Any] = {
            "model": self.model,
            "messages": groq_messages,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

        # OpenAI-compatible: choices[0].message.content
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as exc:
            raise RuntimeError("Unexpected Groq response format") from exc


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


# Pattern: "ACTION: NAME" or "ACTION: NAME { ... }" or "ACTION: NAME key=val key2=val2"
_ACTION_LINE_RE = re.compile(
    r"^\s*ACTION:\s*(\w+)(?:\s+\{([^}]*)\}|\s+(.+))?\s*$",
    re.IGNORECASE | re.MULTILINE,
)


def _parse_action_and_data(raw_text: str) -> tuple[Optional[AIAction], Dict[str, Any] | None, str]:
    """Parse ACTION tags from the model reply per CLAUDE.md.

    Returns (action, data, reply_text_with_action_lines_stripped).
    """
    action: Optional[AIAction] = None
    data: Dict[str, Any] | None = None
    lines = raw_text.split("\n")
    kept_lines: list[str] = []

    for line in lines:
        m = _ACTION_LINE_RE.match(line.strip())
        if m:
            name, brace_content, rest = m.group(1), m.group(2), m.group(3)
            try:
                action = AIAction(name.upper())
            except ValueError:
                kept_lines.append(line)
                continue
            # Optional payload: {service_id, date, party_size} or key=val key2=val2
            if brace_content:
                parts = [p.strip() for p in brace_content.split(",")]
                data = {p: None for p in parts if p}
            elif rest:
                data = {}
                for part in rest.split():
                    if "=" in part:
                        k, _, v = part.partition("=")
                        data[k.strip()] = v.strip()
            if not data:
                data = None
            # Don't add ACTION line to reply shown to user
            continue
        kept_lines.append(line)

    clean_reply = "\n".join(kept_lines).strip()
    return action, data, clean_reply or raw_text


async def process_message(
    system_prompt: str,
    messages: List[Dict[str, str]],
) -> AIResult:
    """High-level AI entry point.

    This function is responsible only for:
    - Selecting the configured provider
    - Sending system_prompt + messages
    - Parsing ACTION tags and returning a normalized AIResult (reply_text = conversational part only)
    """

    provider = _get_provider()
    raw_text = await provider.generate(system_prompt=system_prompt, messages=messages)

    action, data, reply_text = _parse_action_and_data(raw_text)

    return AIResult(reply_text=reply_text, action=action, data=data)

