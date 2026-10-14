import asyncio
from typing import Any
import pytest
from unittest.mock import patch, MagicMock

from app.core.exceptions import QuotaExceededException
from app.services.llm_providers.base import LLMProvider
from app.services.llm_router import LLMRouter, SUPPORTED_TASKS


class FakeProvider:
    """
    Deterministic test double implementing LLMProvider protocol.
    Records calls for assertion without invoking any external services or AIService.
    """

    def __init__(
        self,
        text_response: str = "fake text response",
        json_response: dict[str, Any] | list[dict[str, Any]] | None = None,
    ) -> None:
        self.text_response = text_response
        self.json_response = json_response if json_response is not None else {"result": "fake structured response"}
        self.text_calls: list[dict[str, Any]] = []
        self.json_calls: list[dict[str, Any]] = []
        self.generate_calls: list[dict[str, Any]] = []

    def generate(self, prompt: str, *, task: str, **options: Any) -> Any:
        self.generate_calls.append({"prompt": prompt, "task": task, "options": options})
        return self.text_response

    async def generate_text(
        self,
        prompt: str,
        *,
        task: str,
        user_id: str | None = None,
        **options: Any,
    ) -> str:
        self.text_calls.append({
            "prompt": prompt,
            "task": task,
            "user_id": user_id,
            "options": options,
        })
        return self.text_response

    async def generate_json(
        self,
        prompt: str,
        *,
        task: str,
        user_id: str | None = None,
        **options: Any,
    ) -> Any:
        self.json_calls.append({
            "prompt": prompt,
            "task": task,
            "user_id": user_id,
            "options": options,
        })
        return self.json_response


# Step 5 / Step 6: Verify protocol compliance
def test_fake_provider_satisfies_protocol():
    fake = FakeProvider()
    assert isinstance(fake, LLMProvider)


# Step 7: Test text generation
def test_text_generation_via_fake_provider():
    async def _run():
        fake = FakeProvider(text_response="fake text response")
        router = LLMRouter(
            providers={"fake": fake},
            task_routes={"rag_chat": "fake"},
        )

        response = await router.generate_text(
            "What is the liability cap?",
            task="rag_chat",
            user_id="user_test_42",
        )

        assert response == "fake text response"
        assert len(fake.text_calls) == 1
        call = fake.text_calls[0]
        assert call["prompt"] == "What is the liability cap?"
        assert call["task"] == "rag_chat"
        assert call["user_id"] == "user_test_42"
        assert len(fake.json_calls) == 0

    asyncio.run(_run())


# Step 8: Test structured generation
def test_structured_generation_via_fake_provider():
    async def _run():
        expected_json = {
            "document_type": "NDA",
            "summary": "Standard bilateral non-disclosure agreement.",
            "risk_level": "Low",
        }
        fake = FakeProvider(json_response=expected_json)
        router = LLMRouter(
            providers={"fake": fake},
            task_routes={"summary": "fake"},
        )

        response = await router.generate_json(
            "Summarize the agreement.",
            task="summary",
            user_id="user_corp_1",
        )

        assert response == expected_json
        assert len(fake.json_calls) == 1
        call = fake.json_calls[0]
        assert call["prompt"] == "Summarize the agreement."
        assert call["task"] == "summary"
        assert call["user_id"] == "user_corp_1"
        assert len(fake.text_calls) == 0

    asyncio.run(_run())


# Step 9: Test every task mapping through the router
@pytest.mark.parametrize("task,is_text", [
    ("summary", False),
    ("risk_analysis", False),
    ("compliance", False),
    ("rag_chat", True),
    ("version_impact", False),
    ("clause_extraction", False),
])
def test_all_six_tasks_routed_to_fake_provider(task: str, is_text: bool):
    async def _run():
        fake = FakeProvider(
            text_response=f"response for {task}",
            json_response={"task": task, "status": "ok"},
        )
        router = LLMRouter(
            providers={"fake": fake},
            task_routes={t: "fake" for t in SUPPORTED_TASKS},
        )

        if is_text:
            res = await router.generate_text("test prompt", task=task, user_id="u1")
            assert res == f"response for {task}"
            assert len(fake.text_calls) == 1
            assert fake.text_calls[0]["task"] == task
        else:
            res = await router.generate_json("test prompt", task=task, user_id="u1")
            assert res == {"task": task, "status": "ok"}
            assert len(fake.json_calls) == 1
            assert fake.json_calls[0]["task"] == task

    asyncio.run(_run())


# Step 10: Test unsupported tasks fail explicitly
def test_unsupported_task_rejected_by_router():
    async def _run():
        fake = FakeProvider()
        router = LLMRouter(
            providers={"fake": fake},
            task_routes={t: "fake" for t in SUPPORTED_TASKS},
        )

        with pytest.raises(ValueError, match="Unsupported LLM task: 'invalid_task'"):
            await router.generate_text("prompt", task="invalid_task")

        with pytest.raises(ValueError, match="Unsupported LLM task: 'invalid_task'"):
            await router.generate_json("prompt", task="invalid_task")

        assert len(fake.text_calls) == 0
        assert len(fake.json_calls) == 0

    asyncio.run(_run())


# Step 11: Test unconfigured provider routes fail explicitly
def test_unconfigured_provider_route_rejected():
    fake = FakeProvider()
    with pytest.raises(ValueError, match="Task routes point to unconfigured providers: \\['missing_provider'\\]"):
        LLMRouter(
            providers={"fake": fake},
            task_routes={"summary": "missing_provider"},
        )


# Step 12: Test quota exception propagation
def test_quota_exception_propagates_from_fake_provider():
    async def _run():
        class QuotaFailingProvider(FakeProvider):
            async def generate_json(self, prompt: str, *, task: str, user_id: str | None = None, **options: Any) -> Any:
                raise QuotaExceededException("Rate limit reached for test provider.")

            async def generate_text(self, prompt: str, *, task: str, user_id: str | None = None, **options: Any) -> str:
                raise QuotaExceededException("Quota exceeded for test provider.")

        failing_provider = QuotaFailingProvider()
        router = LLMRouter(
            providers={"fake": failing_provider},
            task_routes={"summary": "fake", "rag_chat": "fake"},
        )

        with pytest.raises(QuotaExceededException) as exc_info_json:
            await router.generate_json("prompt", task="summary")
        assert "Rate limit reached" in exc_info_json.value.message

        with pytest.raises(QuotaExceededException) as exc_info_text:
            await router.generate_text("prompt", task="rag_chat")
        assert "Quota exceeded" in exc_info_text.value.message

    asyncio.run(_run())


# Step 13: Test that AIService is never constructed or called
def test_aiservice_is_never_constructed_with_fake_provider():
    async def _run():
        fake = FakeProvider(
            text_response="pure fake response",
            json_response={"status": "fake"},
        )
        router = LLMRouter(
            providers={"fake": fake},
            task_routes={t: "fake" for t in SUPPORTED_TASKS},
        )

        with patch("app.services.ai_service.AIService") as mock_ai:
            for task in SUPPORTED_TASKS:
                if task == "rag_chat":
                    text_out = await router.generate_text("chat prompt", task=task, user_id="u99")
                    assert text_out == "pure fake response"
                else:
                    json_out = await router.generate_json("json prompt", task=task, user_id="u99")
                    assert json_out == {"status": "fake"}

            # Assert AIService was strictly never called or constructed across all tasks
            mock_ai.assert_not_called()

        assert len(fake.text_calls) == 1
        assert len(fake.json_calls) == 5

    asyncio.run(_run())
