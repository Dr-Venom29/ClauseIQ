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
