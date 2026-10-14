from typing import Any, Protocol, runtime_checkable

@runtime_checkable
class LLMProvider(Protocol):
    """Common interface for text and structured generation providers."""

    def generate(
        self,
        prompt: str,
        *,
        task: str,
        **options: Any,
    ) -> Any:
        """Generate text or raise a classified provider exception."""
        ...

    def generate_text(
        self,
        prompt: str,
        *,
        task: str,
        user_id: str | None = None,
        **options: Any,
    ) -> Any:
        """Generate plain text or raise a classified provider exception."""
        ...

    def generate_json(
        self,
        prompt: str,
        *,
        task: str,
        user_id: str | None = None,
        **options: Any,
    ) -> Any:
        """Generate structured JSON or raise a classified provider exception."""
        ...
