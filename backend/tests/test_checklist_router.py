import asyncio
import json
import pytest
from unittest.mock import MagicMock, AsyncMock
from app.core.exceptions import QuotaExceededException
from app.models.document import Document, Chunk, AnalysisSnapshot
from app.services.checklist_service import ChecklistService
from app.services.llm_router import LLMRouter


def test_checklist_service_routes_to_router_with_task():
    async def _run():
        db = MagicMock()
        mock_router = MagicMock(spec=LLMRouter)
        expected_checklist = [
            {"title": "Termination Clause", "status": "present", "explanation": "30 days notice", "citation": "Sec 5"},
            {"title": "Confidentiality", "status": "present", "explanation": "Standard NDA", "citation": "Sec 2"},
            {"title": "Governing Law", "status": "missing", "explanation": "Not found", "citation": "None"}
        ]
        mock_router.generate_json = AsyncMock(return_value=expected_checklist)

        service = ChecklistService(db, router=mock_router)
        service.document_repo.get_by_id = MagicMock(return_value=Document(
            id="doc1", user_id="u1", content_hash="hash123", filename="test.pdf"
        ))
        service.snapshot_repo.get_snapshot = MagicMock(return_value=None)
        service.snapshot_repo.create_snapshot = MagicMock()
        service.chunk_repo.get_chunks = MagicMock(return_value=[
            Chunk(id="c1", document_id="doc1", page=1, content="Parties agree to terminate upon 30 days notice."),
        ])
        service.metrics_repo.increment = MagicMock()

        result = await service.generate_checklist(document_id="doc1", user_id="u1")

        assert result == expected_checklist
        mock_router.generate_json.assert_awaited_once()
        call_args, call_kwargs = mock_router.generate_json.call_args
        assert call_kwargs.get("task") == "compliance"
        assert call_kwargs.get("user_id") == "u1"
        assert "Parties agree to terminate" in call_args[0]
        service.snapshot_repo.create_snapshot.assert_called_once()
        service.metrics_repo.increment.assert_called_with("cache_miss", user_id="u1")

    asyncio.run(_run())


def test_checklist_service_uses_cache_on_hit():
    async def _run():
        db = MagicMock()
        mock_router = MagicMock(spec=LLMRouter)
        cached_checklist = [
            {"title": "Cached Compliance", "status": "present", "explanation": "Cached", "citation": "Sec 1"}
        ]

        service = ChecklistService(db, router=mock_router)
        service.document_repo.get_by_id = MagicMock(return_value=Document(
            id="doc1", user_id="u1", content_hash="hash123", filename="test.pdf"
        ))
        service.snapshot_repo.get_snapshot = MagicMock(return_value=AnalysisSnapshot(
            document_id="doc1", document_hash="hash123", analysis_type="checklist",
            result_json=json.dumps(cached_checklist), user_id="u1"
        ))
        service.metrics_repo.increment = MagicMock()

        result = await service.generate_checklist(document_id="doc1", user_id="u1")

        assert result == cached_checklist
        mock_router.generate_json.assert_not_called()
        service.metrics_repo.increment.assert_called_with("cache_hit", user_id="u1")

    asyncio.run(_run())


def test_checklist_service_falls_back_on_quota_exceeded():
    async def _run():
        db = MagicMock()
        mock_router = MagicMock(spec=LLMRouter)
        mock_router.generate_json = AsyncMock(side_effect=QuotaExceededException("Quota exceeded"))

        service = ChecklistService(db, router=mock_router)
        service.document_repo.get_by_id = MagicMock(return_value=Document(
            id="doc1", user_id="u1", content_hash="hash123", filename="test.pdf"
        ))
        service.snapshot_repo.get_snapshot = MagicMock(return_value=None)
        service.snapshot_repo.create_snapshot = MagicMock()
        # Content has termination and confidentiality, but missing indemnification, governing law, force majeure
        service.chunk_repo.get_chunks = MagicMock(return_value=[
            Chunk(id="c1", document_id="doc1", page=1, content="This agreement may terminate at any time. All terms are confidential."),
        ])
        service.metrics_repo.increment = MagicMock()

        result = await service.generate_checklist(document_id="doc1", user_id="u1")

        # Verify offline checks
        status_map = {item["title"]: item["status"] for item in result}
        assert status_map["Termination Clause"] == "present"
        assert status_map["Confidentiality"] == "present"
        assert status_map["Indemnification"] == "missing"
        assert status_map["Governing Law"] == "missing"
        assert status_map["Force Majeure"] == "missing"

        for item in result:
            assert item["citation"] == "Offline Mode Fallback"

        service.snapshot_repo.create_snapshot.assert_called_once()

    asyncio.run(_run())


def test_checklist_service_document_not_found():
    async def _run():
        db = MagicMock()
        mock_router = MagicMock(spec=LLMRouter)
        service = ChecklistService(db, router=mock_router)
        service.document_repo.get_by_id = MagicMock(return_value=None)

        with pytest.raises(ValueError, match="Document not found"):
            await service.generate_checklist(document_id="missing_doc", user_id="u1")

    asyncio.run(_run())


def test_checklist_service_unhandled_exception_propagates():
    async def _run():
        db = MagicMock()
        mock_router = MagicMock(spec=LLMRouter)
        mock_router.generate_json = AsyncMock(side_effect=RuntimeError("Unexpected LLM failure"))

        service = ChecklistService(db, router=mock_router)
        service.document_repo.get_by_id = MagicMock(return_value=Document(
            id="doc1", user_id="u1", content_hash="hash123", filename="test.pdf"
        ))
        service.snapshot_repo.get_snapshot = MagicMock(return_value=None)
        service.chunk_repo.get_chunks = MagicMock(return_value=[
            Chunk(id="c1", document_id="doc1", page=1, content="Some content"),
        ])

        with pytest.raises(RuntimeError, match="Unexpected LLM failure"):
            await service.generate_checklist(document_id="doc1", user_id="u1")

    asyncio.run(_run())
