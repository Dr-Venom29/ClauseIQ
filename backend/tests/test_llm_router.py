import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.core.exceptions import QuotaExceededException
from app.services.llm_router import LLMRouter, SUPPORTED_TASKS, DEFAULT_TASK_ROUTES, get_llm_router
from app.services.llm_providers.gemini_provider import GeminiProvider


class FakeProvider:
    def __init__(self, response="test response", json_response=None):
        self.response = response
        self.json_response = json_response or {"key": "value"}
        self.calls = []

    def generate(self, prompt, *, task, **options):
        self.calls.append((prompt, task, options))
        return self.response

    def generate_text(self, prompt, *, task, **options):
        self.calls.append((prompt, task, options))
        return self.response

    def generate_json(self, prompt, *, task, **options):
        self.calls.append((prompt, task, options))
        return self.json_response


def test_summary_routes_to_gemini():
    gemini = FakeProvider()
    router = LLMRouter(
        providers={"gemini": gemini},
        task_routes={"summary": "gemini"},
    )
    result = router.generate(
        "Summarize this contract",
        task="summary",
    )
    assert result == "test response"
    assert len(gemini.calls) == 1
    assert gemini.calls[0][1] == "summary"


def test_unknown_task_in_routes_is_rejected():
    gemini = FakeProvider()
    with pytest.raises(ValueError, match="Unsupported LLM tasks"):
        LLMRouter(
            providers={"gemini": gemini},
            task_routes={"unsupported_task": "gemini"},
        )


def test_unknown_task_in_generate_is_rejected():
    gemini = FakeProvider()
    router = LLMRouter(
        providers={"gemini": gemini},
        task_routes={"summary": "gemini"},
    )
    with pytest.raises(ValueError, match="Unsupported LLM task"):
        router.generate("test prompt", task="invalid_task")


def test_unconfigured_provider_is_rejected():
    gemini = FakeProvider()
    with pytest.raises(ValueError, match="unconfigured providers"):
        LLMRouter(
            providers={"gemini": gemini},
            task_routes={"summary": "non_existent_provider"},
        )


def test_empty_providers_is_rejected():
    with pytest.raises(ValueError, match="At least one LLM provider is required"):
        LLMRouter(providers={}, task_routes={})


def test_quota_exceeded_exception_propagates_synchronously():
    class FailingProvider:
        def generate(self, prompt, *, task, **options):
            raise QuotaExceededException("Rate limit reached")

    router = LLMRouter(
        providers={"gemini": FailingProvider()},
        task_routes={"summary": "gemini"},
    )
    with pytest.raises(QuotaExceededException) as exc_info:
        router.generate("test", task="summary")
    assert "Rate limit reached" in exc_info.value.message


def test_gemini_provider_adapter_async():
    async def _run():
        mock_ai = MagicMock()
        mock_ai.generate_text = AsyncMock(return_value="gemini generated text")
        mock_ai.generate_json = AsyncMock(return_value={"parsed": True})

        provider = GeminiProvider(ai_service=mock_ai)
        router = LLMRouter(
            providers={"gemini": provider},
            task_routes={"rag_chat": "gemini", "risk_analysis": "gemini"},
        )

        # Test text generation through router
        text_result = await router.generate_text("query", task="rag_chat", user_id="u123")
        assert text_result == "gemini generated text"
        mock_ai.generate_text.assert_awaited_once_with(
            prompt="query",
            user_id="u123",
            model_name="gemini-2.5-flash",
        )

        # Test JSON generation through router
        json_result = await router.generate_json("risk prompt", task="risk_analysis", user_id="u123")
        assert json_result == {"parsed": True}
        mock_ai.generate_json.assert_awaited_once_with(
            prompt="risk prompt",
            user_id="u123",
            model_name="gemini-2.5-flash",
        )

    asyncio.run(_run())


def test_quota_exception_propagates_through_gemini_adapter():
    async def _run():
        mock_ai = MagicMock()
        mock_ai.generate_json = AsyncMock(side_effect=QuotaExceededException("Gemini quota exhausted"))

        provider = GeminiProvider(ai_service=mock_ai)
        router = LLMRouter(
            providers={"gemini": provider},
            task_routes={"summary": "gemini"},
        )

        with pytest.raises(QuotaExceededException) as exc_info:
            await router.generate_json("prompt", task="summary")
        assert "Gemini quota exhausted" in exc_info.value.message

    asyncio.run(_run())


def test_default_task_routes_covers_all_supported_tasks():
    assert set(DEFAULT_TASK_ROUTES.keys()) == SUPPORTED_TASKS
    for task, provider in DEFAULT_TASK_ROUTES.items():
        assert provider == "gemini"


def test_get_llm_router_singleton():
    router1 = get_llm_router()
    router2 = get_llm_router()
    assert router1 is router2
    assert "gemini" in router1.providers
