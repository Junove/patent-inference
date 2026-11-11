"""Near AI Cloud chat client (FR-G1, FR-G3). OpenAI-compatible chat-completions
streaming; vision input is a content part on the user message, same as text."""
import json
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass

import httpx

from app.config import Settings


@dataclass
class ChatChunk:
    delta: str = ""
    usage: dict | None = None  # present only on the final chunk, e.g. {"total_tokens": 123}


class NearAIClient(ABC):
    @abstractmethod
    def stream(self, messages: list[dict], *, max_tokens: int) -> AsyncIterator[ChatChunk]: ...


class HttpNearAIClient(NearAIClient):
    def __init__(self, settings: Settings):
        self._settings = settings

    async def stream(self, messages: list[dict], *, max_tokens: int) -> AsyncIterator[ChatChunk]:
        settings = self._settings
        payload = {"model": settings.near_ai_model, "messages": messages, "stream": True, "max_tokens": max_tokens}
        headers = {"Authorization": f"Bearer {settings.near_ai_api_key}"}
        async with httpx.AsyncClient(base_url=settings.near_ai_base_url, timeout=120) as http:
            async with http.stream("POST", "/chat/completions", json=payload, headers=headers) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if not line.startswith("data:"):
                        continue
                    raw = line.removeprefix("data:").strip()
                    if raw == "[DONE]":
                        break
                    chunk = json.loads(raw)
                    delta = chunk["choices"][0]["delta"].get("content", "") if chunk.get("choices") else ""
                    yield ChatChunk(delta=delta, usage=chunk.get("usage"))
