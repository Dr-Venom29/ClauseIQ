import asyncio
import json
import pytest
from unittest.mock import MagicMock, AsyncMock
from app.core.exceptions import QuotaExceededException
from app.models.document import Document, Chunk, AnalysisSnapshot
from app.services.summary_service import SummaryService
from app.services.llm_router import LLMRouter


def test_summary_service_routes_to_router_with_task():
    async def _run():
        db = MagicMock()
        mock_router = MagicMock(spec=LLMRouter)
        expected_summary = {
            "executive_summary": "Exec summary",
            "purpose": "Purpose",
            "key_obligations": ["Obligation 1"],
            "important_clauses": ["Clause 1"],
            "penalties": ["Penalty 1"],
            "exceptions": ["Exception 1"],
            "takeaways": ["Takeaway 1"]
        }
        mock_router.generate_json = AsyncMock(return_value=expected_summary)

        service = SummaryService(db, router=mock_router)
        # Mock repositories
        service.document_repo.get_by_id = MagicMock(return_value=Document(
            id="doc1", user_id="u1", content_hash="hash123", filename="test.pdf"
        ))
        service.snapshot_repo.get_snapshot = MagicMock(return_value=None)
        service.snapshot_repo.create_snapshot = MagicMock()
        service.chunk_repo.get_chunks = MagicMock(return_value=[
            Chunk(id="c1", document_id="doc1", page=1, content="This is page 1 content"),
        ])
        service.metrics_repo.increment = MagicMock()

        result = await service.generate_summary(document_id="doc1", user_id="u1")

        assert result == expected_summary
        mock_router.generate_json.assert_awaited_once()
        call_args, call_kwargs = mock_router.generate_json.call_args
        assert call_kwargs.get("task") == "summary"
        assert call_kwargs.get("user_id") == "u1"
        assert "This is page 1 content" in call_args[0]
        service.snapshot_repo.create_snapshot.assert_called_once()
        service.metrics_repo.increment.assert_called_with("cache_miss", user_id="u1")

    asyncio.run(_run())


def test_summary_service_uses_cache_on_hit():
    async def _run():
        db = MagicMock()
        mock_router = MagicMock(spec=LLMRouter)
        cached_data = {"executive_summary": "Cached Exec Summary"}

        service = SummaryService(db, router=mock_router)
        service.document_repo.get_by_id = MagicMock(return_value=Document(
            id="doc1", user_id="u1", content_hash="hash123", filename="test.pdf"
        ))
        service.snapshot_repo.get_snapshot = MagicMock(return_value=AnalysisSnapshot(
            document_id="doc1", document_hash="hash123", analysis_type="summary",
            result_json=json.dumps(cached_data), user_id="u1"
        ))
        service.metrics_repo.increment = MagicMock()

        result = await service.generate_summary(document_id="doc1", user_id="u1")

        assert result == cached_data
        mock_router.generate_json.assert_not_called()
        service.metrics_repo.increment.assert_called_with("cache_hit", user_id="u1")

    asyncio.run(_run())


def test_summary_service_falls_back_on_quota_exceeded():
    async def _run():
        db = MagicMock()
        mock_router = MagicMock(spec=LLMRouter)
        mock_router.generate_json = AsyncMock(side_effect=QuotaExceededException("Quota exceeded"))

        service = SummaryService(db, router=mock_router)
        service.document_repo.get_by_id = MagicMock(return_value=Document(
            id="doc1", user_id="u1", content_hash="hash123", filename="test.pdf"
        ))
        service.snapshot_repo.get_snapshot = MagicMock(return_value=None)
        service.snapshot_repo.create_snapshot = MagicMock()
        service.chunk_repo.get_chunks = MagicMock(return_value=[
            Chunk(id="c1", document_id="doc1", page=1, content="First chunk content."),
            Chunk(id="c2", document_id="doc1", page=2, content="Second chunk content."),
        ])
        service.metrics_repo.increment = MagicMock()

        result = await service.generate_summary(document_id="doc1", user_id="u1")

        assert "First chunk content." in result["executive_summary"]
        assert "AI quota exhausted" in result["takeaways"][0]
        assert result["purpose"] == "Extracted automatically (Offline Mode)"
        service.snapshot_repo.create_snapshot.assert_called_once()

    asyncio.run(_run())
