import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
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


def test_provider_interchangeability_without_aiservice():
    """
    Validates genuine provider abstraction:
    Configuring an alternative provider allows tasks to execute without
    ever constructing, importing, or calling AIService.
    """
    async def _run():
        class StandaloneLegalProvider:
            def __init__(self):
                self.calls = []

            async def generate(self, prompt: str, *, task: str, **options):
                self.calls.append(("generate", prompt, task, options))
                return "standalone output"

            async def generate_text(self, prompt: str, *, task: str, user_id: str | None = None, **options):
                self.calls.append(("generate_text", prompt, task, user_id, options))
                return "standalone text response"

            async def generate_json(self, prompt: str, *, task: str, user_id: str | None = None, **options):
                self.calls.append(("generate_json", prompt, task, user_id, options))
                return {"source": "standalone_provider", "analysis": "approved"}

        alt_provider = StandaloneLegalProvider()

        router = LLMRouter(
            providers={"alt_legal": alt_provider},
            task_routes={
                "summary": "alt_legal",
                "risk_analysis": "alt_legal",
                "compliance": "alt_legal",
                "rag_chat": "alt_legal",
                "version_impact": "alt_legal",
                "clause_extraction": "alt_legal",
            },
        )

        with patch("app.services.ai_service.AIService") as mock_ai:
            # 1. Structured JSON generation
            summary_res = await router.generate_json("Summarize contract", task="summary", user_id="user_abc")
            assert summary_res == {"source": "standalone_provider", "analysis": "approved"}

            # 2. Plain text generation
            chat_res = await router.generate_text("Explain clause 4", task="rag_chat", user_id="user_abc")
            assert chat_res == "standalone text response"

            # 3. AIService was never instantiated or called
            mock_ai.assert_not_called()

        assert len(alt_provider.calls) == 2
        assert alt_provider.calls[0][0] == "generate_json"
        assert alt_provider.calls[0][2] == "summary"
        assert alt_provider.calls[1][0] == "generate_text"
        assert alt_provider.calls[1][2] == "rag_chat"

    asyncio.run(_run())


def test_mixed_provider_routing_without_cross_talk():
    """
    Validates that router correctly routes different tasks to independent providers
    without cross-talk or leakage.
    """
    async def _run():
        class ProviderA:
            def __init__(self):
                self.called = False
            async def generate_json(self, prompt: str, *, task: str, user_id: str | None = None, **options):
                self.called = True
                return {"provider": "A"}

        class ProviderB:
            def __init__(self):
                self.called = False
            async def generate_json(self, prompt: str, *, task: str, user_id: str | None = None, **options):
                self.called = True
                return {"provider": "B"}

        prov_a = ProviderA()
        prov_b = ProviderB()

        router = LLMRouter(
            providers={"provider_a": prov_a, "provider_b": prov_b},
            task_routes={
                "summary": "provider_a",
                "risk_analysis": "provider_b",
                "compliance": "provider_a",
                "rag_chat": "provider_b",
                "version_impact": "provider_a",
                "clause_extraction": "provider_b",
            },
        )

        res_a = await router.generate_json("prompt", task="summary")
        assert res_a == {"provider": "A"}
        assert prov_a.called is True
        assert prov_b.called is False

        res_b = await router.generate_json("prompt", task="risk_analysis")
        assert res_b == {"provider": "B"}
        assert prov_b.called is True

    asyncio.run(_run())


def test_consumer_service_with_swapped_provider():
    """
    Validates end-to-end service behavior: injecting an alternative router
    into a consumer service (SummaryService) functions seamlessly with no AIService dependency.
    """
    async def _run():
        class MockOllamaLegalProvider:
            async def generate_json(self, prompt: str, *, task: str, user_id: str | None = None, **options):
                return {
                    "document_type": "Master Services Agreement",
                    "parties": ["Client Corp", "Vendor LLC"],
                    "key_obligations": ["Provide deliverables on schedule"],
                    "governing_law": "New York",
                    "summary": "Standard MSA routed entirely through local provider."
                }

        local_provider = MockOllamaLegalProvider()
        router = LLMRouter(
            providers={"local_llm": local_provider},
            task_routes={"summary": "local_llm"},
        )

        from app.services.summary_service import SummaryService
        from app.models.document import Document, Chunk

        db = MagicMock()
        service = SummaryService(db, router=router)
        service.document_repo.get_by_id = MagicMock(return_value=Document(
            id="doc999", user_id="u_corp", content_hash="hash999", filename="msa.pdf"
        ))
        service.snapshot_repo.get_snapshot = MagicMock(return_value=None)
        service.snapshot_repo.create_snapshot = MagicMock()
        service.chunk_repo.get_chunks = MagicMock(return_value=[
            Chunk(id="c99", document_id="doc999", page=1, content="This Master Services Agreement is entered..."),
        ])
        service.metrics_repo.increment = MagicMock()

        with patch("app.services.ai_service.AIService") as mock_ai:
            result = await service.generate_summary(document_id="doc999", user_id="u_corp")
            mock_ai.assert_not_called()

        assert result["summary"] == "Standard MSA routed entirely through local provider."
        assert result["governing_law"] == "New York"
        service.snapshot_repo.create_snapshot.assert_called_once()

    asyncio.run(_run())
