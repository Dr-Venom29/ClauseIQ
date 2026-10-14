import asyncio
import json
import pytest
from unittest.mock import MagicMock, AsyncMock
from app.core.exceptions import QuotaExceededException
from app.models.document import Document, Chunk, AnalysisSnapshot
from app.services.risk_service import RiskService
from app.services.llm_router import LLMRouter


def test_risk_service_routes_to_router_with_task():
    async def _run():
        db = MagicMock()
        mock_router = MagicMock(spec=LLMRouter)
        expected_risks = {
            "high_risks": [{"risk": "Unlimited Liability", "severity": "high", "reason": "No cap", "citation": "Sec 4"}],
            "medium_risks": [],
            "low_risks": [{"risk": "Notice period", "severity": "low", "reason": "30 days", "citation": "Sec 8"}],
            "assumptions": ["Standard commercial terms"]
        }
        mock_router.generate_json = AsyncMock(return_value=expected_risks)

        service = RiskService(db, router=mock_router)
        service.document_repo.get_by_id = MagicMock(return_value=Document(
            id="doc1", user_id="u1", content_hash="hash123", filename="test.pdf"
        ))
        service.snapshot_repo.get_snapshot = MagicMock(return_value=None)
        service.snapshot_repo.create_snapshot = MagicMock()
        service.chunk_repo.get_chunks = MagicMock(return_value=[
            Chunk(id="c1", document_id="doc1", page=1, content="Liability shall be uncapped."),
        ])
        service.metrics_repo.increment = MagicMock()

        result = await service.analyze_risks(document_id="doc1", user_id="u1")

        assert result == expected_risks
        mock_router.generate_json.assert_awaited_once()
        call_args, call_kwargs = mock_router.generate_json.call_args
        assert call_kwargs.get("task") == "risk_analysis"
        assert call_kwargs.get("user_id") == "u1"
        assert "Liability shall be uncapped." in call_args[0]
        service.snapshot_repo.create_snapshot.assert_called_once()
        service.metrics_repo.increment.assert_called_with("cache_miss", user_id="u1")

    asyncio.run(_run())


def test_risk_service_uses_cache_on_hit():
    async def _run():
        db = MagicMock()
        mock_router = MagicMock(spec=LLMRouter)
        cached_risks = {
            "high_risks": [],
            "medium_risks": [{"risk": "Cached Risk", "severity": "medium", "reason": "Cached", "citation": "None"}],
            "low_risks": [],
            "assumptions": []
        }

        service = RiskService(db, router=mock_router)
        service.document_repo.get_by_id = MagicMock(return_value=Document(
            id="doc1", user_id="u1", content_hash="hash123", filename="test.pdf"
        ))
        service.snapshot_repo.get_snapshot = MagicMock(return_value=AnalysisSnapshot(
            document_id="doc1", document_hash="hash123", analysis_type="risks",
            result_json=json.dumps(cached_risks), user_id="u1"
        ))
        service.metrics_repo.increment = MagicMock()

        result = await service.analyze_risks(document_id="doc1", user_id="u1")

        assert result == cached_risks
        mock_router.generate_json.assert_not_called()
        service.metrics_repo.increment.assert_called_with("cache_hit", user_id="u1")

    asyncio.run(_run())


def test_risk_service_falls_back_on_quota_exceeded():
    async def _run():
        db = MagicMock()
        mock_router = MagicMock(spec=LLMRouter)
        mock_router.generate_json = AsyncMock(side_effect=QuotaExceededException("Quota exhausted"))

        service = RiskService(db, router=mock_router)
        service.document_repo.get_by_id = MagicMock(return_value=Document(
            id="doc1", user_id="u1", content_hash="hash123", filename="test.pdf"
        ))
        service.snapshot_repo.get_snapshot = MagicMock(return_value=None)
        service.snapshot_repo.create_snapshot = MagicMock()
        service.chunk_repo.get_chunks = MagicMock(return_value=[
            Chunk(id="c1", document_id="doc1", page=1, content="There is a heavy liability and punitive damages clause."),
        ])
        service.metrics_repo.increment = MagicMock()

        result = await service.analyze_risks(document_id="doc1", user_id="u1")

        # Offline heuristic should have picked up "liability" and "punitive damages"
        medium_risk_names = [r["risk"] for r in result["medium_risks"]]
        assert "Liability Clause Present" in medium_risk_names
        assert "Punitive Damages Mentioned" in medium_risk_names
        assert "AI quota exhausted" in result["assumptions"][0]
        service.snapshot_repo.create_snapshot.assert_called_once()

    asyncio.run(_run())


def test_risk_service_document_not_found():
    async def _run():
        db = MagicMock()
        mock_router = MagicMock(spec=LLMRouter)
        service = RiskService(db, router=mock_router)
        service.document_repo.get_by_id = MagicMock(return_value=None)

        with pytest.raises(ValueError, match="Document not found"):
            await service.analyze_risks(document_id="nonexistent", user_id="u1")

    asyncio.run(_run())
