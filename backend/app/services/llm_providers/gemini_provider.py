from collections.abc import Callable
import inspect
from typing import Any
from app.services.ai_service import AIService
from app.services.llm_providers.base import LLMProvider

class GeminiProvider:
    """Adapter around ClauseIQ's existing AIService."""

    def __init__(
        self,
        ai_service: AIService | None = None,
        generate_fn: Callable[..., Any] | None = None,
        generate_json_fn: Callable[..., Any] | None = None,
    ) -> None:
        self._ai_service = ai_service
        self._generate_fn = generate_fn
        self._generate_json_fn = generate_json_fn

    @property
    def ai_service(self) -> AIService:
        if self._ai_service is None:
            self._ai_service = AIService()
        return self._ai_service

    async def generate(
        self,
        prompt: str,
        *,
        task: str,
        **options: Any,
    ) -> Any:
        """General generation method delegating to generate_fn or generate_text."""
        if self._generate_fn is not None:
            res = self._generate_fn(prompt, **options)
            if inspect.isawaitable(res):
                return await res
            return res
        return await self.generate_text(prompt, task=task, **options)

    async def generate_text(
        self,
        prompt: str,
        *,
        task: str,
        user_id: str | None = None,
        **options: Any,
    ) -> str:
        """Generate text using existing AIService.generate_text."""
        if self._generate_fn is not None:
            res = self._generate_fn(prompt, user_id=user_id, **options)
            if inspect.isawaitable(res):
                return await res
            return res

        model_name = options.get("model_name", "gemini-2.5-flash")
        return await self.ai_service.generate_text(
            prompt=prompt,
            user_id=user_id,
            model_name=model_name,
        )

    async def generate_json(
        self,
        prompt: str,
        *,
        task: str,
        user_id: str | None = None,
        **options: Any,
    ) -> Any:
        """Generate structured JSON using existing AIService.generate_json."""
        if self._generate_json_fn is not None:
            res = self._generate_json_fn(prompt, user_id=user_id, **options)
            if inspect.isawaitable(res):
                return await res
            return res

        model_name = options.get("model_name", "gemini-2.5-flash")
        return await self.ai_service.generate_json(
            prompt=prompt,
            user_id=user_id,
            model_name=model_name,
        )
