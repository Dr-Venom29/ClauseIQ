from typing import Any
from app.services.llm_providers.base import LLMProvider
from app.services.llm_providers.gemini_provider import GeminiProvider

SUPPORTED_TASKS: frozenset[str] = frozenset({
    "summary",
    "risk_analysis",
    "compliance",
    "rag_chat",
    "version_impact",
    "clause_extraction",
})

DEFAULT_TASK_ROUTES: dict[str, str] = {
    "summary": "gemini",
    "risk_analysis": "gemini",
    "compliance": "gemini",
    "rag_chat": "gemini",
    "version_impact": "gemini",
    "clause_extraction": "gemini",
}


class LLMRouter:
    """Routes generation requests to configured providers based on task."""

    def __init__(
        self,
        providers: dict[str, LLMProvider],
        task_routes: dict[str, str] | None = None,
    ) -> None:
        if not providers:
            raise ValueError("At least one LLM provider is required.")

        self.providers = providers
        self.task_routes = dict(task_routes) if task_routes is not None else dict(DEFAULT_TASK_ROUTES)

        unknown_tasks = set(self.task_routes) - SUPPORTED_TASKS
        if unknown_tasks:
            raise ValueError(f"Unsupported LLM tasks: {sorted(unknown_tasks)}")

        invalid_providers = set(self.task_routes.values()) - set(self.providers)
        if invalid_providers:
            raise ValueError(
                f"Task routes point to unconfigured providers: {sorted(invalid_providers)}"
            )

    def get_provider(self, task: str) -> LLMProvider:
        if task not in SUPPORTED_TASKS:
            raise ValueError(f"Unsupported LLM task: '{task}'")
        provider_name = self.task_routes.get(task)
        if not provider_name or provider_name not in self.providers:
            raise ValueError(f"No configured provider for task: '{task}'")
        return self.providers[provider_name]

    def generate(
        self,
        prompt: str,
        *,
        task: str,
        **options: Any,
    ) -> Any:
        """Route general text generation to the appropriate provider."""
        provider = self.get_provider(task)
        if hasattr(provider, "generate"):
            return provider.generate(prompt, task=task, **options)
        if hasattr(provider, "generate_text"):
            return provider.generate_text(prompt, task=task, **options)
        raise NotImplementedError(f"Provider {provider} does not support generate")

    def generate_text(
        self,
        prompt: str,
        *,
        task: str,
        user_id: str | None = None,
        **options: Any,
    ) -> Any:
        """Route plain text generation to the appropriate provider."""
        provider = self.get_provider(task)
        if hasattr(provider, "generate_text"):
            return provider.generate_text(prompt, task=task, user_id=user_id, **options)
        if hasattr(provider, "generate"):
            return provider.generate(prompt, task=task, user_id=user_id, **options)
        raise NotImplementedError(f"Provider {provider} does not support generate_text")

    def generate_json(
        self,
        prompt: str,
        *,
        task: str,
        user_id: str | None = None,
        **options: Any,
    ) -> Any:
        """Route structured JSON generation to the appropriate provider."""
        provider = self.get_provider(task)
        if hasattr(provider, "generate_json"):
            return provider.generate_json(prompt, task=task, user_id=user_id, **options)
        raise NotImplementedError(f"Provider {provider} does not support generate_json")


_router_instance: LLMRouter | None = None


def get_llm_router() -> LLMRouter:
    """Retrieve or initialize the application's singleton LLM router."""
    global _router_instance
    if _router_instance is None:
        gemini_provider = GeminiProvider()
        _router_instance = LLMRouter(
            providers={"gemini": gemini_provider},
            task_routes=DEFAULT_TASK_ROUTES,
        )
    return _router_instance
