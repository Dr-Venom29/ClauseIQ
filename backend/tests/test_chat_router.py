import asyncio
import pytest
from unittest.mock import MagicMock, AsyncMock
from app.core.exceptions import QuotaExceededException
from app.services.chat_service import ChatService
from app.services.llm_router import LLMRouter


class MockSearchResult:
    def __init__(self, content, page_number, section, document_name):
        self.content = content
        self.page_number = page_number
        self.section = section
        self.document_name = document_name


def test_chat_service_routes_to_router_with_task():
    async def _run():
        db = MagicMock()
        mock_router = MagicMock(spec=LLMRouter)
        mock_router.generate_text = AsyncMock(
            return_value="According to [Citation 1], the termination notice is 30 days."
        )

        service = ChatService(db, router=mock_router)
        service.search_service.search = AsyncMock(return_value=[
            MockSearchResult(
                content="Termination requires 30 days written notice.",
                page_number=3,
                section="Clause 5.1",
                document_name="contract.pdf"
            )
        ])

        result = await service.chat(
            query="What is the notice period?",
            user_id="user_123",
            document_id="doc_456"
        )

        assert result["response"] == "According to [Citation 1], the termination notice is 30 days."
        assert len(result["citations"]) == 1
        assert result["citations"][0] == {
            "document_name": "contract.pdf",
            "page_number": 3,
            "section": "Clause 5.1"
        }

        mock_router.generate_text.assert_awaited_once()
        call_args, call_kwargs = mock_router.generate_text.call_args
        assert call_kwargs.get("task") == "rag_chat"
        assert call_kwargs.get("user_id") == "user_123"
        assert "Termination requires 30 days written notice." in call_args[0]
        assert "What is the notice period?" in call_args[0]

        service.search_service.search.assert_awaited_once_with(
            "What is the notice period?",
            user_id="user_123",
            document_id="doc_456",
            top_k=5
        )

    asyncio.run(_run())


def test_chat_service_handles_quota_exception():
    async def _run():
        db = MagicMock()
        mock_router = MagicMock(spec=LLMRouter)
        mock_router.generate_text = AsyncMock(
            side_effect=QuotaExceededException("AI quota exhausted. Please try again later.")
        )

        service = ChatService(db, router=mock_router)
        service.search_service.search = AsyncMock(return_value=[
            MockSearchResult(
                content="Some clause content",
                page_number=1,
                section="1.0",
                document_name="doc.pdf"
            )
        ])

        result = await service.chat(
            query="Tell me about clause 1",
            user_id="user_123"
        )

        assert result["response"] == "AI quota exhausted. Please try again later."
        assert len(result["citations"]) == 1

    asyncio.run(_run())


def test_chat_service_unhandled_exception_propagates():
    async def _run():
        db = MagicMock()
        mock_router = MagicMock(spec=LLMRouter)
        mock_router.generate_text = AsyncMock(
            side_effect=RuntimeError("Unexpected connection drop")
        )

        service = ChatService(db, router=mock_router)
        service.search_service.search = AsyncMock(return_value=[])

        with pytest.raises(RuntimeError, match="Unexpected connection drop"):
            await service.chat(query="test query", user_id="user_123")

    asyncio.run(_run())
